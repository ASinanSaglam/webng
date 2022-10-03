import os, h5py, sys
import scipy.ndimage
import subprocess as sbpc
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import itertools as itt
import webng.analysis.utils as utils
from webng.analysis.analysis import weAnalysis

# Hacky way to disable warnings so we can focus on important stuff
import warnings

warnings.filterwarnings("ignore")

# TODO: Separate out the pdisting, use native code
# TODO: Hook into native code to decouple some parts like # of dimensions etc.
# we need the system.py anyway, let's use native code to read CFG file
class weAverage(weAnalysis):
    """
    Class for the averaging analysis.

    This tool creates a N by N matrix-like plot where N is the number of observables
    in the BNGL tool (unless overridden by the `dimensions` option). The diagonal
    will contain 1D probability distributions and off diagonals will contain 2D probability
    heatmaps of each dimension vs each other dimension.

    This tool uses `w_pdist` WESTPA tool to calculate probabilty distributions hence
    it needs `w_pdist` to be accessible directly from the commandline.
    """

    def __init__(self, opts):
        super().__init__(opts)
        # Once the arguments are parsed, do a few prep steps, opening h5file
        self.h5file_path = os.path.join(opts["sim_name"], "west.h5")
        self.h5file = h5py.File(self.h5file_path, "r")
        # We can determine an iteration to pull the mapper from ourselves
        self.get_mapper(opts["mapper-iter"])
        # Set the dimensionality
        self.set_dims(opts["dimensions"])
        # Voronoi or not
        self.voronoi = opts["plot-voronoi"]
        # Plotting energies or not?
        self.do_energy = opts["plot-energy"]
        # iterations
        self.first_iter, self.last_iter = self.set_iter_range(
            opts["first-iter"], opts["last-iter"]
        )
        # output name
        self.outname = opts["output"]
        # data smoothing
        self.data_smoothing_level = opts["smoothing"]
        # data normalization to min/max
        self.normalize = opts["normalize"]
        # get color bar option
        if "color_bar" in opts:
            self.color_bar = opts["color_bar"]
        else:
            self.color_bar = None

    def get_mapper(self, mapper_iter):
        # Gotta fix this behavior
        if mapper_iter is None:
            mapper_iter = self.h5file.attrs["west_current_iteration"] - 1
        # Load in mapper from the iteration given/found
        print(
            "Loading file {}, mapper from iteration {}".format(
                self.h5file_path, mapper_iter
            )
        )
        # We have to rewrite this behavior to always have A mapper from somewhere
        # and warn the user appropriately, atm this is very shaky
        try:
            self.mapper = utils.load_mapper(self.h5file, mapper_iter)
        except:
            self.mapper = utils.load_mapper(self.h5file, mapper_iter - 1)

    def set_dims(self, dims=None):
        if dims is None:
            dims = self.h5file["iterations/iter_{:08d}".format(1)]["pcoord"].shape[2]
        self.dims = dims
        # return the dimensionality if we need to
        return self.dims

    def set_names(self, names):
        if names is not None:
            self.names = dict(zip(range(len(names)), names))
        else:
            # We know the dimensionality, can assume a
            # naming scheme if we don't have one
            print("Giving default names to each dimension")
            self.names = dict((i, str(i)) for i in range(self.dims))

    def set_iter_range(self, first_iter, last_iter):
        if first_iter is None:
            first_iter = 0
        if last_iter is None:
            last_iter = self.h5file.attrs["west_current_iteration"] - 1

        return first_iter, last_iter

    def setup_figure(self):
        # Setup the figure and names for each dimension
        f = plt.figure(figsize=(5,5))
        # plt.figure(figsize=(1.5, 1.5))
        # f, axarr = plt.subplots(self.dims, self.dims)
        # f.subplots_adjust(
        #     hspace=0.4, wspace=0.4, bottom=0.05, left=0.05, top=0.98, right=0.9
        # )
        return f

    def save_fig(self):
        # setup our output filename
        if self.outname is not None:
            outname = self.outname
        else:
            outname = "all_{:05d}_{:05d}.png".format(self.first_iter, self.last_iter)

        # save the figure
        print("Saving figure to {}".format(outname))
        plt.savefig(outname, dpi=600)
        plt.close()
        return

    def open_pdist_file(self, fdim, sdim):
        # TODO: Rewrite so that it uses w_pdist directly and we can avoid using
        # --construct-dataset and remove the dependency on assignment.py here
        pfile = os.path.join(self.work_path, "pdist_{}_{}.h5".format(fdim, sdim))
        # for now let's just get it working
        try:
            if not os.path.isfile(pfile):
                raise IOError
            open_file = h5py.File(pfile, "r")
            return open_file
        except IOError:
            print(
                "Cannot open pdist file for {} vs {}, calling w_pdist".format(
                    fdim, sdim
                )
            )
            # We are assuming we don't have the file now
            # TODO: Expose # of bins somewhere, this is REALLY hacky,
            # I need to fiddle with w_pdist to fix it up

            # we need to have assignment.py for w_pdist to work
            # TODO: Try to make it use utils.pull data instead
            with open("assignment.py", "w") as f:
                f.write(self.pull_data_str)

            with open("data_to_pull.txt", "w") as f:
                f.write("{} {}".format(fdim, sdim))

            proc = sbpc.Popen(
                [
                    "w_pdist",
                    "-W",
                    "{}".format(self.h5file_path),
                    "-o",
                    "{}".format(pfile),
                    "-b",
                    "[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,50],[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,50]]",
                    "--construct-dataset",
                    "assignment.pull_data",
                ]
            )
            proc.wait()
            assert proc.returncode == 0, "w_pdist call failed, exiting"
            open_file = h5py.File(pfile, "r")
            return open_file

    def run(self, ext=None):
        first_iter, last_iter = self.first_iter, self.last_iter
        if "plot-opts" in self.opts:
            plot_opts = self.opts["plot-opts"]
            name_fsize = self._getd(plot_opts, "name-font-size", default=6)
            vor_lw = self._getd(plot_opts, "voronoi-lw", default=0.15)
            vor_col = self._getd(plot_opts, "voronoi-col", default=0.75)
            vor_col = str(vor_col)

        f = self.setup_figure()
        ax = f.gca()
        # Loop over every dimension vs every other dimension
        # Set the names if we are there
        # set x label
        ax.set_xlabel("A", fontsize=name_fsize)
        # set y label
        ax.set_ylabel("B", fontsize=name_fsize)

        # Set equal widht height
        if self.normalize:
            ax.set(adjustable="box", aspect="equal")
        # Plotting off-diagonal, plotting 2D heatmaps
        datFile = self.open_pdist_file(1, 2)
        inv = False

        # Get average histograms over iterations,
        # take -ln of the histogram after normalizing
        # and set minimum to 0
        Hists = datFile["histograms"][first_iter:last_iter]
        Hists = Hists.mean(axis=0)
        Hists = Hists / (Hists.sum())
        # Hists = -np.log(Hists)
        # Hists = Hists - Hists.min()
        # Let's remove the nans and smooth
        Hists[np.isnan(Hists)] = np.nanmax(Hists)
        if self.do_energy:
            Hists = -np.log(Hists)
        # Hists = Hists/Hists.max()
        if self.data_smoothing_level is not None:
            Hists = scipy.ndimage.filters.gaussian_filter(
                Hists, self.data_smoothing_level
            )
        # pcolormesh takes in transposed matrices to get
        # the expected orientation
        e_dist = Hists.T

        # Get x/y bins, normalize them to 1 max
        x_bins = datFile["binbounds_0"][...]
        x_max = x_bins.max()
        if self.normalize:
            if x_max != 0:
                x_bins = x_bins / x_max
        y_bins = datFile["binbounds_1"][...]
        y_max = y_bins.max()
        if self.normalize:
            if y_max != 0:
                y_bins = y_bins / y_max

        # If we are at the other side of the diagonal line
        if not inv:
            e_dist = e_dist.T
            x_bins, y_bins = y_bins, x_bins

        # Set certain values to white to avoid distractions
        cmap = mpl.cm.magma_r
        cmap.set_bad(color="white")
        cmap.set_over(color="white")
        cmap.set_under(color="white")

        # Set x/y limits
        if self.normalize:
            ax.set_xlim(0.0, 1.0)
            ax.set_ylim(0.0, 1.0)
        else:
            ax.set_xlim(0.0, 30.0)
            ax.set_ylim(0.0, 30.0)

        # Plot the heatmap
        pcolormesh = ax.pcolormesh(
            x_bins, y_bins, e_dist, cmap=cmap, vmin=1e-10
        )

        f.colorbar(
            pcolormesh,
            ax=ax,
            label="probability"
        )
        
        # label states
        import pickle
        with open("/home/boltzmann/webng_work/webng/stest/exmisa/analysis/metasble_assignments.pkl", "rb") as f:
            mstabs = pickle.load(f)
        colors = ["#FFFFFF","#0000FF","#FF0000","#000000"]
        for i in range(0,30):
            for j in range(0,30):
                cell = self.mapper.assign([[i,j]])[0]
                state = mstabs[cell]
                ax.plot(i,j,c=colors[state],lw=0,markersize=2,marker="o")
        self.save_fig()
        return

if __name__ == "__main__":
    import yaml
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
    with open("/home/boltzmann/webng_work/webng/stest/opts.yaml", "r") as f:
            opt_dict = yaml.load(f, Loader=Loader)
    print("running analysis: average")
    # enabled, run
    analysis_dict = opt_dict["analyses"]
    avg_dict = analysis_dict["average"]
    avg_dict["pcoords"] = opt_dict["propagator_options"]["pcoords"]
    avg_dict["sim_name"] = opt_dict["path_options"]["sim_name"]
    avg_dict["output"]  = "/home/boltzmann/webng_work/webng/stest/exmisa/analysis/avg_label.png"
    avg_dict["work-path"] = "/home/boltzmann/webng_work/webng/stest/exmisa/analysis"
    weAverage(avg_dict).run()