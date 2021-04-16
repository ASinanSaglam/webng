# Copyright (C) 2013 Matthew C. Zwier and Lillian T. Chong
#
# This file is part of WESTPA.
#
# WESTPA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WESTPA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WESTPA.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division; __metaclass__ = type
from westtools import WESTTool, WESTDataReader, IterRangeSelection, ProgressIndicatorComponent
import numpy, h5py
import networkx as nx
from scipy.sparse import coo_matrix

import westpa
from westpa import h5io
from west.data_manager import seg_id_dtype, n_iter_dtype, weight_dtype
from westpa.extloader import get_object


# TODO: Add more documentation
class WNetworker(WESTTool):
    prog='w_networker'
    description = '''\
Makes a network file from a transition matrix that can be visualized 
by most graph programs.

-----------------------------------------------------------------------------
Output format
-----------------------------------------------------------------------------

The output file (-o/--output, by default "network.gml") contains the network
as described by the transition matrix found in the transition matrix file

-----------------------------------------------------------------------------
Command-line arguments
-----------------------------------------------------------------------------
'''

    def __init__(self):
        super(WNetworker,self).__init__()

        self.data_reader = WESTDataReader()
        self.iter_range = IterRangeSelection()
        self.progress = ProgressIndicatorComponent()
        self.output_filename = None
        self.tm_filename = None
        self.postprocess_function = None

    def add_args(self, parser):
        self.data_reader.add_args(parser)
        self.iter_range.add_args(parser)
        
        igroup = parser.add_argument_group('input options')
        # TODO: Get WESTPA h5 file and add some stuff from it into nodes
        igroup.add_argument('-tm', '--transition-matrix', default='tm.h5',
                            help='''Use transition matrix from the'''
                            '''resulting h5 file of w_reweigh (default: %(default)s).''')

        ogroup = parser.add_argument_group('output options')
        ogroup.add_argument('-o', '--output', default='network.gml',
                            help='''Write output to OUTPUT (default: %(default)s).''')

        ppgroup = parser.add_argument_group('postprocess options')
        ppgroup.add_argument('--postprocess-function',
                             help='''Names a function (as in module.function) that will be called just prior
                                  to saving the graph. The function will be called as ``postprocess(G, tm, prob)``
                                  where ``G`` is the fully built networkx graph, ``tm`` is the transition matrix
                                  used to build the graph and ``prob`` is the probability distribution used''')
        self.progress.add_args(parser)

    def process_args(self, args):
        self.progress.process_args(args)
        self.data_reader.process_args(args)
        with self.data_reader:
            self.iter_range.process_args(args)
        # Set the attributes according to arguments
        self.output_filename = args.output
        self.tm_filename = args.transition_matrix
        if args.postprocess_function:
            self.postprocess_function = get_object(args.postprocess_function,path=['.'])

    def _load_from_h5(self, fname, istart, istop):
        tmh5 = h5py.File(fname, 'r')
        # We will need the number of rows and columns to convert from 
        # sparse matrix format
        nrows = tmh5.attrs['nrows']
        ncols = tmh5.attrs['ncols']
        # gotta average over iterations
        tm = None
        for it in range(istart, istop):
            it_str = 'iter_{:08}'.format(it)
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
        # Not as straight forward as it seems since there is the 
        # "unknown" state to deal with and it requires a funky
        # fix to go from non-markovian to markovian matrix
        nstates = 2
        mnrows = int(nrows/nstates)
        mncols = int(ncols/nstates)
        mtm = numpy.zeros((mnrows, mncols), dtype=flux.dtype)
        for i in range(mnrows):
            for j in range(mncols):
                mtm[i,j] = tm[i*2:(i+1)*2,j*2:(j+1)*2].sum()
        mtm = mtm/len(tmh5['iterations'])
        # Let's also get probabilities
        bin_probs = tmh5['bin_populations']
        avg_bin_probs = numpy.average(bin_probs[istart:istop], axis=0)/nstates
        prob = avg_bin_probs.reshape(mnrows, nstates).sum(axis=1)
        return mtm, prob

    def read_tmfile(self, fname, istart, istop):
        if fname.endswith('.h5'):
            tm, prob = self._load_from_h5(fname, istart, istop)
        else:
            # TODO: error out
            pass
        return tm, prob

    def save_graph(self, outname, graph):
        # determine save function
        if outname.endswith(".gml"):
            func = nx.write_gml
        else:
            # TODO: error out
            pass
        func(graph, outname)

    def go(self):
        self.data_reader.open('r')
        # Get the iterations we want to average the tm if needed
        iter_start, iter_stop = self.iter_range.iter_start, self.iter_range.iter_stop
        # Read transition matrix and probabilities
        tm, prob = self.read_tmfile(self.tm_filename, iter_start, iter_stop)
        # Start the progress indicator and work on the graph
        pi = self.progress.indicator
        with pi:
            node_sizes = prob
            edge_sizes = tm

            pi.new_operation('Building graph, adding nodes', extent=len(node_sizes))
            G = nx.DiGraph()
            for i in range(tm.shape[0]):
                if node_sizes[i] > 0:
                    G.add_node(i, weight=float(node_sizes[i])) 
                pi.progress += 1
            
            pi.new_operation('Adding edges', extent=len(edge_sizes.flatten()))
            for i in range(tm.shape[0]):
                for j in range(tm.shape[1]):
                    if edge_sizes[i][j] > 0:
                        G.add_edge(i, j, weight=float(edge_sizes[i][j])) 
                    pi.progress += 1

            if self.postprocess_function:
                self.postprocess_function(G, tm, prob)
            self.save_graph(self.output_filename, G)

if __name__ == '__main__':
    WNetworker().main()
