import sys

class weAnalysis:
    def __init__(self):
        # we need to write assignment.py sometimes
        self.pull_data_str =  "import numpy as np\n"
        self.pull_data_str += "def pull_data(n_iter, iter_group):\n"
        self.pull_data_str += "    '''\n"
        self.pull_data_str += "    This function reshapes the progress coordinate and\n"
        self.pull_data_str += "    auxiliary data for each iteration and retuns it to\n"
        self.pull_data_str += "    the tool.\n"
        self.pull_data_str += "    '''\n"
        self.pull_data_str += "    data_to_pull = np.loadtxt(\"data_to_pull.txt\") - 1\n"
        self.pull_data_str += "    d1, d2 = data_to_pull\n"
        self.pull_data_str += "    pcoord  = iter_group['pcoord'][:,:,[int(d1),int(d2)]]\n"
        self.pull_data_str += "    data = pcoord\n"    
        self.pull_data_str += "    return data\n"

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary".format(key))
        return val