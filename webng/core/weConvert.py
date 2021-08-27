import yaml, os, shutil, sys, bionetgen
import numpy as np
import subprocess as sbpc

# TODO: Expose more functionality to the options file
# especially some of them can be optionally exposed
class weConvert:
    """
    This is the class that will be used by the command line tool when it's
    called with the subcommand `webng setup`.

    The class needs the dictionary from configuration YAML file for initalization
    and will use the options there to setup the WESTPA simulation folder.

    The `run` method will use the parsed options and make the WESTPA simulation folder
    using the templates it contains. TODO: Use jinja for templating instead.
    """

    def __init__(self, args):
        """
        take arguments from cement app and get ready to write
        """
        self.opts = self._load_yaml(args.opts)
        self._parse_opts(self.opts)
        # TODO: make this optional somewhere else
        self.copy_run_net = True

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary".format(key))
        return val

    def _parse_opts(self, opts_dict):
        """
        Parses the loaded YAML dictionary and updates the
        class attributes appropriately
        """
        # Set the main directory we are in
        self.main_dir = os.getcwd()
        # Propagator options
        propagator_options = self._getd(self.opts, "propagator_options")
        self.propagator_type = self._getd(
            propagator_options, "propagator_type", default="executable"
        )
        if self.propagator_type == "libRoadRunner":
            self.pcoord_list = self._getd(propagator_options, "pcoords")
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
        self.plen = self._getd(sampling_options, "pcoord_length")
        # binning options
        binning_options = self._getd(self.opts, "binning_options")
        # At the moment I'm assuming a safe set of defaults?
        self.traj_per_bin = self._getd(binning_options, "traj_per_bin", default=10)
        self.block_size = self._getd(binning_options, "block_size", default=10)
        self.center_freq = self._getd(binning_options, "center_freq", default=1)
        self.max_centers = self._getd(binning_options, "max_centers", default=300)

    def _load_yaml(self, yfile):
        """
        internal function that opens a file and loads it in using
        yaml library
        """
        with open(yfile, "r") as f:
            y = yaml.load(f)
        return y

    def _write_librrPropagator(self):
        lines = [
            "from __future__ import division, print_function; __metaclass__ = type\n",
            "import numpy as np\n",
            "import westpa, copy, time, random\n",
            "from westpa.core.propagators import WESTPropagator\n",
            "import roadrunner as librr\n",
            "import logging\n",
            "log = logging.getLogger(__name__)\n",
            "log.debug('loading module %r' % __name__)\n",
            "# We want to write the librrPropagator here\n",
            "class librrPropagator(WESTPropagator):\n",
            "    def __init__(self, rc=None):\n",
            "        super(librrPropagator,self).__init__(rc)\n",
            "        # Get the rc file stuff\n",
            "        config = self.rc.config\n",
            "        for key in [('west','librr','init','model_file'),\n"
            "                    ('west','librr','init','init_time_step'),\n",
            "                    ('west','librr','init','final_time_step'),\n",
            "                    ('west','librr','init','num_time_step'),\n",
            "                    ('west','librr','data','pcoords')]:\n",
            "            config.require(key)\n",
            "        self.runner_config = {}\n",
            "        self.runner_config['model_file'] = config['west','librr','init','model_file']\n",
            "        self.runner_config['init_ts'] = config['west','librr','init','init_time_step']\n",
            "        self.runner_config['final_ts'] = config['west','librr','init','final_time_step']\n",
            "        self.runner_config['num_ts'] = config['west','librr','init','num_time_step']\n",
            "        self.runner_config['pcoord_keys'] = config['west','librr','data','pcoords']\n",
            "        # Initialize the libRR propagator using the init file\n",
            "        # Note: We COULD use a string, meaning we can save that to the \n",
            "        # h5file and just pull the string out? I should look into this\n",
            "        self.runner = librr.RoadRunner(self.runner_config['model_file'])\n",
            '        self.runner.setIntegrator("gillespie")\n',
            "        self.runner.setIntegratorSetting('gillespie', 'variable_step_size', False)\n",
            "        self.runner.setIntegratorSetting('gillespie', 'nonnegative', True)\n",
            "        self.initial_pcoord = self.get_initial_pcoords()\n",
            "        self.full_state_keys = self.get_full_state_keys()\n",
            "        # setting time course so our result is just pcoord result\n",
            "        self.runner.timeCourseSelections = self.runner_config['pcoord_keys']\n"
            "    # Overwriting inhereted methods\n",
            "    def get_pcoord(self, state):\n",
            "        state.pcoord = copy.copy(self.initial_pcoord)\n",
            "        return\n",
            "    def gen_istate(self, basis_state, initial_state):\n",
            "        return initial_state\n",
            "    # Rest is original class methods, except for propagate ofc\n",
            "    def get_initial_pcoords(self):\n",
            "        return [self.runner[x] for x in self.runner_config['pcoord_keys']]\n",
            "    def get_full_state_keys(self):\n",
            "        # TODO: Is this the best way? More importantly, is this the correct way?\n",
            "        # since RR timecourses are just concs and not the values themselves,\n",
            "        # we probably have to find a way to pull everything that are not constants\n",
            "        fs = self.runner.getFloatingSpeciesAmountsNamedArray().colnames\n",
            '        concs = ["["+x+"]" for x in fs]\n',
            "        return fs+concs\n",
            "    def get_final_state(self):\n",
            "        # gets the final state info in full to be used by set_concs later\n",
            "        return [self.runner[x] for x in self.full_state_keys]\n",
            "    def set_runner_state(self, state):\n",
            "        for ival, val in enumerate(state):\n",
            "            self.runner.setValue(self.full_state_keys[ival], val)\n",
            "    def propagate(self, segments):\n",
            "        piter = segments[0].n_iter-1\n",
            "        # Set some init states for segments\n",
            "        for iseg, segment in enumerate(segments):\n",
            "            # print(piter,segment.parent_state)\n",
            "            starttime = time.time()\n",
            "            seed = random.randint(0,2**14)\n",
            "            # Make sure we are reset so we can set the init state by hand\n",
            "            self.runner.resetAll()\n",
            "            # Set a new seed\n",
            "            self.runner.setIntegratorSetting('gillespie', 'seed', seed)\n",
            "            # Deal with init state here\n",
            "            # if segment.initpoint_type == Segment.SEG_INITPOINT_CONTINUES:\n",
            "            #     pass\n",
            "            # elif segment.initpoint_type == Segment.SEG_INITPOINT_NEWTRAJ:\n",
            "            #     pass\n",
            "            if piter > 0:\n",
            "                self.set_runner_state(segment.data['restart_state'])\n",
            "            # now we simulate using given parameters\n",
            "            result = self.runner.simulate(self.runner_config['init_ts'], \n",
            "                                          self.runner_config['final_ts'],\n",
            "                                          self.runner_config['num_ts'])\n",
            "            # We need to store the current state of everything in the system\n",
            "            # so we can set it \n",
            "            segment.data['final_state'] = self.get_final_state()\n",
            "            segment.data['seed'] = seed\n",
            "            # Get segment pcoords\n",
            "            segment.pcoord = result\n",
            "            # TODO: calc cputime somehow\n",
            "            segment.walltime = time.time() - starttime\n",
            "            segment.cputime = 0\n",
            "            segment.status = segment.SEG_STATUS_COMPLETE\n",
            "        return segments\n",
        ]
        with open("libRR_propagator.py", "w") as f:
            f.writelines(lines)

    def _write_restartDriver(self):
        lines = [
            "from __future__ import division; __metaclass__ = type",
            "import logging",
            "log = logging.getLogger(__name__)",
            "class RestartDriver(object):",
            "    def __init__(self, sim_manager, plugin_config):",
            "        super(RestartDriver, self).__init__()",
            "        if not sim_manager.work_manager.is_master:",
            "                return",
            "        self.sim_manager = sim_manager",
            "        self.data_manager = sim_manager.data_manager",
            "        self.system = sim_manager.system",
            "        self.priority = plugin_config.get('priority', 0)",
            "        # Register callback",
            "        sim_manager.register_callback(sim_manager.pre_propagation, self.pre_propagation, self.priority)",
            "    def pre_propagation(self):",
            "        segments = self.sim_manager.incomplete_segments.values()",
            "        n_iter = self.sim_manager.n_iter",
            "        if n_iter == 1:",
            "            return",
            "        parent_iter_group = self.data_manager.get_iter_group(n_iter - 1)",
            "        # Get parent ids for segments",
            "        parent_ids = [seg.parent_id for seg in segments]",
            "        # Get a list of unique parent ids and collect restart data for each",
            "        unique_parent_ids = set(parent_ids)",
            "        restart_data = {segid: {} for segid in unique_parent_ids}",
            "        for dsname in ['final_state', 'seed']:",
            "            try:",
            "                dsinfo = self.data_manager.dataset_options[dsname]",
            "            except KeyError:",
            "                raise KeyError('Data set {} not found'.format(dsname))",
            "            ds = parent_iter_group[dsinfo['h5path']]",
            "            for seg_id in unique_parent_ids:",
            "                restart_data[seg_id][dsname] = ds[seg_id]",
            "        for segment in segments:",
            "            segment.data['restart_state'] = restart_data[segment.parent_id]['final_state']",
        ]
        full_text = "\n".join(lines)
        with open("restart_plugin.py", "w") as f:
            f.write(full_text)

    def _write_runsh(self):
        """
        write the run.sh file for WESTPA simulations
        """
        # TODO: Add submission scripts for varied clusters
        # TODO: Add a hook to write any submission scripts?
        lines = ["#!/bin/bash\n", 'w_run --work-manager processes "$@"\n']

        with open("run.sh", "w") as f:
            f.writelines(lines)
        os.chmod("run.sh", 0o764)

    def _write_envsh(self):
        """
        environment script that uses westpa.sh to setup the environment
        """
        if self.WESTPA_path is None:
            sys.exit("WESTPA path is not specified")

        lines = [
            "#!/bin/sh\n",
            'export WEST_SIM_ROOT="$PWD"\n',
            "export SIM_NAME=$(basename $WEST_SIM_ROOT)\n",
        ]

        if self.copy_run_net:
            lines.append('export RunNet="$WEST_SIM_ROOT/bngl_conf/run_network"\n')
        else:
            lines.append('export RunNet="{}/bin/run_network"\n'.format(self.bng_path))

        with open("env.sh", "w") as f:
            f.writelines(lines)
        os.chmod("env.sh", 0o764)

    def _write_auxfuncs(self):
        """
        auxilliary function, by default we want to avoid the first point because that's
        time in BNG output
        """
        lines = [
            "#!/usr/bin/env python\n",
            "import numpy\n",
            "def pcoord_loader(fieldname, coord_filename, segment, single_point=False):\n",
            "    pcoord    = numpy.loadtxt(coord_filename, dtype = numpy.float32)\n",
            "    if not single_point:\n",
            "        segment.pcoord = pcoord[:,1:]\n",
            "    else:\n",
            "        segment.pcoord = pcoord[1:]",
        ]

        f = open("aux_functions.py", "w")
        f.writelines(lines)
        f.close()

    def _write_bstatestxt(self):
        """
        a simple version of the basis states file,
        here you can define multiple starting points if you wanted
        """
        lines = ["0 1 0.net"]

        f = open("bstates/bstates.txt", "w")
        f.writelines(lines)
        f.close()

    def _write_getpcoord(self):
        """
        the pcoord acquiring script for the inital center
        """
        lines = [
            "#!/bin/bash\n",
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            "  set -x\n",
            "  env | sort\n",
            "fi\n",
            "cd $WEST_SIM_ROOT\n",
            "cat bngl_conf/init.gdat > $WEST_PCOORD_RETURN\n",
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            "  head -v $WEST_PCOORD_RETURN\n",
            "fi\n",
        ]

        with open("westpa_scripts/get_pcoord.sh", "w") as f:
            f.writelines(lines)
        os.chmod("westpa_scripts/get_pcoord.sh", 0o764)

    def _write_postiter(self):
        """
        a basic post-iteration script that deletes iterations that are
        older than 3 iterations
        """
        lines = [
            "#!/bin/bash\n",
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            "    set -x\n",
            "    env | sort\n",
            "fi\n",
            "cd $WEST_SIM_ROOT || exit 1\n",
            "if [[ $WEST_CURRENT_ITER -gt 3 ]];then\n",
            '  PREV_ITER=$(printf "%06d" $((WEST_CURRENT_ITER-3)))\n',
            "  rm -rf ${WEST_SIM_ROOT}/traj_segs/${PREV_ITER}\n",
            "  rm -f  seg_logs/${PREV_ITER}-*.log\n",
            "fi\n",
        ]

        with open("westpa_scripts/post_iter.sh", "w") as f:
            f.writelines(lines)
        os.chmod("westpa_scripts/post_iter.sh", 0o764)

    def _write_initsh(self, traj=True):
        """
        WESTPA initialization script
        """
        if traj:
            lines = [
                "#!/bin/bash\n",
                "source env.sh\n",
                "rm -rf traj_segs seg_logs istates west.h5 \n",
                "mkdir   seg_logs traj_segs \n",
                "cp $WEST_SIM_ROOT/bngl_conf/init.net bstates/0.net\n",
                'BSTATE_ARGS="--bstate-file bstates/bstates.txt"\n',
                'w_init $BSTATE_ARGS --segs-per-state {} --work-manager=threads "$@"'.format(
                    self.traj_per_bin
                ),
            ]
        else:
            lines = [
                "#!/bin/bash\n",
                "source env.sh\n",
                "rm -rf istates west.h5\n",
                "cp $WEST_SIM_ROOT/bngl_conf/init.net bstates/0.net\n",
                'BSTATE_ARGS="--bstate-file bstates/bstates.txt"\n',
                'w_init $BSTATE_ARGS --segs-per-state {} --work-manager=threads "$@"'.format(
                    self.traj_per_bin
                ),
            ]

        with open("init.sh", "w") as f:
            f.writelines(lines)
        os.chmod("init.sh", 0o764)

    def _write_systempy(self):
        """
        the system.py where the bin mapper is defined, most binning options
        go here
        """
        lines = [
            "from __future__ import division, print_function; __metaclass__ = type\n",
            "import numpy as np\n",
            "import westpa\n",
            "from westpa import WESTSystem\n",
            "from westpa.core.binning import VoronoiBinMapper\n",
            "from scipy.spatial.distance import cdist\n",
            "import logging\n",
            "log = logging.getLogger(__name__)\n",
            "log.debug('loading module %r' % __name__)\n",
            "def dfunc(p, centers):\n",
            "    ds = cdist(np.array([p]),centers)\n",
            "    return np.array(ds[0], dtype=p.dtype)\n",
            "class System(WESTSystem):\n",
            "    def initialize(self):\n",
            "        self.pcoord_ndim = {}\n".format(self.dims),
            "        self.pcoord_len = {}\n".format(self.plen + 1),
            "        self.pcoord_dtype = np.float32\n",
            "        self.nbins = 1\n",
            "        centers = np.zeros((self.nbins,self.pcoord_ndim),dtype=self.pcoord_dtype)\n",
            "        # Using the values from the inital point\n",
            "        i = np.loadtxt('bngl_conf/init.gdat')\n",
            "        centers[0] = i[0,1:]\n",
            "        self.bin_mapper = VoronoiBinMapper(dfunc, centers)\n",
            "        self.bin_target_counts = np.empty((self.bin_mapper.nbins,), np.int)\n",
            "        self.bin_target_counts[...] = {}\n".format(self.traj_per_bin),
        ]

        f = open("system.py", "w")
        f.writelines(lines)
        f.close()

    def _write_westcfg(self):
        """
        the WESTPA configuration file, another YAML file
        """
        # TODO: Expose max wallclock time?
        if self.propagator_type == "executable":
            self._executable_westcfg()
        elif self.propagator_type == "libRoadRunner":
            self._libRR_westcfg()

    def _libRR_westcfg(self):
        step_len = self.tau / self.plen
        step_no = self.plen

        lines = [
            "# vi: set filetype=yaml :\n",
            "---\n",
            "west: \n",
            "  system:\n",
            "    driver: system.System\n",
            "    module_path: $WEST_SIM_ROOT\n",
            "  propagation:\n",
            "    max_total_iterations: {}\n".format(self.max_iter),
            "    max_run_wallclock:    72:00:00\n",
            "    propagator:           libRR_propagator.librrPropagator \n",
            "    gen_istates:          false\n",
            "    block_size:           {}\n".format(self.block_size),
            "  data:\n",
            "    west_data_file: west.h5\n",
            "    datasets:\n",
            "      - name:        pcoord\n",
            "        scaleoffset: 4\n",
            "      - name:        seed\n",
            "        scaleoffset: 4\n",
            "      - name:        final_state \n",
            "        scaleoffset: 4\n",
            "  plugins:\n",
            "    - plugin: westpa.westext.adaptvoronoi.AdaptiveVoronoiDriver\n",
            "      av_enabled: true\n",
            "      dfunc_method: system.dfunc\n",
            "      walk_count: {}\n".format(self.traj_per_bin),
            "      max_centers: {}\n".format(self.max_centers),
            "      center_freq: {}\n".format(self.center_freq),
            "    - plugin: restart_plugin.RestartDriver\n",
            "  librr:\n",
            "    init:\n",
            "      model_file: {} # Generate this\n".format(
                os.path.join(self.main_dir, self.fname, "bngl_conf", "init.xml")
            ),
            "      init_time_step: 0\n",
            "      final_time_step: {}\n".format(self.tau),
            "      num_time_step: {}\n".format(step_no + 1),
            "    data:\n",
            "      pcoords: {}\n".format(('["' + '","'.join(self.pcoord_list) + '"]')),
        ]  # TODO: Write pcoords
        with open("west.cfg", "w") as f:
            f.writelines(lines)

    def _executable_westcfg(self):
        lines = [
            "# vi: set filetype=yaml :\n",
            "---\n",
            "west: \n",
            "  system:\n",
            "    driver: system.System\n",
            "    module_path: $WEST_SIM_ROOT\n",
            "  propagation:\n",
            "    max_total_iterations: {}\n".format(self.max_iter),
            "    max_run_wallclock:    72:00:00\n",
            "    propagator:           executable\n",
            "    gen_istates:          false\n",
            "    block_size:           {}\n".format(self.block_size),
            "  data:\n",
            "    west_data_file: west.h5\n",
            "    datasets:\n",
            "      - name:        pcoord\n",
            "        scaleoffset: 4\n",
            "    data_refs:\n",
            "      segment:       $WEST_SIM_ROOT/traj_segs/{segment.n_iter:06d}/{segment.seg_id:06d}\n",
            "      basis_state:   $WEST_SIM_ROOT/bstates/{basis_state.auxref}\n",
            "      initial_state: $WEST_SIM_ROOT/istates/{initial_state.iter_created}/{initial_state.state_id}.rst\n",
            "  plugins:\n",
            "    - plugin: westext.adaptvoronoi.AdaptiveVoronoiDriver\n",
            "      av_enabled: true\n",
            "      dfunc_method: system.dfunc\n",
            "      walk_count: {}\n".format(self.traj_per_bin),
            "      max_centers: {}\n".format(self.max_centers),
            "      center_freq: {}\n".format(self.center_freq),
            "  executable:\n",
            "    environ:\n",
            "      PROPAGATION_DEBUG: 1\n",
            "    datasets:\n",
            "      - name:    pcoord\n",
            "        loader:  aux_functions.pcoord_loader\n",
            "        enabled: true\n",
            "    propagator:\n",
            "      executable: $WEST_SIM_ROOT/westpa_scripts/runseg.sh\n",
            "      stdout:     $WEST_SIM_ROOT/seg_logs/{segment.n_iter:06d}-{segment.seg_id:06d}.log\n",
            "      stderr:     stdout\n",
            "      stdin:      null\n",
            "      cwd:        null\n",
            "      environ:\n",
            "        SEG_DEBUG: 1\n",
            "    get_pcoord:\n",
            "      executable: $WEST_SIM_ROOT/westpa_scripts/get_pcoord.sh\n",
            "      stdout:     /dev/null \n",
            "      stderr:     stdout\n",
            "    gen_istate:\n",
            "      executable: $WEST_SIM_ROOT/westpa_scripts/gen_istate.sh\n",
            "      stdout:     /dev/null \n",
            "      stderr:     stdout\n",
            "    post_iteration:\n",
            "      enabled:    true\n",
            "      executable: $WEST_SIM_ROOT/westpa_scripts/post_iter.sh\n",
            "      stderr:     stdout\n",
            "    pre_iteration:\n",
            "      enabled:    false\n",
            "      executable: $WEST_SIM_ROOT/westpa_scripts/pre_iter.sh\n",
            "      stderr:     stdout\n",
        ]

        f = open("west.cfg", "w")
        f.writelines(lines)
        f.close()

    def _write_runsegsh(self):
        """
        the most important script that extends an individual segment,
        this is where tau is defined
        """

        step_len = self.tau / self.plen
        step_no = self.plen

        lines = [
            "#!/bin/bash\n",
            'if [ -n "$SEG_DEBUG" ] ; then\n',
            "  set -x\n",
            "  env | sort\n",
            "fi\n",
            "if [[ -n $SCRATCH ]];then\n",
            "  mkdir -pv $WEST_CURRENT_SEG_DATA_REF\n",
            "  mkdir -pv ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n",
            "  cd ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n",
            "else\n",
            "  mkdir -pv $WEST_CURRENT_SEG_DATA_REF\n",
            "  cd $WEST_CURRENT_SEG_DATA_REF\n",
            "fi\n",
            'if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then\n',
            "  if [[ -n $SCRATCH ]];then\n",
            "    cp $WEST_PARENT_DATA_REF/seg_end.net ./parent.net\n",
            "    cp $WEST_PARENT_DATA_REF/seg.gdat ./parent.gdat\n",
            "  else\n",
            "    ln -sv $WEST_PARENT_DATA_REF/seg_end.net ./parent.net\n",
            "    ln -sv $WEST_PARENT_DATA_REF/seg.gdat ./parent.gdat\n",
            "  fi\n",
            "  $RunNet -o ./seg -p ssa -h $WEST_RAND16 --cdat 0 --fdat 0 -x -e -g ./parent.net ./parent.net {} {}\n".format(
                step_len, step_no
            ),
            "  tail -n 1 parent.gdat > $WEST_PCOORD_RETURN\n",
            "  cat seg.gdat >> $WEST_PCOORD_RETURN\n",
            'elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then\n',
            "  if [[ -n $SCRATCH ]];then\n",
            "    cp $WEST_PARENT_DATA_REF ./parent.net\n",
            "  else\n",
            "    ln -sv $WEST_PARENT_DATA_REF ./parent.net\n",
            "  fi\n",
            "  $RunNet -o ./seg -p ssa -h $WEST_RAND16 --cdat 0 --fdat 0 -e -g ./parent.net ./parent.net {} {}\n".format(
                step_len, step_no
            ),
            "  cat seg.gdat > $WEST_PCOORD_RETURN\n",
            "fi\n",
            "if [[ -n $SCRATCH ]];then\n",
            "  cp ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF/seg_end.net $WEST_CURRENT_SEG_DATA_REF/.\n",
            "  rm -rf ${SCRATCH}/$WEST_CURRENT_SEG_DATA_REF\n",
            "fi\n",
        ]

        with open("westpa_scripts/runseg.sh", "w") as f:
            f.writelines(lines)
        os.chmod("westpa_scripts/runseg.sh", 0o764)

    def write_dynamic_files(self):
        """
        these files change depending on the given options, in particular
        sampling and binning options
        """
        self._write_systempy()
        self._write_westcfg()
        if self.propagator_type == "executable":
            self._write_runsegsh()
            self._write_initsh(traj=True)
        else:
            self._write_initsh(traj=False)

    def write_static_files(self):
        """
        these files are always (mostly) the same regardless of given options
        """
        # everything here assumes we are in the right folder
        self._write_envsh()
        self._write_bstatestxt()
        self._write_auxfuncs()
        self._write_runsh()
        if self.propagator_type == "executable":
            self._write_getpcoord()
            self._write_postiter()
        elif self.propagator_type == "libRoadRunner":
            self._write_restartDriver()
            self._write_librrPropagator()

    def make_sim_folders(self):
        """
        make folders WESTPA needs
        """
        self.sim_dir = self.fname
        try:
            os.makedirs(self.fname)
        except FileExistsError as e:
            # TODO: make an overwrite option
            print(f"The folder {self.fname} you are trying to create already exists")
            print(e)
        os.chdir(self.fname)
        os.makedirs("bngl_conf")
        os.makedirs("bstates")
        if self.propagator_type == "executable":
            os.makedirs("westpa_scripts")

    def copy_run_network(self):
        """
        this copies the run_network binary with correct permissions to where
        WESTPA will expect to find it.
        """
        # Assumes path is absolute path and not relative
        shutil.copyfile(
            os.path.join(self.bng_path, "bin/run_network"), "bngl_conf/run_network"
        )
        os.chmod("bngl_conf/run_network", 0o764)

    def run_BNGL_on_file(self):
        """
        this function runs the BNG2.pl on the given bngl file
        to get a) .net file for the starting point and b) .gdat file
        to get the first voronoi center for the simulation
        """
        if self.propagator_type == "executable":
            self._executable_BNGL_on_file()
        elif self.propagator_type == "libRoadRunner":
            self._libRR_BNGL_on_file()

    def _libRR_BNGL_on_file(self):
        # We still need this stuff
        model = self._executable_BNGL_on_file()
        # But we also need to generate the XML file
        # get in the conf folder
        os.chdir("bngl_conf")
        # make a copy that we will use to generate the XML
        sim = model.setup_simulator()
        sbml_str = sim.getCurrentSBML()
        with open("init.xml", "w") as f:
            f.write(str(sbml_str))
        os.chdir(os.path.join(self.main_dir, self.sim_dir))

    def _executable_BNGL_on_file(self):
        # IMPORTANT!
        # This assumes that the bngl file doesn't have any directives at the end!
        # we have a bngl file
        os.chdir("bngl_conf")
        # Make specific BNGL files for a) generating network and then
        # b) getting a starting  gdat file
        model = bionetgen.bngmodel(self.bngl_file)
        model.add_action("generate_network", action_args=[("overwrite", 1)])
        model.add_action(
            "simulate", action_args=[("method", "'ssa'"), ("t_end", 2), ("n_steps", 2)]
        )
        with open("init.bngl", "w") as f:
            f.write(str(model))
        r = bionetgen.run("init.bngl", "for_init")
        shutil.copyfile(os.path.join("for_init", "init.net"), "init.net")
        header_str = ""
        for i in r[0].dtype.names:
            header_str += " " + i
        np.savetxt("init.gdat", r[0], header=header_str)
        shutil.rmtree("for_init")
        os.chdir(os.path.join(self.main_dir, self.sim_dir))
        return model

    def run(self):
        """
        runs the class functions in appropriate order to
        make the WESTPA simultion folder
        """
        self.make_sim_folders()
        if self.copy_run_net:
            self.copy_run_network()
        self.write_static_files()
        self.run_BNGL_on_file()
        self.write_dynamic_files()
        return
