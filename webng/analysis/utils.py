import numpy as np
import pickle, sys
import matplotlib
import matplotlib.pyplot as plt
from westpa.core.binning import NopMapper

index_dtype = np.uint16


class wrapped_clusterer(NopMapper):
    def __init__(self, clusterer):
        super(NopMapper, self).__init__()
        self.predictor = clusterer
        self.labels = [0, 1, 2, 3]
        self.nbins = 4

    def assign(self, coords, mask=None, output=None):
        assigned = np.array(self.predictor.predict(coords), dtype=index_dtype)
        try:
            output[...] = assigned[...]
        except:
            pass

        return assigned


def pull_data(n_iter, iter_group):
    """
    This function reshapes the progress coordinate and
    auxiliary data for each iteration and retuns it to
    the tool.
    """
    data_to_pull = np.loadtxt("data_to_pull.txt") - 1
    d1, d2 = data_to_pull
    pcoord = iter_group["pcoord"][:, :, [d1, d2]]

    data = pcoord

    return data


def pull_all_data(n_iter, iter_group):
    """
    This function reshapes the progress coordinate and
    auxiliary data for each iteration and retuns it to
    the tool.
    """
    pcoord = iter_group["pcoord"][:, :, :]

    data = pcoord

    return data


def avg(hist, midpoints, binbounds):

    # First we are going to import the pyplot library
    # to get access to the matplotlib object so we can
    # further modify it.
    import matplotlib.pyplot as plt

    # Now we are going to change the title, add axis labels
    plt.xlabel("Protein A concentration")
    plt.ylabel("Protein B concentration")
    plt.xlim((0, 30))
    plt.ylim((0, 30))


def assign_cluster():
    print("making the wrapped clusterer")
    WClusterer = wrapped_clusterer(clusterer)
    return WClusterer


def load_mapper(h, iter_no):
    import pickle

    topol_grp = h["bin_topologies"]
    hashval = h["iterations/iter_{:08d}".format(iter_no)].attrs["binhash"]
    hashval = bytes(hashval, "utf-8")
    index = topol_grp["index"]
    pickles = topol_grp["pickles"]
    n_entries = len(index)

    chunksize = 256
    istart = iter_no - 1
    for istart in range(0, n_entries, chunksize):
        chunk = index[istart : min(istart + chunksize, n_entries)]
        for i in range(len(chunk)):
            if chunk[i]["hash"] == hashval:
                pkldat = bytes(pickles[istart + i, 0 : chunk[i]["pickle_len"]].data)
                mapper = pickle.loads(pkldat)
    return mapper


def assign_voronoi():
    print("Pulling the latest bin mapper")
    import h5py

    h = h5py.File("west.h5", "r")
    i = h.attrs["west_current_iteration"] - 1
    mapper = load_mapper(h, i)
    return mapper


def assign_pcca():
    print("making the wrapped clusterer")
    import h5py

    h = h5py.File("west.h5", "r")
    i = h.attrs["west_current_iteration"] - 1
    mapper = load_mapper(h, i)
    WClusterer = wrapped_mapper(mapper)
    WClusterer.load_pcca_labels(
        "/home/monoid/PROJECTS/PLURI_12GENE/001/analysis/metasble_assignments.pkl"
    )
    return WClusterer


# def assign_halton():
#     import matplotlib.pyplot as plt
#     import ghalton as gh
#     print("getting halton centers")
#     import h5py
#     h = h5py.File('west.h5','r')
#     i = h.attrs['west_current_iteration']
#     mapper = load_mapper(h, i)
#     seq = gh.Halton(mapper.centers.shape[1])
#     s = np.array(seq.get(mapper.centers.shape[0]))
#     for i in range(mapper.centers.shape[1]):
#         s[:,i] = s[:,i] * (mapper.centers[:,i].max())
#     np.save("halton_centers.npy", s)
#     # done plotting
#     mapper.centers = s
#     return mapper


class wrapped_mapper(NopMapper):
    def __init__(self, mapper):
        super(NopMapper, self).__init__()
        self.underlying_mapper = mapper
        self.labels = mapper.labels
        self.nbins = mapper.nbins

    def load_pcca_labels(self, label_file):
        f = open(label_file, "r")
        self.pcca_labels = np.array([0] + list(pickle.load(f)))
        f.close()

    def assign(self, coords, mask=None, output=None):
        # print("In .assign")
        # print("coordinates")
        # print(coords, coords.shape)

        assigned = self.underlying_mapper.assign(coords)
        # print("shape of coords to remap")
        # print(assigned.shape)
        remapped = np.array(map(lambda x: self.pcca_labels[x], assigned))
        try:
            output[...] = remapped[...]
            # print(output, output.shape)
        except:
            pass
        # print("assigned")
        # print(assigned, assigned.shape)

        return remapped


def pull_weight(n_iter, iter_group):
    """
    Custom weight puller for a custom version of w_pdist.
    This will probably eventually make it into the main repo
    """
    # import sys, h5py
    # import numpy as np
    #
    ## Let's pull in the parent we want
    # parent = np.loadtxt('parent_to_track.txt')
    # parent_file = h5py.File('root_parents.h5', 'r')
    # parents = parent_file['iter_%08d/parents'%n_iter]
    # weights_to_get = (parents == parent)
    ## Get the weights
    # weights = iter_group['seg_index']['weight'][...]
    ## everything else is 0
    # data = np.zeros(weights.shape)
    # data[weights_to_get] = weights[weights_to_get]
    ## normalize
    # data = data/sum(data)
    return iter_group["seg_index"]["weight"][...]


# Next two functions by:
# Voronoi diagram from a list of points
# Copyright (C) 2011  Nicolas P. Rougier


def circumcircle(P1, P2, P3):
    """
    Used for plotting voronoi center in `average` analysis.

    Adapted from:
    http://local.wasp.uwa.edu.au/~pbourke/geometry/circlefrom3/Circle.cpp
    """
    delta_a = P2 - P1
    delta_b = P3 - P2
    if np.abs(delta_a[0]) <= 0.000000001 and np.abs(delta_b[1]) <= 0.000000001:
        center_x = 0.5 * (P2[0] + P3[0])
        center_y = 0.5 * (P1[1] + P2[1])
    else:
        aSlope = delta_a[1] / delta_a[0]
        bSlope = delta_b[1] / delta_b[0]

        if aSlope == 0.0:
            aSlope = 1e-6

        if bSlope == 0.0:
            bSlope = 1e-6

        if np.isinf(aSlope):
            aSlope = 1e6

        if np.isinf(bSlope):
            bSlope = 1e6

        if np.abs(aSlope - bSlope) <= 0.000000001:
            return None
        center_x = (
            aSlope * bSlope * (P1[1] - P3[1])
            + bSlope * (P1[0] + P2[0])
            - aSlope * (P2[0] + P3[0])
        ) / (2 * (bSlope - aSlope))
        center_y = -1 * (center_x - (P1[0] + P2[0]) / 2) / aSlope + (P1[1] + P2[1]) / 2
    return center_x, center_y


def voronoi(X, Y):
    """
    Used for plotting voronoi center in `average` analysis.
    """
    P = np.zeros((X.size + 4, 2))
    P[: X.size, 0], P[: Y.size, 1] = X, Y
    # We add four points at "infinity"
    m = max(np.abs(X).max(), np.abs(Y).max()) * 1e5
    P[X.size :, 0] = [-m, -m, +m, +m]
    P[Y.size :, 1] = [-m, +m, -m, +m]
    D = matplotlib.tri.Triangulation(P[:, 0], P[:, 1])
    T = D.triangles
    n = T.shape[0]
    C = np.zeros((n, 2))
    for i in range(n):
        C[i] = circumcircle(P[T[i, 0]], P[T[i, 1]], P[T[i, 2]])
    X, Y = C[:, 0], C[:, 1]
    segments = []
    for i in range(n):
        for j in range(3):
            k = D.neighbors[i][j]
            if k != -1:
                segments.append([(X[i], Y[i]), (X[k], Y[k])])
    return segments
