import os, sys, h5py, argparse
import scipy.ndimage
import subprocess as sbpc
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import itertools as itt
import assignment as asgn
import voronoi_plot as vp
#from 

# Hacky way to disable warnings so we can focus on important stuff
import warnings 
warnings.filterwarnings("ignore")

# TODO: Separate out the pdisting, use native code
# TODO: Hook into native code to decouple some parts like # of dimensions etc.
# we need the system.py anyway, let's use native code to read CFG file
class evoPlotter:
    def __init__(self):
        # Let's parse cmdline arguments
        self._parse_args()
        # Once the arguments are parsed, do a few prep steps, opening h5file
        self.h5file_path = self.args.h5file_path
        self.h5file = h5py.File(self.args.h5file_path, 'r')
        # Set the dimensionality 
        self.set_dims(self.args.dims)
        # Set names if we have them
        self.set_names(self.args.names)
        # Set work path
        self.work_path = self.args.work_path
        # Plotting energies or not?
        self.do_energy = self.args.do_energy
        # output name
        self.outname = self.args.outname
        # averaging window
        self.avg_window = self.args.avg_window
        # set last iter
        self.last_iter = self.h5file.attrs['west_current_iteration'] - 1

    def _parse_args(self):
        parser = argparse.ArgumentParser()

        # TODO: Add defaults to help output
        # Data input options
        parser.add_argument('-W', '--westh5',
                            dest='h5file_path',
                            default="west.h5",
                            help='Path to the WESTPA h5 file', 
                            type=str)

        parser.add_argument('--work-path',
                            dest='work_path', default=os.getcwd(),
                            help='Path to do our work in, save figs, the pdist files etc.',
                            type=str)

        parser.add_argument('--name-file',
                            dest='names',
                            default=None,
                            help='Text file containing the names of each dimension separated by spaces',
                            type=str)

        parser.add_argument('--do-energy',
                            dest='do_energy', action='store_true', default=False,
                            help='Plot -lnP instead of probabilities')

        parser.add_argument('-aw', '--avg-window', default=10,
                          dest='avg_window',
                          help='Averaging window size in iterations',
                          type=int)

        # TODO Support a list of dimensions instead
        parser.add_argument('--dimensions', default=None,
                          dest='dims',
                          help='Number of dimensions to plot, at the moment a'
                                'list of dimensions is not supported',
                          type=int)

        parser.add_argument('-o', '--outname', default=None,
                          dest='outname',
                          help='Name of the output file, extension determines the format',
                          type=str)

        self.args = parser.parse_args()


    def set_dims(self, dims=None):
        if dims is None:
            dims = self.h5file['iterations/iter_{:08d}'.format(1)]['pcoord'].shape[2]
        self.dims = dims
        # return the dimensionality if we need to 
        return self.dims

    def set_names(self, name_file):
        print("Loading names from file {}".format(name_file))
        if name_file is not None:
            f = open(name_file, 'r')
            n = f.readline()
            f.close()
            names = n.split()
            self.names = dict( zip(range(len(names)), names) )
        else:
            # We know the dimensionality, can assume a 
            # naming scheme if we don't have one
            print("Giving default names to each dimension")
            self.names = dict( (i, str(i)) for i in range(self.dims) )

    def setup_figure(self):
        # Setup the figure and names for each dimension
        #plt.figure(figsize=(20,20))
        plt.figure(figsize=(1.5,3.0))
        rows = self.dims/2
        f, axarr = plt.subplots(rows,2)
        f.subplots_adjust(hspace=1.2, wspace=0.2, bottom=0.1, left=0.06, top=0.98, right=0.98)
        if rows == 1:
            axarr = np.array([axarr])
        return f, axarr

    def save_fig(self):
        # setup our output filename
        if self.outname is not None:
            outname = self.outname
        else:
            outname = "all_{:05d}.png".format(self.last_iter)

        # save the figure
        print("Saving figure to {}".format(outname))
        plt.savefig(outname, dpi=600)
        plt.close()
        return 

    def open_pdist_file(self, fdim):
        # TODO: Rewrite so that it uses w_pdist directly and we can avoid using
        # --construct-dataset and remove the dependency on assignment.py here
        if fdim != self.dims:
            pfile = os.path.join(self.work_path, "pdist_{}_{}.h5".format(fdim, self.dims))
        else:
            pfile = os.path.join(self.work_path, "pdist_1_{}.h5".format(self.dims))
        # for now let's just get it working
        try:
            open_file = h5py.File(pfile, 'r')
            return open_file
        except IOError:
            print("Cannot open pdist file for {}, calling w_pdist".format(fdim))
            # We are assuming we don't have the file now
            # TODO: Expose # of bins somewhere, this is REALLY hacky,
            # I need to fiddle with w_pdist to fix it up
            f = open("data_to_pull.txt", "w")
            f.write("{} {}".format(fdim, self.dims))
            f.close()
            proc = sbpc.Popen(["w_pdist", "-W", "{}".format(self.h5file_path), 
                       "-o", "{}".format(pfile), "-b", "30", 
                       "--construct-dataset", "assignment.pull_data"])
            proc.wait()
            assert proc.returncode == 0, "w_pdist call failed, exiting"
            open_file = h5py.File(pfile, 'r')
            return open_file
            
    def plot(self, ext=None):
        f, axarr = self.setup_figure()
        rows, cols = self.dims/2, 2

        # Loop over every dimension vs every other dimension
        for ii,jj in itt.product(range(rows),range(cols)):
            inv = False
            cdim = ii*2 + jj
            print("Plotting dimension {}".format(cdim+1))

            # It's too messy to plot the spines and ticks for large dimensions
            for kw in ['top', 'right']:
                axarr[ii,jj].spines[kw].set_visible(False)
            axarr[ii,jj].tick_params(left=False, bottom=False)
        
            # Set the names 
            axarr[ii,jj].set_ylabel(self.names[cdim], fontsize=6)
            if ii == ((self.dims/2)-1):
                # set y label
                axarr[ii,jj].set_xlabel("WE Iterations", fontsize=6)

            # First pull a file that contains the dimension
            datFile = self.open_pdist_file(cdim+1)
            if (cdim+1) == self.dims:
                inv = True
     
            Hists = datFile['histograms'][:,:,:]
            if inv:
                Hists = Hists.mean(axis=1)
            else:
                Hists = Hists.mean(axis=2)

            moving_avg = []
            for starti in range(1, self.last_iter-self.avg_window):
                prob = Hists[starti:starti+self.avg_window].mean(axis=0)
                prob = prob/prob.sum()
                if not self.do_energy:
                    prob = prob/prob.max()
                moving_avg.append(prob)
            Hists = np.array(moving_avg)
            if self.do_energy:
                Hists = -np.log(Hists)
                Hists = Hists - Hists.min()

            # Calculate the x values, normalize s.t. it spans 0-1
            x_bins = datFile['binbounds_0'][...]
            x_max = x_bins.max()
            x_bins = x_bins/x_max
          
            # Plot on the correct ax, set x limit
            axarr[ii,jj].set_ylim(0.0, 1.0)
            cmap = mpl.cm.magma_r
            cmap.set_bad(color='white')
            cmap.set_over(color='white')
            cmap.set_under(color='white')

            pcolormesh = axarr[ii,jj].pcolormesh(
                                    range(0, self.last_iter-self.avg_window), 
                                    x_bins, 
                                    Hists.T, cmap=cmap, vmin=1e-60)
        
        self.save_fig()
        return

if __name__ == "__main__":
    # Get the regular plot
    ep = evoPlotter()
    ep.plot()
