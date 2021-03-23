import pickle, h5py, sys, argparse
import numpy as np
import networkx as nx
import pyemma as pe 

#TODO: Turn into WESTPA tool
# Hacky way to ignore warnings, in particular pyemma insists on Python3
import warnings
warnings.filterwarnings("ignore")
np.set_printoptions(precision=2)

class PCCANetworker:
    def __init__(self):
        # Get arguments as usual
        self._parse_args()
        # Parse and set the arguments
        # Open files 
        self.pcca = self._load_pickle(self.args.pcca_pickle)
        self.full_tm = self.pcca.transition_matrix
        self.coarse_tm = self.pcca.transition_matrix
        # Set mstable file to load 
        self.mstabs = self._load_pickle(self.args.mstab_file)
        # name file 
        self.state_labels = self._load_state_labels(self.args.state_labels)
        self._set_state_dicts()

    def _parse_args(self):
        parser = argparse.ArgumentParser()

        # Data input options
        parser.add_argument('-PCCA', '--pcca-pickle',
                            dest='pcca_pickle',
                            default="pcca.pkl",
                            help='Path to the pickled PCCA+ object',
                            type=str)

        parser.add_argument('--mstab-file',
                            dest='mstab_file',
                            default='metasble_assignments.pkl',
                            help='File to load metastable assignments from',
                            type=str)

        parser.add_argument('--state-labels',
                            dest='state_labels',
                            default=None,
                            help='Text file containing the state labels for each coarse grained state',
                            type=str)

        self.args = parser.parse_args()

    def _load_pickle(self, filename):
        f = open(filename, 'r')
        l = pickle.load(f)
        f.close()
        return l

    def _load_state_labels(self, slfile):
        '''
        '''
        if slfile is not None:
            slfile = open(slfile, 'r')
            labels = slfile.readline().split()
            slfile.close()
        else:
            labels = [str(i) for i in range(self.mstabs.max())]

        return labels

    def _set_state_dicts(self):
        # Get the dictionary
        self.state_label_dict = dict(zip(range(len(self.state_labels)), self.state_labels))
        # Use matplotlib to pull colors for every state
        self.state_colors = {0: "#FF00FF", 1: "#000000", 2: "#FF0000", 3:"#0000FF"}
        return

    def get_full_network(self):
        node_sizes = self.pcca.stationary_probability*1000
        edge_sizes = self.pcca.transition_matrix
        tm = edge_sizes

        G = nx.DiGraph()
        for i in range(tm.shape[0]):
            if node_sizes[i] > 0:
                G.add_node(i, weight=float(node_sizes[i]), color=self.state_colors[self.mstabs[i]], 
                        LabelGraphics={"text": " "}, graphics={"type": "circle", "fill": self.state_colors[self.mstabs[i]], 
                                                               "w": node_sizes[i], "h": node_sizes[i]})
        
        for i in range(tm.shape[0]):
            for j in range(tm.shape[1]):
                if i != j:
                    #if edge_sizes[i][j] > 1e-2:
                    if edge_sizes[i][j] > 0:
                        G.add_edge(i, j, weight=float(edge_sizes[i][j]), 
                                   graphics={"type": "arc", 
                                       "targetArrow": "none", "fill": self.state_colors[self.mstabs[i]]})
        
        self.network = G
        self.curr_network_ext = "full"
        return

    def get_coarse_network(self):
        node_sizes = self.pcca.coarse_grained_stationary_probability*1000
        edge_sizes = self.pcca.coarse_grained_transition_matrix
        tm = edge_sizes
        
        G = nx.DiGraph()
        for i in range(tm.shape[0]):
            if node_sizes[i] > 0:
                G.add_node(i, weight=float(node_sizes[i]), color=self.state_colors[i], LabelGraphics={"text": " "}, #)
                       graphics={"type": "circle", "fill": self.state_colors[i], "w": node_sizes[i], "h": node_sizes[i]})
        
        for i in range(tm.shape[0]):
            for j in range(tm.shape[1]):
                if i != j:
                    if edge_sizes[i][j] > 0:
                        G.add_edge(i, j, weight=float(edge_sizes[i][j]), 
                                   graphics={"type": "arc", "targetArrow": "none", 
                                             "fill": self.state_colors[i]})
        
        self.network = G
        self.curr_network_ext = "coarse"
        return

    def save_network(self):
        nx.write_gml(self.network, "pcca_{}.gml".format(self.curr_network_ext))
        return

    def run(self):
        '''
        '''
        self.get_full_network()
        self.save_network()
        self.get_coarse_network()
        self.save_network()


if __name__ == '__main__':
    n = PCCANetworker()
    n.run()
