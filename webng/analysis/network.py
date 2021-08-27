import pickle, os, sys
import numpy as np
import networkx as nx
from webng.analysis.analysis import weAnalysis

# Hacky way to ignore warnings, in particular pyemma insists on Python3
import warnings

warnings.filterwarnings("ignore")
np.set_printoptions(precision=2)


class weNetwork(weAnalysis):
    def __init__(self, opts):
        # get our parent initialization setup
        super().__init__(opts)
        # Parse and set the arguments
        # Load PCCA
        default_pcca = os.path.join(self.work_path, "pcca.pkl")
        self.pcca_path = self._getd(
            opts, "pcca-pickle", default=default_pcca, required=False
        )
        if self.pcca_path is None:
            self.pcca_path = default_pcca
        try:
            self.pcca = self._load_pickle(self.pcca_path)
        except:
            print("can't open file {}, quitting".format(self.pcca_path))
            sys.exit()
        # Get transition matrix
        self.full_tm = self.pcca.transition_matrix
        self.coarse_tm = self.pcca.transition_matrix
        # Set mstable file to load
        default_mstab = os.path.join(self.work_path, "metasble_assignments.pkl")
        self.mstab_file = self._getd(
            opts, "metastable-states", default=default_mstab, required=False
        )
        self.mstabs = self._load_pickle(self.mstab_file)
        # name file
        self.state_label_path = self._getd(
            opts, "state-labels", default=None, required=False
        )
        self.state_labels = self._load_state_labels(self.state_label_path)
        self._set_state_dicts()

    def _load_pickle(self, filename):
        with open(filename, "rb") as f:
            l = pickle.load(f)
        return l

    def _load_state_labels(self, slfile):
        """ """
        if slfile is not None:
            with open(slfile, "r") as f:
                labels = f.readline().split()
        else:
            labels = [str(i) for i in range(self.mstabs.max())]

        return labels

    def _set_state_dicts(self):
        # Get the dictionary
        self.state_label_dict = dict(
            zip(range(len(self.state_labels)), self.state_labels)
        )
        # Use matplotlib to pull colors for every state
        self.state_colors = {
            0: "#FF00FF",
            1: "#000000",
            2: "#FF0000",
            3: "#0000FF",
            4: "#FFFFFF",
        }
        return

    def get_full_network(self):
        node_sizes = self.pcca.stationary_probability * 1000
        edge_sizes = self.pcca.transition_matrix
        tm = edge_sizes

        G = nx.DiGraph()
        for i in range(tm.shape[0]):
            if node_sizes[i] > 0:
                G.add_node(
                    i,
                    weight=float(node_sizes[i]),
                    color=self.state_colors[self.mstabs[i]],
                    LabelGraphics={"text": " "},
                    graphics={
                        "type": "circle",
                        "fill": self.state_colors[self.mstabs[i]],
                        "w": node_sizes[i],
                        "h": node_sizes[i],
                    },
                )

        for i in range(tm.shape[0]):
            for j in range(tm.shape[1]):
                if i != j:
                    # if edge_sizes[i][j] > 1e-2:
                    if edge_sizes[i][j] > 0:
                        G.add_edge(
                            i,
                            j,
                            weight=float(edge_sizes[i][j]),
                            graphics={
                                "type": "arc",
                                "targetArrow": "none",
                                "fill": self.state_colors[self.mstabs[i]],
                            },
                        )

        self.network = G
        self.curr_network_ext = "full"
        return

    def get_coarse_network(self):
        node_sizes = self.pcca.coarse_grained_stationary_probability * 1000
        edge_sizes = self.pcca.coarse_grained_transition_matrix
        tm = edge_sizes

        G = nx.DiGraph()
        for i in range(tm.shape[0]):
            if node_sizes[i] > 0:
                G.add_node(
                    i,
                    weight=float(node_sizes[i]),
                    color=self.state_colors[i],
                    LabelGraphics={"text": " "},  # )
                    graphics={
                        "type": "circle",
                        "fill": self.state_colors[i],
                        "w": node_sizes[i],
                        "h": node_sizes[i],
                    },
                )

        for i in range(tm.shape[0]):
            for j in range(tm.shape[1]):
                if i != j:
                    if edge_sizes[i][j] > 0:
                        G.add_edge(
                            i,
                            j,
                            weight=float(edge_sizes[i][j]),
                            graphics={
                                "type": "arc",
                                "targetArrow": "none",
                                "fill": self.state_colors[i],
                            },
                        )

        self.network = G
        self.curr_network_ext = "coarse"
        return

    def save_network(self):
        nx.write_gml(self.network, "pcca_{}.gml".format(self.curr_network_ext))
        return

    def run(self):
        """ """
        self.get_full_network()
        self.save_network()
        self.get_coarse_network()
        self.save_network()
