import pickle, h5py, os, shutil
from sys import stdout
import numpy as np
import pygpcca as pgp
import subprocess as sbpc
from scipy.sparse import coo_matrix
from webng.analysis.analysis import weAnalysis

# Hacky way to ignore warnings, in particular pyemma insists on Python3
import warnings

warnings.filterwarnings("ignore")
np.set_printoptions(precision=2)


class weCluster(weAnalysis):
    def __init__(self, opts):
        super().__init__(opts)
        # Parse and set the arguments
        # get west.h5 path
        self.westh5_path = os.path.join(self.opts["sim_name"], "west.h5")
        # iterations
        self.first_iter, self.last_iter = self._getd(
            opts, "first-iter", default=None, required=False
        ), self._getd(opts, "last-iter", default=None, required=False)
        # get states
        state_dict = self._getd(opts, "states", default=None, required=True)
        self.states = {"states": state_dict}
        # Open files
        self.assignFile = self._load_assignments(
            self._getd(opts, "assignments", default=None, required=False)
        )
        # Set assignments
        self.assignments = self.assignFile["assignments"]
        # load transition matrix
        self.tm = self._load_trans_mat(
            self._getd(opts, "transition-matrix", default=None, required=False)
        )
        # Set mstable file to save
        self.mstab_file = self._getd(
            opts,
            "metastable-states-file",
            default="metasble_assignments.pkl",
            required=False,
        )
        # Cluster count
        self.cluster_count = self._getd(opts, "cluster-count")
        # Do we symmetrize
        self.symmetrize = self._getd(opts, "symmetrize", default=True, required=False)
        # normalize data so results are in %s
        self.normalize = self._getd(opts, "normalize", default=False, required=False)

    def _load_assignments(self, file_path):
        if file_path is None:
            # we need to make our own
            import yaml

            # we need system.py
            shutil.copy(os.path.join(self.opts["sim_name"], "system.py"), "system.py")
            # sort out states
            self.state_file = "states.yaml"
            # write state file
            with open(self.state_file, "w") as f:
                # yaml.dump(self.states, stdout)
                yaml.dump(self.states, f)
            # assign file setup
            self.assign_file = "assign_voronoi.h5"
            proc = sbpc.Popen(
                [
                    "w_assign",
                    "-W",
                    "{}".format(self.westh5_path),
                    "--states-from-file",
                    "{}".format(self.state_file),
                    "-o",
                    "{}".format(self.assign_file),
                ]
            )
            proc.wait()
        else:
            # we just need to open it
            self.assign_file = file_path
        return h5py.File(self.assign_file, "r")

    def _load_trans_mat(self, tmat_file):
        if tmat_file is None:
            self.tmat_file = "tmat.h5"
            proc = sbpc.Popen(
                [
                    "w_reweight",
                    "init",
                    "-W",
                    "{}".format(self.westh5_path),
                    "-o",
                    "{}".format(self.tmat_file),
                    "-a",
                    "{}".format(self.assign_file),
                ]
            )
            proc.wait()
        else:
            # Load h5 file
            self.tmat_file = tmat_file
        tmh5 = h5py.File(self.tmat_file, "r")
        # We will need the number of rows and columns to convert from
        # sparse matrix format
        nrows = tmh5.attrs["nrows"]
        ncols = tmh5.attrs["ncols"]
        # gotta average over iterations
        tm = None
        if self.first_iter is None:
            self.first_iter = tmh5.attrs["iter_start"]
        if self.last_iter is None:
            self.last_iter = tmh5.attrs["iter_stop"]

        for i in range(self.first_iter, self.last_iter):
            it_str = "iter_{:08d}".format(i)
            col = tmh5["iterations"][it_str]["cols"]
            row = tmh5["iterations"][it_str]["rows"]
            flux = tmh5["iterations"][it_str]["flux"]
            ctm = coo_matrix((flux, (row, col)), shape=(nrows, ncols)).toarray()
            if tm is None:
                tm = ctm
            else:
                tm += ctm
        # We need to convert the "non-markovian" matrix to
        # a markovian matrix here
        # TODO: support more than 2 states
        nstates = 2
        mnrows = int(nrows / nstates)
        mncols = int(ncols / nstates)
        mtm = np.zeros((mnrows, mncols), dtype=flux.dtype)
        for i in range(mnrows):
            for j in range(mncols):
                mtm[i, j] = tm[i * 2 : (i + 1) * 2, j * 2 : (j + 1) * 2].sum()
        mtm = mtm / len(tmh5["iterations"])
        print("Averaged transition matrix")
        print(mtm, mtm.shape)
        return mtm

    def row_normalize(self):
        """ """
        for irow, row in enumerate(self.tm):
            if row.sum() != 0:
                self.tm[irow] /= row.sum()

    def preprocess_tm(self):
        """ """
        zt = np.where(self.tm.sum(axis=1) == 0)
        if len(zt[0]) != 0:
            print("there are bins where there are no transitions")
            print(zt)
            print("removing these bins from the transition matrix")
        ind = np.where(self.tm.sum(axis=1) != 0)[0]
        self.z_inds = zt
        self.nz_inds = ind
        self.tm = self.tm[..., ind][ind, ...]
        if self.symmetrize:
            print("symmetrizing transition matrix")
            self.tm = (self.tm + self.tm.T) / 2.0
        self.row_normalize()

    def print_pcca_results(self):
        """ """
        print("#########################")
        print("crispness vals")
        print(self.pcca.crispness_values)
        print("optimal crisp")
        print(self.pcca.optimal_crispness)
        print("n_m")
        print(self.pcca.n_m)
        print("top eig")
        print(self.pcca.top_eigenvalues)
        print("dom eig")
        print(self.pcca.dominant_eigenvalues)
        print("memberships")
        print(self.pcca.memberships)
        print("stat prob")
        print(self.pcca.stationary_probability)
        print("coarse grained tm")
        print(self.pcca.coarse_grained_transition_matrix)
        print("coarse grained probs")
        print(self.pcca.coarse_grained_stationary_probability)
        print("#########################")

    def cluster(self):
        """ """
        print("##### Clustering #####")
        self.preprocess_tm()
        dims = self.tm.shape[0]
        self.pcca = pgp.GPCCA(self.tm, z="LM", method="brandts")
        print(self.pcca.minChi(self.cluster_count, dims))
        self.pcca.optimize({"m_min": self.cluster_count, "m_max": dims})
        self.p = self.pcca.coarse_grained_stationary_probability
        self.ctm = self.pcca.coarse_grained_transition_matrix
        self.assignments = []
        for i in range(self.pcca.memberships.shape[0]):
            self.assignments.append(
                np.where(
                    self.pcca.memberships[i, :] == max(self.pcca.memberships[i, :])
                )[0][0]
            )
        self.assignments = np.array(self.assignments)
        self.print_pcca_results()

    def save_pcca(self):
        with open("pcca.pkl", "wb") as f:
            pickle.dump(self.pcca, f)

    # def _load_custom_centers(self, centers, nz_inds=None):
    #     '''
    #     '''
    #     print("loading custom centers")
    #     if nz_inds is not None:
    #         ccenters = np.load(centers)[self.nz_inds]
    #     else:
    #         ccenters = np.load(centers)
    #     for i in range(ccenters.shape[1]):
    #         ccenters_i = ccenters[:,i]
    #         if self.normalize:
    #             imin, imax = ccenters_i.min(), ccenters_i.max()
    #             ccenters[:,i] = ccenters[:,i] - imin
    #             if imax > 0:
    #                 ccenters[:,i] = ccenters[:,i]/imax
    #             ccenters *= 100
    #     print("custom centers loaded")
    #     #print(ccenters)
    #     return ccenters

    def load_bin_arrays(self):
        """ """
        a = self.assignFile
        print("loading bin labels")
        bin_labels_str = a["bin_labels"][...]
        bin_labels = []
        for ibstr, bstr in enumerate(bin_labels_str):
            st, ed = bstr.find(b"["), bstr.find(b"]")
            bin_labels.append(eval(bstr[st : ed + 1]))
        bin_labels = np.array(bin_labels)[self.nz_inds]
        for i in range(bin_labels.shape[1]):
            if self.normalize:
                imin, imax = bin_labels[:, i].min(), bin_labels[:, i].max()
                bin_labels[:, i] = bin_labels[:, i] - imin
                if imax > 0:
                    bin_labels[:, i] = bin_labels[:, i] / imax
                bin_labels *= 100
        print("bin labels loaded")
        # print(bin_labels)
        self.bin_labels = bin_labels

    def save_mstable_assignments(self):
        """ """
        # TODO: OBJify
        mstab_ass = self.assignments
        mstabs = []
        li = 0
        for i in self.z_inds[0]:
            mstabs += list(mstab_ass[li:i])
            mstabs += [0]
            li = i
        mstabs += list(mstab_ass[li:])
        self.full_mstabs = np.array(mstabs)
        self.save_full_mstabs()

    def save_full_mstabs(self):
        """ """
        if self.mstab_file is None:
            self.mstab_file = "metasble_assignments.pkl"
        with open(self.mstab_file, "wb") as f:
            pickle.dump(self.full_mstabs, f)

    def print_mstable_states(self):
        """ """
        print("##### Metastable states info #####")
        self.load_bin_arrays()
        a = self.assignments
        # TODO: OBJify
        print("NAMES: ", self.names)
        width = 6
        for i in range(a.max() + 1):
            print(
                "metastable state {} with probability {:.2f}%".format(
                    i, self.p[i] * 100
                )
            )
            print(
                "{} bins are assigned to this state: ".format(
                    len(np.where(a.T == i)[0])
                )
            )
            avg_vals = self.bin_labels[a.T == i].mean(axis=0)
            for iname, name in enumerate(self.names):
                print("  {}: {}".format(self.names[name], avg_vals[iname]))

    def get_mstable_assignments(self):
        """ """
        self.print_mstable_states()
        self.save_mstable_assignments()

    def run(self):
        """ """
        self.cluster()
        self.save_pcca()
        self.get_mstable_assignments()
