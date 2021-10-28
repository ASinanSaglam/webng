import westpa, bionetgen, yaml, os, platform


class weTemplater:
    """
    This is the class that will be used by the command line tool when it's
    called with the subcommand `webng template`.

    The class needs and object containing input/output attributes (usually a
    argparser object) for initialization.

    The `run` method will write a template webng config file using the given
    options as well as paths acquired from imported libraries.
    """

    def __init__(self, args):
        # get arguments
        if args.input is None:
            # let's write a sample model file
            with open("exmisa.bngl", "w") as f:
                f.write(
                    "begin model\n"
                    + "begin parameters\n"
                    + "    g0 4.0\n"
                    + "    g1 18.0\n"
                    + "    k 1.0\n"
                    + "    ha 1E-5\n"
                    + "    hr 1E-1\n"
                    + "    fa 1E-5\n"
                    + "    fr 1.0\n"
                    + "end parameters\n"
                    + "begin molecule types\n"
                    + "    A()\n"
                    + "    B()\n"
                    + "    GeneA_00()\n"
                    + "    GeneA_01()\n"
                    + "    GeneA_10()\n"
                    + "    GeneB_00()\n"
                    + "    GeneB_01()\n"
                    + "    GeneB_10()\n"
                    + "end molecule types\n"
                    + "begin species #initial molecule count\n"
                    + "    GeneA_00() 1\n"
                    + "    GeneA_01() 0\n"
                    + "    GeneA_10() 0\n"
                    + "    GeneB_00() 1\n"
                    + "    GeneB_01() 0\n"
                    + "    GeneB_10() 0\n"
                    + "    A() 4\n"
                    + "    B() 18\n"
                    + "end species\n"
                    + "begin observables\n"
                    + "    Molecules Atot A()\n"
                    + "    Molecules Btot B()\n"
                    + "end observables\n"
                    + "begin reaction rules\n"
                    + "    GeneA_00() + A() + A() <-> GeneA_10() ha, fa\n"
                    + "    GeneA_00() + B() + B() <-> GeneA_01() hr, fr\n"
                    + "    GeneA_00() -> GeneA_00() + A() g0\n"
                    + "    GeneA_01() -> GeneA_01() + A() g0\n"
                    + "    GeneA_10() -> GeneA_10() + A() g1\n"
                    + "    GeneB_00() + A() + A() <-> GeneB_01() hr, fr\n"
                    + "    GeneB_00() + B() + B() <-> GeneB_10() ha, fa\n"
                    + "    GeneB_00() -> GeneB_00() + B() g0\n"
                    + "    GeneB_01() -> GeneB_01() + B() g0\n"
                    + "    GeneB_10() -> GeneB_10() + B() g1\n"
                    + "    A() -> 0 k\n"
                    + "    B() -> 0 k\n"
                    + "end reaction rules\n"
                    + "end model\n"
                )
                self.inp_file = "exmisa.bngl"
        else:
            self.inp_file = args.input
        self.out_file = args.output
        # setup a template dictionary
        self.template_dict = {
            "propagator_options": {"propagator_type": "libRoadRunner", "pcoords": None},
            "binning_options": {
                "block_size": 10,
                "center_freq": 1,
                "max_centers": 300,
                "traj_per_bin": 100,
            },
            "path_options": {
                "WESTPA_path": None,
                "bng_path": None,
                "bngl_file": None,
                "sim_name": None,
            },
            "sampling_options": {
                "dimensions": None,
                "max_iter": 100,
                "pcoord_length": 10,
                "tau": 100,
            },
            "analyses": {
                "enabled": False,
                "work-path": None,
                "average": {
                    "enabled": False,
                    "mapper-iter": None,
                    "plot-voronoi": False,
                    "plot-energy": False,
                    "normalize": False,
                    "first-iter": None,
                    "last-iter": None,
                    "dimensions": None,
                    "output": "average.png",
                    "smoothing": 0.5,
                    "plot-opts": {
                        "name-font-size": 12,
                        "voronoi-lw": 1,
                        "voronoi-col": 0.75,
                    },
                },
                "evolution": {
                    "enabled": False,
                    "plot-energy": False,
                    "normalize": False,
                    "dimensions": None,
                    "output": "evolution.png",
                    "avg_window": 1,
                    "plot-opts": {
                        "name-font-size": 12,
                    },
                },
                "cluster": {
                    "enabled": False,
                    "first-iter": None,  # default, beginning of sim
                    "last-iter": None,  # default, end of sim
                    "transition-matrix": None,  # default, make a new one
                    "assignments": None,  # default, make a new one
                    "metastable-states-file": None,  # default, metasble_assignments.pkl
                    "cluster-count": 2,  # default, 2, require the cluster count
                    "normalize": None,  # default false
                    "symmetrize": None,  # default true
                    "states": [
                        {"label": "a", "coords": [[20.0, 4.0]]},
                        {"label": "b", "coords": [[4.0, 20.0]]},
                    ],
                },
                "network": {
                    "enabled": False,
                    "pcca-pickle": None,
                    "metastable-states-file": None,
                    "state-labels": None,
                },
            },
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
        self.template_dict["path_options"]["sim_name"] = os.path.join(
            os.getcwd(), model_name
        )
        # set propagator options, in particular get observable names
        pcoords = self._get_pcoords()
        self.template_dict["propagator_options"]["pcoords"] = pcoords
        self.template_dict["sampling_options"]["dimensions"] = len(pcoords)
        # # update analysis options as well
        # for an_key in self.template_dict["analyses"].keys():
        #     if an_key == "enabled":
        #         continue
        #     self.template_dict["analyses"][an_key]["work-path"] = \
        #         os.path.join(self.template_dict["path_options"]["sim_name"], "analysis")

    def run(self):
        ystr = yaml.dump(self.template_dict)
        with open(self.out_file, "w") as f:
            f.write(ystr)
