import westpa, bionetgen, yaml, os, platform

class weTemplater:
    def __init__(self, args):
        # get arguments
        self.inp_file = args.input
        self.out_file = args.output
        # setup a template dictionary
        self.template_dict = {
            "propagator_options": { "propagator_type": "libRoadRunner",
                                    "pcoords": None},
            "binning_options":  {"block_size": 10, 
                                 "center_freq": 1, 
                                 "max_centers": 300, 
                                 "traj_per_bin": 100},
            "path_options":     {"WESTPA_path": None, 
                                 "bng_path": None,
                                 "bngl_file": None, 
                                 "sim_name": None},
            "sampling_options": {"dimensions": None, 
                                 "max_iter": 10, 
                                 "pcoord_length": 10, 
                                 "tau": 100}
        }
        # adjust dictionary
        self._adjust_template()

    def _get_westpa_path(self):
        # full path to library
        wlib_path = westpa.__path__[0]
        # remove the last two folders, "wpath"/src/westpa
        # is the standard form of this
        wpath = os.path.split(wlib_path)[0]
        wpath = os.path.split(wpath)[0]
        return wpath

    def _get_bng_path(self):
        # now we need the BNG path, get it from the library as well
        # we need the platform and the appropriate folder name
        system = platform.system() 
        if system == "Linux":
            bng_name = "bng-linux"
        elif system == "Windows":
            bng_name = "bng-win"
        elif system == "Darwin":
            bng_name = "bng-mac"
        # get library path
        lib_path = os.path.dirname(bionetgen.__file__)
        bng_path = os.path.join(lib_path, bng_name)
        return bng_path

    def _get_pcoords(self):
        # use bng api to get the model object
        model = bionetgen.bngmodel(self.inp_file)
        obs_arr = []
        # get observable strings
        for obs in model.observables:
            obs_arr.append(str(obs))
        return obs_arr

    def _adjust_template(self):
        # set westpa path
        self.template_dict["path_options"]["WESTPA_path"] = self._get_westpa_path()
        # set bng path
        self.template_dict["path_options"]["bng_path"] = self._get_bng_path()
        # input model
        self.template_dict["path_options"]["bngl_file"] = os.path.abspath(self.inp_file)
        # output folder
        model_file = os.path.split(self.inp_file)[1]
        model_name = os.path.splitext(model_file)[0]
        self.template_dict["path_options"]["sim_name"] = os.path.join(os.getcwd(), model_name)
        # set propagator options, in particular get observable names
        pcoords = self._get_pcoords()
        self.template_dict["propagator_options"]["pcoords"] = pcoords
        self.template_dict["sampling_options"]["dimensions"] = len(pcoords)

    def run(self):
        ystr = yaml.dump(self.template_dict)
        with open(self.out_file, "w") as f:
            f.write(ystr)