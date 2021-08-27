import sys, os


class weAnalysis:
    """
    Base class for all analysis classes.
    """

    def __init__(self, opts):
        # get this in so we can import system.py if need be
        sys.path.append(opts["sim_name"])
        # keep opts around
        self.opts = opts
        # Set work path
        self.work_path = self._getd(opts, "work-path", default=None, required=False)
        if self.work_path is None:
            self.work_path = os.path.join(self.opts["sim_name"], "analysis")
        # we want to go there
        if not os.path.isdir(self.work_path):
            os.mkdir(self.work_path)
        # assert os.path.isdir(self.work_path), "Work path: {} doesn't exist".format(self.work_path)
        self.curr_path = os.getcwd()
        os.chdir(self.work_path)
        # Set names if we have them
        self.set_names(opts["pcoords"])
        # we need to write assignment.py sometimes
        self.pull_data_str = "import numpy as np\n"
        self.pull_data_str += "def pull_data(n_iter, iter_group):\n"
        self.pull_data_str += "    '''\n"
        self.pull_data_str += "    This function reshapes the progress coordinate and\n"
        self.pull_data_str += "    auxiliary data for each iteration and retuns it to\n"
        self.pull_data_str += "    the tool.\n"
        self.pull_data_str += "    '''\n"
        self.pull_data_str += '    data_to_pull = np.loadtxt("data_to_pull.txt") - 1\n'
        self.pull_data_str += "    d1, d2 = data_to_pull\n"
        self.pull_data_str += (
            "    pcoord  = iter_group['pcoord'][:,:,[int(d1),int(d2)]]\n"
        )
        self.pull_data_str += "    data = pcoord\n"
        self.pull_data_str += "    return data\n"

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary".format(key))
        return val

    def set_names(self, names):
        if names is not None:
            self.names = dict(zip(range(len(names)), names))
        else:
            # We know the dimensionality, can assume a
            # naming scheme if we don't have one
            print("Giving default names to each dimension")
            self.names = dict((i, str(i)) for i in range(self.dims))
