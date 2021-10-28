import os, sys, h5py, argparse, pickle
import scipy.ndimage
import subprocess as sbpc
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import itertools as itt
import assignment as asgn
import voronoi_plot as vp
from sklearn.decomposition import PCA

# Hacky way to disable warnings so we can focus on important stuff
import warnings

warnings.filterwarnings("ignore")


class WEPCAer:
    def __init__(self):
        # Let's parse cmdline arguments
        self._parse_args()
        # Once the arguments are parsed, do a few prep steps, opening h5file
        self.h5file_path = self.args.h5file_path
        self.h5file = h5py.File(self.args.h5file_path, "r")
        # We can determine an iteration to pull the mapper from ourselves
        self._get_mapper(self.args.mapper_iter)
        # Set the dimensionality
        self._set_dims(self.args.dims)
        # Set names if we have them
        self._set_names(self.args.names)
        # Set work path
        self.work_path = self.args.work_path
        # iterations
        self.iiter, self.fiter = self._set_iter_range(self.args.iiter, self.args.fiter)
        # output name
        self.outname = self.args.outname
        # data smoothing
        self.data_smoothing_level = self.args.data_smoothing
        # Plotting energies or not?
        self.do_energy = self.args.do_energy

    def _parse_args(self):
        parser = argparse.ArgumentParser()

        # Data input options
        parser.add_argument(
            "-W",
            "--westh5",
            dest="h5file_path",
            default="west.h5",
            help="Path to the WESTPA h5 file",
            type=str,
        )

        parser.add_argument(
            "--mapper-iter",
            dest="mapper_iter",
            default=None,
            help="Iteration to pull the bin mapper from",
            type=int,
        )

        parser.add_argument(
            "--work-path",
            dest="work_path",
            default=os.getcwd(),
            help="Path to do our work in, save figs, the pdist files etc.",
            type=str,
        )

        parser.add_argument(
            "--name-file",
            dest="names",
            default=None,
            help="Text file containing the names of each dimension separated by spaces",
            type=str,
        )

        parser.add_argument(
            "--first-iter",
            default=None,
            dest="iiter",
            help="Plot data starting at iteration FIRST_ITER. "
            "By default, plot data starting at the first "
            "iteration in the specified w_pdist file. ",
            type=int,
        )

        parser.add_argument(
            "--last-iter",
            default=None,
            dest="fiter",
            help="Plot data up to and including iteration "
            "LAST_ITER. By default, plot data up to and "
            "including the last iteration in the specified ",
            type=int,
        )

        # TODO Support a list of dimensions instead
        parser.add_argument(
            "--dimensions",
            default=None,
            dest="dims",
            help="Number of dimensions to plot, at the moment a"
            "list of dimensions is not supported",
            type=int,
        )

        parser.add_argument(
            "-o",
            "--outname",
            default=None,
            dest="outname",
            help="Name of the output file, extension determines the format",
            type=str,
        )

        parser.add_argument(
            "--do-energy",
            dest="do_energy",
            action="store_true",
            default=False,
            help="Plot -lnP instead of probabilities",
        )

        parser.add_argument(
            "--smooth-data",
            default=None,
            dest="data_smoothing",
            help="Smooth data (plotted as histogram or contour"
            " levels) using a gaussian filter with sigma="
            "DATA_SMOOTHING_LEVEL.",
            type=float,
        )

        self.args = parser.parse_args()

    def _get_mapper(self, mapper_iter):
        # Gotta fix this behavior
        if mapper_iter is None:
            mapper_iter = self.h5file.attrs["west_current_iteration"] - 1
        # Load in mapper from the iteration given/found
        print(
            "Loading file {}, mapper from iteration {}".format(
                self.args.h5file_path, mapper_iter
            )
        )
        # We have to rewrite this behavior to always have A mapper from somewhere
        # and warn the user appropriately, atm this is very shaky
        try:
            self.mapper = asgn.load_mapper(self.h5file, mapper_iter)
        except:
            self.mapper = asgn.load_mapper(self.h5file, mapper_iter - 1)

    def _set_dims(self, dims=None):
        if dims is None:
            dims = self.h5file["iterations/iter_{:08d}".format(1)]["pcoord"].shape[2]
        self.dims = dims
        # return the dimensionality if we need to
        return self.dims

    def _set_names(self, name_file):
        print("Loading names from file {}".format(name_file))
        if name_file is not None:
            f = open(name_file, "r")
            n = f.readline()
            f.close()
            names = n.split()
            self.names = dict(zip(range(len(names)), names))
        else:
            # We know the dimensionality, can assume a
            # naming scheme if we don't have one
            print("Giving default names to each dimension")
            self.names = dict((i, str(i)) for i in range(self.dims))

    def _set_iter_range(self, iiter, fiter):
        if iiter is None:
            iiter = 0
        if fiter is None:
            fiter = self.h5file.attrs["west_current_iteration"] - 1

        return iiter, fiter

    def _calc_row_cols(self):
        num_figs = int(((self.dims * self.dims) - self.dims) / 2)
        sq = int(np.ceil(np.sqrt(num_figs)))
        num_cols, num_rows = int(np.ceil(num_figs / float(sq))), sq
        return num_rows, num_cols

    def setup_figure(self):
        # Setup the figure and names for each dimension
        plt.figure(figsize=(1.5, 1.5))
        r, c = self._calc_row_cols()
        f, axarr = plt.subplots(r, c)
        f.subplots_adjust(
            hspace=0.4, wspace=0.4, bottom=0.05, left=0.05, top=0.97, right=0.98
        )
        if r == 1:
            axarr = np.array([axarr])
            if c == 1:
                axarr = np.array([axarr])
        return f, axarr

    def save_fig(self, dims=None):
        # setup our output filename
        if self.outname is not None:
            outname = self.outname
        else:
            outname = "PCA_{:05d}_{:05d}.png".format(self.iiter, self.fiter)

        # save the figure
        print("Saving figure to {}".format(outname))
        plt.savefig(outname, dpi=600)
        plt.close()
        return

    def collect_data(self):
        all_pcoords = None
        all_weights = None
        for it in range(self.iiter, self.fiter):
            weights = self.h5file["iterations/iter_{:08d}".format(it + 1)]["seg_index"][
                "weight"
            ][...]

            # Not sure about the best way to PCA a WE simulation
            # at the moment I'll be pulling a single data point per iteration
            pcoord = self.h5file["iterations/iter_{:08d}".format(it + 1)]["pcoord"][
                :, -1, :
            ]
            a, c = pcoord.shape[0], pcoord.shape[1]

            # Uncomment if you want all pcoords
            # pcoord = h['iterations/iter_%08d'%it]['pcoord'][:,:,:]
            # a,b,c = pcoord.shape[0], pcoord.shape[1], pcoord.shape[2]

            if all_pcoords is None:
                all_pcoords = pcoord.reshape((a, c))
                # Uncomment if you want all pcoords
                # all_pcoords = pcoord.reshape((a*b,c))
            else:
                all_pcoords = np.vstack((all_pcoords, pcoord.reshape((a, c))))
                # Uncomment if you want all pcoords
                # all_pcoords = np.vstack((all_pcoords,pcoord.reshape((a*b,c))))
            if all_weights is None:
                all_weights = weights
            else:
                all_weights = np.append(all_weights, weights)

        self.working_pcoords = all_pcoords
        self.working_weights = all_weights
        return

    def preprocess_data(self):
        # Take weighted avg and weighted stds for prepping the pcoords
        wavg = np.average(self.working_pcoords, weights=self.working_weights, axis=0)
        self.working_pcoords = self.working_pcoords - wavg
        wavg = np.average(self.working_pcoords, weights=self.working_weights, axis=0)
        wstd = np.average(
            (self.working_pcoords - wavg) ** 2, weights=self.working_weights, axis=0
        )
        self.working_pcoords = self.working_pcoords / wstd
        return

    def cluster(self):
        self.pcaer = PCA()
        self.pcaer.fit(self.working_pcoords)
        self.components = self.pcaer.components_
        print("PCA components were: ")
        print(self.components)
        return

    def get_test_data(self, numpts=10000):
        # Get random indices
        n_samples = self.working_pcoords.shape[0]
        test_inds = np.random.randint(0, high=n_samples, size=numpts)
        self.test_inds = test_inds

        # Pull in random samples
        test_data = self.working_pcoords[test_inds, :]
        self.test_weights = self.working_weights[test_inds]
        # Get transformed samples
        self.test_data = self.pcaer.transform(test_data)
        return

    def plot_all(self):
        # Get figure
        f, axarr = self.setup_figure()
        r, c = self._calc_row_cols()
        print("figure has {} rows and {} cols".format(r, c))

        # Setup the color map
        cmap = mpl.cm.magma_r
        cmap.set_bad(color="white")
        cmap.set_over(color="white")
        cmap.set_under(color="white")

        # just to simplify code a bit
        ts = self.test_data
        tw = self.test_weights

        ctr = 0
        for i in range(self.dims):
            for j in range(i, self.dims):
                if i != j:
                    # Get the histogram
                    # TODO: Expose bin count to the command line
                    H, xedges, yedges = np.histogram2d(
                        ts[:, i], ts[:, j], bins=50, weights=tw
                    )
                    H = H / H.sum()
                    if self.data_smoothing_level is not None:
                        H = scipy.ndimage.filters.gaussian_filter(
                            H, self.data_smoothing_level
                        )
                    if self.do_energy:
                        H = -np.log(H)
                        H = H - H.min()

                    # Plot Histogram
                    X, Y = np.meshgrid(xedges, yedges)
                    # figure out the fig indices
                    fi, fj = ctr / c, ctr % c
                    ctr += 1
                    axarr[fi, fj].set(adjustable="box")
                    axarr[fi, fj].set_title(
                        "{} vs {}".format(i, j),
                        fontdict={"fontsize": 6, "verticalalignment": "top"},
                    )
                    axarr[fi, fj].pcolormesh(X, Y, H, cmap=cmap, vmin=1e-10)

                    # Set some stuff up
                    # plt.xlabel("PC #{}".format(i))
                    # plt.ylabel("PC #{}".format(j))
        for i in range(0, c):
            plt.setp([a.get_yticklabels() for a in axarr[:, i]], visible=False)
        for i in range(0, r):
            plt.setp([a.get_xticklabels() for a in axarr[i, :]], visible=False)

        # Save figure
        self.save_fig()
        return

    def run(self):
        self.collect_data()
        self.preprocess_data()
        self.cluster()
        self.get_test_data()
        self.plot_all()


if __name__ == "__main__":
    pcaer = WEPCAer()
    pcaer.run()
