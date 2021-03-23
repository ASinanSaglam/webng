import h5py, sys, argparse
import numpy as np
np.set_printoptions(precision=3)

# TODO: Add logic to build an assingment file if it's not there?
class TransMatCalculator:
    def __init__(self):
        # Get arguments first
        self._parse_args()
        # Parse and set the arguments
        # First open the files
        self.h5file = h5py.File(self.args.h5file_path, 'r')
        self.assignFile = h5py.File(self.args.assign_path, 'r')
        # Set output name
        self.outname = self.args.outname
        # Set assignments
        self.assignments = self.assignFile['assignments']
        # Set range
        self.first_iter = self.args.first_iter
        self.last_iter = self.args.last_iter
        # make sure assignments cover the range
        hstop_iter = self.assignments.attrs['iter_stop']
        if self.last_iter > hstop_iter:
            sys.exit("The assignment file (up to {}) doesn't cover"
            " the requested range of up to iteration {}".format(\
            hstop_iter, self.last_iter))

    def _parse_args(self):
        '''
        '''
        parser = argparse.ArgumentParser()

        # Data input options
        parser.add_argument('-W', '--westh5',
                            dest='h5file_path',
                            default="west.h5",
                            help='Path to the WESTPA h5 file', 
                            type=str)
        parser.add_argument('-A', '--assignh5',
                            dest='assign_path',
                            default="assign.h5",
                            help='Path to the assignment h5 file', 
                            type=str)
        parser.add_argument('-o', '--outname', default=None,
                          dest='outname',
                          help='Name of the output numpy binary file',
                          type=str)
        # Averaging window
        parser.add_argument('--first-iter', default=None,
                          dest='first_iter',
                          help='Plot data starting at iteration FIRST_ITER. '
                               'By default, plot data starting at the first ' 
                               'iteration in the specified w_pdist file. ',
                          type=int)

        parser.add_argument('--last-iter', default=None,
                          dest='last_iter',
                          help='Plot data up to and including iteration '
                               'LAST_ITER. By default, plot data up to and '
                               'including the last iteration in the specified ',
                          type=int)


        self.args = parser.parse_args()

    def get_parent(self,iiter):
        '''
        '''
        return self.h5file['iterations/iter_%08d'%iiter]['seg_index']['parent_id']
    
    def get_weight(self,iiter):
        '''
        '''
        return self.h5file['iterations/iter_%08d'%iiter]['seg_index']['weight']
    
    def get_assignment(self,iiter):
        '''
        '''
        return self.assignments[iiter-1,:,:]
    
    def get_walk_counts(self,iiter):
        '''
        '''
        return self.h5file['summary']['n_particles'][iiter-1]

    def init_matrix(self):
        '''
        '''

        print("Total number of bins is {}".format(self.assignFile['bin_labels'].shape[0]))
        tm_s = self.assignFile['bin_labels'].shape[0]
        tm = np.zeros((tm_s, tm_s))
        return tm

    def set_iter_range(self, iiter, fiter):
        '''
        '''
        if iiter is None:
            iiter = 0
        if fiter is None:
            fiter = self.h5file.attrs['west_current_iteration'] - 1
        print("Setting averaging window {} to {}".format(iiter, fiter))

        return iiter, fiter 


    def calculate_matrix(self):
        '''
        '''
        tm = self.init_matrix()
        max_assign = tm.shape[0]
        iiter, fiter = self.set_iter_range(self.first_iter, self.last_iter)

        ctr = 0
        print("working on averaging")
        for iiter, iter_arr in enumerate(self.assignments):
            ctr += 1
            if iiter > iiter or iiter <= fiter:
                n_walks = self.get_walk_counts(iiter+1)
                parents = self.get_parent(iiter+1)
                ass = self.get_assignment(iiter)
                weights = self.get_weight(iiter+1)
                for iwalk in range(n_walks):
                    walk = iter_arr[iwalk]
                    parent = parents[iwalk]
                    weight = weights[iwalk]
                    prev_ass = ass[parent] 
                    if walk[0] < max_assign and walk[1] < max_assign: 
                        tm[walk[0]][walk[1]] += weight
                    if prev_ass[1] < max_assign and walk[0] < max_assign: 
                        tm[prev_ass[1]][walk[0]] += weight

        tm /= ctr
        print(tm.sum(axis=1))
        print(tm.sum(axis=0))
        print("averaged transition matrix")
        print(tm)
        np.save(self.outname, tm)

if __name__ == '__main__':
    tmc = TransMatCalculator()
    tmc.calculate_matrix()
