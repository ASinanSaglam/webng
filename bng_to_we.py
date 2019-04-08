import argparse, yaml, os, shutil, sys
import subprocess as sbpc

# TODO: Expose more functionality to the options file
# especially some of them can be optionally exposed
class BNGL_TO_WE:
    def __init__(self):
        '''
        take arguments from the commmand line and then parse the
        options file given
        '''
        # read the options file
        self._parse_args()
        self.opts = self._load_yaml(self.args.opts)
        self._parse_opts(self.opts)
        self.copy_run_net = self.args.copy_run_net

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary")
        return val

    def _parse_opts(self, opts_dict):
        '''
        Parses the loaded YAML dictionary and updates the 
        class attributes appropriately
        '''
        # Set the main directory we are in 
        self.main_dir = os.getcwd()
        # we need to find WESTPA and BNG
        path_options = self._getd(self.opts, "path_options")
        self.WESTPA_path = self._getd(path_options, "WESTPA_path")
        self.bng_path = self._getd(path_options, "bng_path")
        self.bngl_file = self._getd(path_options, "bngl_file")
        self.fname = self._getd(path_options, "sim_name", default="WE_BNG_sim")
        # Define where the BNG2.pl script is 
        self.bngpl = os.path.join(self.bng_path, "BNG2.pl")
        # Sampling options 
        sampling_options = self._getd(self.opts, "sampling_options")
        self.tau = self._getd(sampling_options, "tau")
        self.max_iter = self._getd(sampling_options, "max_iter", default=100)
        self.dims = self._getd(sampling_options, "dimensions")
        self.plen= self._getd(sampling_options, "pcoord_length")
        # binning options
        binning_options = self._getd(self.opts, "binning_options")
        # At the moment I'm assuming a safe set of defaults?
        self.traj_per_bin = self._getd(binning_options, "traj_per_bin", default=10)
        self.block_size = self._getd(binning_options, "block_size", default=10)
        self.center_freq = self._getd(binning_options, "center_freq", default=1)
        self.max_centers = self._getd(binning_options, "max_centers", default=300)

    def _parse_args(self):
        '''
        parse arguments passed in the command line
        '''
        parser = argparse.ArgumentParser()

        # Data input options
        parser.add_argument('--options', '-opts',
                            dest='opts',
                            required=True,
                            help='Options YAML file, required',
                            type=str)

        parser.add_argument('--copy-run-network',
                            dest='copy_run_net',
                            action='store_true',
                            help='If set, copies over the run_network binary')

        self.args = parser.parse_args()

    def _load_yaml(self, yfile):
        '''
        internal function that opens a file and loads it in using 
        yaml library
        '''
        f = open(yfile, "r")
        y = yaml.load(f)
        f.close()
        return y

    def _write_runsh(self):
        '''
        write the run.sh file for WESTPA simulations
        '''
        # TODO: Add submission scripts for varied clusters
        # TODO: Add a hook to write any submission scripts?
        lines = [
          '#!/bin/bash\n',
          'source env.sh\n',
          '$WEST_ROOT/bin/w_run --work-manager processes "$@"\n'\
          ]

        f = open("run.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("run.sh", 0764)

    def _write_envsh(self):
        '''
        environment script that uses westpa.sh to setup the environment
        '''
        if self.WESTPA_path is None:
            sys.exit("WESTPA path is not specified")

        lines = [
            '#!/bin/sh\n',
            'source {}/westpa.sh\n'.format(self.WESTPA_path),
            'export WEST_SIM_ROOT="$PWD"\n',
            'export SIM_NAME=$(basename $WEST_SIM_ROOT)\n'
            ]

        if self.copy_run_net:
            lines.append('export RunNet="$WEST_SIM_ROOT/bngl_conf/run_network"\n')
        else:
            lines.append('export RunNet="{}/bin/run_network"\n'.format(self.bng_path))

        f = open("env.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("env.sh", 0764)

    def _write_auxfuncs(self):
        '''
        auxilliary function, by default we want to avoid the first point because that's
        time in BNG output
        '''
        lines = [
              '#!/usr/bin/env python\n',
              'import numpy\n',
              'def pcoord_loader(fieldname, coord_filename, segment, single_point=False):\n',
              '    pcoord    = numpy.loadtxt(coord_filename, dtype = numpy.float32)\n',
              '    if not single_point:\n',
              '        segment.pcoord = pcoord[:,1:]\n',
              '    else:\n',
              '        segment.pcoord = pcoord[1:]'
              ]

        f = open("aux_functions.py", "w")
        f.writelines(lines)
        f.close()

    def _write_bstatestxt(self):
        '''
        a simple version of the basis states file, 
        here you can define multiple starting points if you wanted
        '''
        lines = [
            '0 1 0.net'
          ]

        f = open("bstates/bstates.txt", "w")
        f.writelines(lines)
        f.close()

    def _write_getpcoord(self):
        '''
        the pcoord acquiring script for the inital center
        '''
        lines = [
            '#!/bin/bash\n',
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            '  set -x\n',
            '  env | sort\n',
            'fi\n',
            'cd $WEST_SIM_ROOT\n',
            'cat bngl_conf/init.gdat > $WEST_PCOORD_RETURN\n',
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            '  head -v $WEST_PCOORD_RETURN\n',
            'fi\n'
            ]

        f = open("westpa_scripts/get_pcoord.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("westpa_scripts/get_pcoord.sh", 0764)

    def _write_postiter(self):
        '''
        a basic post-iteration script that deletes iterations that are 
        older than 3 iterations 
        '''
        lines = [
            '#!/bin/bash\n',
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            '    set -x\n',
            '    env | sort\n',
            'fi\n',
            'cd $WEST_SIM_ROOT || exit 1\n',
            'if [[ $WEST_CURRENT_ITER -gt 3 ]];then\n',
            '  PREV_ITER=$(printf "%06d" $((WEST_CURRENT_ITER-3)))\n',
            '  rm -rf ${WEST_SIM_ROOT}/traj_segs/${PREV_ITER}\n',
            '  rm -f  seg_logs/${PREV_ITER}-*.log\n',
            'fi\n'
            ]

        f = open("westpa_scripts/post_iter.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("westpa_scripts/post_iter.sh", 0764)

    def _write_initsh(self):
        '''
        WESTPA initialization script
        '''
        lines = [
            '#!/bin/bash\n',
            'source env.sh\n',
            'rm -rf traj_segs seg_logs istates west.h5 \n',
            'mkdir   seg_logs traj_segs \n',
            'cp $WEST_SIM_ROOT/bngl_conf/init.net bstates/0.net\n',
            'BSTATE_ARGS="--bstate-file bstates/bstates.txt"\n',
            '$WEST_ROOT/bin/w_init $BSTATE_ARGS --segs-per-state {} --work-manager=threads "$@"'.format(self.traj_per_bin),
            ]

        f = open("init.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("init.sh", 0764)

    def _write_systempy(self):
        '''
        the system.py where the bin mapper is defined, most binning options 
        go here
        '''
        lines = [
            'from __future__ import division, print_function; __metaclass__ = type\n',
            'import numpy as np\n',
            'import west\n',
            'from west import WESTSystem\n',
            'from westpa.binning import VoronoiBinMapper\n',
            'from scipy.spatial.distance import cdist\n',
            'import logging\n',
            'log = logging.getLogger(__name__)\n',
            'log.debug(\'loading module %r\' % __name__)\n',
            'def dfunc(p, centers):\n',
            '    ds = cdist(np.array([p]),centers)\n',
            '    return np.array(ds[0], dtype=p.dtype)\n',
            'class System(WESTSystem):\n',
            '    def initialize(self):\n',
            '        self.pcoord_ndim = {}\n'.format(self.dims),
            '        self.pcoord_len = {}\n'.format(self.plen+1),
            '        self.pcoord_dtype = np.float32\n',
            '        self.nbins = 1\n',
            '\n',
            '        centers = np.zeros((self.nbins,self.pcoord_ndim),dtype=self.pcoord_dtype)\n',
            '        # Using the values from the inital point\n',
            '        i = np.loadtxt(\'bngl_conf/init.gdat\')\n',
            '        centers[0] = i[1:]\n',
            '\n',
            '        self.bin_mapper = VoronoiBinMapper(dfunc, centers)\n',
            '        self.bin_target_counts = np.empty((self.bin_mapper.nbins,), np.int)\n',
            '        self.bin_target_counts[...] = {}\n'.format(self.traj_per_bin)
            ]

        f = open("system.py", "w")
        f.writelines(lines)
        f.close()

    def _write_westcfg(self):
        '''
        the WESTPA configuration file, another YAML file
        '''
        # TODO: Expose max wallclock time?
        lines = [
            '# vi: set filetype=yaml :\n',
            '---\n',
            'west: \n',
            '  system:\n',
            '    driver: system.System\n',
            '    module_path: $WEST_SIM_ROOT\n',
            '  propagation:\n',
            '    max_total_iterations: {}\n'.format(self.max_iter),
            '    max_run_wallclock:    72:00:00\n',
            '    propagator:           executable\n',
            '    gen_istates:          false\n',
            '    block_size:           {}\n'.format(self.block_size),
            '  data:\n',
            '    west_data_file: west.h5\n',
            '    datasets:\n',
            '      - name:        pcoord\n',
            '        scaleoffset: 4\n',
            '    data_refs:\n',
            '      segment:       $WEST_SIM_ROOT/traj_segs/{segment.n_iter:06d}/{segment.seg_id:06d}\n',
            '      basis_state:   $WEST_SIM_ROOT/bstates/{basis_state.auxref}\n',
            '      initial_state: $WEST_SIM_ROOT/istates/{initial_state.iter_created}/{initial_state.state_id}.rst\n',
            '  plugins:\n',
            '    - plugin: westext.adaptvoronoi.AdaptiveVoronoiDriver\n',
            '      av_enabled: true\n',
            '      dfunc_method: system.dfunc\n',
            '      walk_count: {}\n'.format(self.traj_per_bin),
            '      max_centers: {}\n'.format(self.max_centers),
            '      center_freq: {}\n'.format(self.center_freq),
            '  executable:\n',
            '    environ:\n',
            '      PROPAGATION_DEBUG: 1\n',
            '    datasets:\n',
            '      - name:    pcoord\n',
            '        loader:  aux_functions.pcoord_loader\n',
            '        enabled: true\n',
            '    propagator:\n',
            '      executable: $WEST_SIM_ROOT/westpa_scripts/runseg.sh\n',
            '      stdout:     $WEST_SIM_ROOT/seg_logs/{segment.n_iter:06d}-{segment.seg_id:06d}.log\n',
            '      stderr:     stdout\n',
            '      stdin:      null\n',
            '      cwd:        null\n',
            '      environ:\n',
            '        SEG_DEBUG: 1\n',
            '    get_pcoord:\n',
            '      executable: $WEST_SIM_ROOT/westpa_scripts/get_pcoord.sh\n',
            '      stdout:     /dev/null \n',
            '      stderr:     stdout\n',
            '    gen_istate:\n',
            '      executable: $WEST_SIM_ROOT/westpa_scripts/gen_istate.sh\n',
            '      stdout:     /dev/null \n',
            '      stderr:     stdout\n',
            '    post_iteration:\n',
            '      enabled:    true\n',
            '      executable: $WEST_SIM_ROOT/westpa_scripts/post_iter.sh\n',
            '      stderr:     stdout\n',
            '    pre_iteration:\n',
            '      enabled:    false\n',
            '      executable: $WEST_SIM_ROOT/westpa_scripts/pre_iter.sh\n',
            '      stderr:     stdout\n'
            ]
            
        f = open("west.cfg", "w")
        f.writelines(lines)
        f.close()

    def _write_runsegsh(self):
        '''
        the most important script that extends an individual segment, 
        this is where tau is defined
        '''

        step_len = self.tau/self.plen
        step_no = self.plen

        lines = [
            '#!/bin/bash\n',
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            '  set -x\n',
            '  env | sort\n',
            'fi\n',
            'if [[ -n $SCRATCH ]];then\n',
            '  mkdir -pv $WEST_CURRENT_SEG_DATA_REF\n',
            '  mkdir -pv ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n',
            '  cd ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n',
            'else\n',
            '  mkdir -pv $WEST_CURRENT_SEG_DATA_REF\n',
            '  cd $WEST_CURRENT_SEG_DATA_REF\n',
            'fi\n',
            'if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then\n',
            '  if [[ -n $SCRATCH ]];then\n',
            '    cp $WEST_PARENT_DATA_REF/seg_end.net ./parent.net\n',
            '    cp $WEST_PARENT_DATA_REF/seg.gdat ./parent.gdat\n',
            '  else\n',
            '    ln -sv $WEST_PARENT_DATA_REF/seg_end.net ./parent.net\n',
            '    ln -sv $WEST_PARENT_DATA_REF/seg.gdat ./parent.gdat\n',
            '  fi\n',
            '  $RunNet -o ./seg -p ssa -h $WEST_RAND16 --cdat 0 --fdat 0 -x -e -g ./parent.net ./parent.net {} {}\n'.format(step_len, step_no),
            '  tail -n 1 parent.gdat > $WEST_PCOORD_RETURN\n',
            '  cat seg.gdat >> $WEST_PCOORD_RETURN\n',
            'elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then\n',
            '  if [[ -n $SCRATCH ]];then\n',
            '    cp $WEST_PARENT_DATA_REF ./parent.net\n',
            '  else\n',
            '    ln -sv $WEST_PARENT_DATA_REF ./parent.net\n',
            '  fi\n',
            '  $RunNet -o ./seg -p ssa -h $WEST_RAND16 --cdat 0 --fdat 0 -e -g ./parent.net ./parent.net {} {}\n'.format(step_len, step_no),
            '  cat seg.gdat > $WEST_PCOORD_RETURN\n',
            'fi\n',
            '\n',
            'if [[ -n $SCRATCH ]];then\n',
            '  cp ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF/seg_end.net $WEST_CURRENT_SEG_DATA_REF/.\n',
            '  rm -rf ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n',
            'fi\n'
            ]

        f = open("westpa_scripts/runseg.sh", "w")
        f.writelines(lines)
        f.close()
        os.chmod("westpa_scripts/runseg.sh", 0764)

    def write_dynamic_files(self):
        '''
        these files change depending on the given options, in particular
        sampling and binning options
        '''
        self._write_initsh()
        self._write_systempy()
        self._write_westcfg()
        self._write_runsegsh()

    def write_static_files(self):
        '''
        these files are always (mostly) the same regardless of given options 
        '''
        # everything here assumes we are in the right folder
        self._write_runsh()
        self._write_envsh()
        self._write_auxfuncs()
        self._write_bstatestxt()
        self._write_getpcoord()
        self._write_postiter()

    def make_sim_folders(self):
        '''
        make folders WESTPA needs 
        '''
        self.sim_dir = self.fname
        os.makedirs(self.fname)
        os.chdir(self.fname)
        os.makedirs("bngl_conf")
        os.makedirs("bstates")
        os.makedirs("westpa_scripts")


    def copy_run_network(self):
        '''
        this copies the run_network binary with correct permissions to where 
        WESTPA will expect to find it.
        '''
        # Assumes path is absolute path and not relative
        shutil.copyfile(os.path.join(self.bng_path, "bin/run_network"), "bngl_conf/run_network")
        os.chmod("bngl_conf/run_network",0764)

    def run_BNGL_on_file(self):
        '''
        this function runs the BNG2.pl on the given bngl file
        to get a) .net file for the starting point and b) .gdat file
        to get the first voronoi center for the simulation
        '''
        # IMPORTANT! 
        # This assumes that the bngl file doesn't have any directives at the end! 
        # we have a bngl file
        os.chdir("bngl_conf")
        # Make specific BNGL files for a) generating network and then 
        # b) getting a starting  gdat file
        shutil.copyfile(self.bngl_file, "init.bngl")
        shutil.copyfile(self.bngl_file, "for_network.bngl")
        f = open("for_network.bngl", "a")
        # Adding directives to generate the files we want
        f.write('generate_network({overwrite=>1});\n')
        f.close()
        shutil.copyfile(self.bngl_file, "for_gdat.bngl")
        f = open("for_gdat.bngl", "a")
        # Adding directives to generate the files we want
        f.write('generate_network({overwrite=>1});\n')
        f.write('simulate({method=>"ssa",t_end=>2,n_steps=>1});\n')
        f.close()
        # run BNG2.pl on things to get the files we need
        proc = sbpc.Popen([self.bngpl, "for_network.bngl"])
        proc.wait()
        assert proc.returncode == 0, "call to BNG2.pl failed, make sure it's in your PATH"
        # copy our network back
        shutil.copyfile("for_network.net", "init.net")
        os.remove("for_network.bngl")
        os.remove("for_network.net")
        # run on gdat 
        proc = sbpc.Popen([self.bngpl, "for_gdat.bngl"])
        proc.wait()
        assert proc.returncode == 0, "call to BNG2.pl failed, make sure it's in your PATH"
        # edit the gdat file to get rid of the last line
        f = open("for_gdat.gdat", "r")
        l = f.readlines()
        f.close()
        # Now write the first two lines to init.gdat
        f = open("init.gdat", "w")
        f.writelines(l[:2])
        f.close()
        os.remove("for_gdat.bngl")
        os.remove("for_gdat.net")
        os.remove("for_gdat.cdat")
        os.remove("for_gdat.gdat")
        # return to main simulation folder
        os.chdir(os.path.join(self.main_dir, self.sim_dir))

    def run(self):
        '''
        runs the class functions in appropriate order to 
        make the WESTPA simultion folder
        '''
        self.make_sim_folders()
        if self.copy_run_net: 
            self.copy_run_network()
        self.write_static_files()
        self.run_BNGL_on_file()
        self.write_dynamic_files()
        return

if __name__ == "__main__":
    btw = BNGL_TO_WE()
    btw.run()
