import pickle, h5py, sys, argparse
import numpy as np
import networkx as nx
import pyemma as pe 
from scipy.sparse import coo_matrix
from webng.analysis.analysis import weAnalysis

# Hacky way to ignore warnings, in particular pyemma insists on Python3
import warnings
warnings.filterwarnings("ignore")
np.set_printoptions(precision=2)

class weCluster(weAnalysis):
    def __init__(self, opts):
        super().__init__()
        # Get arguments as usual
        self._parse_args()
        # Parse and set the arguments
        # iterations
        self.iiter, self.fiter = self.args.iiter, self.args.fiter
        # Open files 
        self.assignFile = h5py.File(self.args.assign_path, 'r')
        self.tm = self._load_trans_mat(self.args.trans_mat_file)
        # Set mstable file to save
        self.mstab_file = self.args.mstab_file
        # Set assignments
        self.assignments = self.assignFile['assignments']
        # Cluster count
        self.cluster_count = self.args.cluster_count
        # Do we symmetrize
        self.symmetrize = self.args.symmetrize
        # name file 
        self.name_path = self.args.name_path
        # normalize data so results are in %s 
        self.normalize = self.args.normalize

    def _parse_args(self):
        parser = argparse.ArgumentParser()

        # Data input options
        parser.add_argument('-TM', '--trans_mat',
                            dest='trans_mat_file',
                            default="tmat.h5",
                            help='Path to the w_reweight output h5 file'
                            'that contains the transition matrix',
                            type=str)

        parser.add_argument('-A', '--assignh5',
                            dest='assign_path',
                            default="assign.h5",
                            help='Path to the assignment h5 file', 
                            type=str)

        parser.add_argument('--mstab-file',
                            dest='mstab_file',
                            default="metasble_assignments.pkl",
                            help='File to save metastable assignments into',
                            type=str)

        # Cluster count
        parser.add_argument('--pcca-count', required=True,
                          dest='cluster_count',
                          help='Cluster count for the PCCA+ algorithm',
                          type=int)

        # Do we symmetrize the matrix?
        parser.add_argument('--symmetrize-matrix',
                            dest='symmetrize', action='store_true', default=False,
                            help='Symmetrize matrix using (TM + TM.T)/2.0')

        parser.add_argument('--normalize', '-n',
                            dest='normalize', action='store_true', default=False,
                            help='Normalizes the data such that min/max is 0/1')

        parser.add_argument('--name-file',
                            dest='name_path',
                            default=None,
                            help='Text file containing the names of each dimension separated by spaces',
                            type=str)
        
        parser.add_argument('--halton-centers',
                            dest='halton_centers',
                            default=None,
                            help='np.load\'able file for custom halton centers rather than the mapper centers',
                            type=str)

        parser.add_argument('--first-iter', default=None,
                          dest='iiter',
                          help='Average TM starting from this iteration'
                               'By default, TM will be averaged starting from the first ' 
                               'iteration in the specified h5 file. ',
                          type=int)

        parser.add_argument('--last-iter', default=None,
                          dest='fiter',
                          help='Average TM ending in this iteration '
                               'LAST_ITER. By default, TM will be averaged up to'
                               'and including the last iteration in the specified h5 file',
                          type=int)

        self.args = parser.parse_args()

    def _load_trans_mat(self, tmat_file):
        # Load h5 file
        tmh5 = h5py.File(tmat_file, 'r')
        # We will need the number of rows and columns to convert from 
        # sparse matrix format
        nrows = tmh5.attrs['nrows']
        ncols = tmh5.attrs['ncols']
        # gotta average over iterations
        tm = None
        if self.iiter is None:
            self.iiter = tmh5.attrs['iter_start']
        if self.fiter is None:
            self.fiter = tmh5.attrs['iter_stop']

        for i in range(self.iiter, self.fiter):
            it_str = "iter_{:08d}".format(i)
            col = tmh5['iterations'][it_str]['cols']
            row = tmh5['iterations'][it_str]['rows']
            flux = tmh5['iterations'][it_str]['flux']
            ctm = coo_matrix((flux, (row,col)), shape=(nrows, ncols)).toarray()
            if tm is None:
                tm = ctm
            else:
                tm += ctm
        # We need to convert the "non-markovian" matrix to 
        # a markovian matrix here
        # TODO: support more than 2 states
        nstates = 2
        mnrows = nrows/nstates
        mncols = ncols/nstates
        mtm = np.zeros((mnrows, mncols), dtype=flux.dtype)
        for i in range(mnrows):
            for j in range(mncols):
                mtm[i,j] = tm[i*2:(i+1)*2,j*2:(j+1)*2].sum()
        mtm = mtm/len(tmh5['iterations'])
        print("Averaged transition matrix")
        print(mtm, mtm.shape)
        return mtm

    def row_normalize(self):
        '''
        '''
        for irow, row in enumerate(self.tm):
            if row.sum() != 0:
                self.tm[irow] /= row.sum() 

    def preprocess_tm(self):
        '''
        '''
        zt = np.where(self.tm.sum(axis=1)==0)
        if len(zt[0]) != 0:
            print("there are bins where there are no transitions")
            print(zt)
            print("removing these bins from the transition matrix")
        ind = np.where(self.tm.sum(axis=1)!=0)[0]
        self.z_inds = zt
        self.nz_inds = ind
        self.tm = self.tm[...,ind][ind,...]
        if self.symmetrize:
            print("symmetrizing transition matrix")
            self.tm = (self.tm + self.tm.T)/2.0
        self.row_normalize()

    def print_pcca_results(self):
        '''
        '''
        print("##### Clustering results #####")
        print("MSM probs")
        print(self.p*100)
        print("MSM TM")
        print(self.ctm*100)

    def cluster(self):
        '''
        '''
        print("##### Clustering #####")
        self.preprocess_tm()

        self.MSM = pe.msm.MSM(self.tm, reversible=True)
        self.pcca = self.MSM.pcca(self.cluster_count)
        self.p = self.pcca.coarse_grained_stationary_probability
        self.ctm = self.pcca.coarse_grained_transition_matrix
        self.mstable_assignments = self.pcca.metastable_assignment
        self.max_mstable_states = self.mstable_assignments.max()
        self.print_pcca_results()

    def save_pcca(self):
        f = open("pcca.pkl", 'w')
        pickle.dump(self.pcca, f)
        f.close()

    def load_names(self):
        '''
        '''
        # TODO: OBJify

        if self.name_path is not None:
            name_file = open(self.name_path, 'r')
            self.names = name_file.readline().split()
            name_file.close()
        else:
            self.names = [str(i) for i in range(self.bin_labels.shape[1])]

    def _load_custom_centers(self, centers, nz_inds=None):
        '''
        '''
        print("loading custom centers")
        if nz_inds is not None:
            ccenters = np.load(centers)[self.nz_inds]
        else:
            ccenters = np.load(centers)
        for i in range(ccenters.shape[1]):
            ccenters_i = ccenters[:,i]
            if self.normalize:
                imin, imax = ccenters_i.min(), ccenters_i.max()
                ccenters[:,i] = ccenters[:,i] - imin
                if imax > 0:
                    ccenters[:,i] = ccenters[:,i]/imax
                ccenters *= 100
        print("custom centers loaded")
        #print(ccenters)
        return ccenters

    def load_bin_arrays(self):
        '''
        '''
        a = self.assignFile
        print("loading bin labels")
        bin_labels_str = a['bin_labels'][...]
        bin_labels = []
        for ibstr, bstr in enumerate(bin_labels_str):
            st, ed = bstr.find('['), bstr.find(']')
            bin_labels.append(eval(bstr[st:ed+1]))
        bin_labels = np.array(bin_labels)[self.nz_inds]
        for i in range(bin_labels.shape[1]):
            if self.normalize:
                imin, imax = bin_labels[:,i].min(), bin_labels[:,i].max()
                bin_labels[:,i] = bin_labels[:,i] - imin
                if imax > 0:
                    bin_labels[:,i] = bin_labels[:,i]/imax
                bin_labels *= 100
        print("bin labels loaded")
        #print(bin_labels)
        self.bin_labels = bin_labels

    def save_mstable_assignments(self):
        '''
        '''
        # TODO: OBJify
        mstab_ass = self.mstable_assignments
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
        '''
        '''
        f = open(self.mstab_file, 'w')
        pickle.dump(self.full_mstabs, f)
        f.close()

    def print_mstable_states(self):
        '''
        '''
        print("##### Metastable states info #####")
        if self.halton_centers is None:
            self.load_bin_arrays()
        else:
            self.bin_labels = self._load_custom_centers(self.halton_centers, nz_inds=self.nz_inds)
        self.load_names()
        a = self.mstable_assignments
        # TODO: OBJify
        width = 6
        for i in range(a.max()+1):
            print("metastable state {} with probability {:.2f}%".format(i, self.p[i]*100))
            print("{} bins are assigned to this state".format(len(np.where(a.T==i)[0])))
            for name in self.names:
                # python 2.7 specific unfortunately
                print('{0:^{width}}'.format(name, width=width, align="center"),)
            # similarly 2.7 specific
            print()
            avg_vals = self.bin_labels[a.T==i].mean(axis=0)
            for val in avg_vals:
                # python 2.7 specific unfortunately
                print('{0:{width}.2f}'.format(val, width=width),)
            # similarly 2.7 specific
            print

    def get_mstable_assignments(self):
        '''
        '''
        self.print_mstable_states()
        self.save_mstable_assignments()

    def run(self):
        '''
        '''
        self.cluster()
        self.save_pcca()
        self.get_mstable_assignments()
