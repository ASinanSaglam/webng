import h5py, IPython, pickle
import numpy as np


def find_origin(wlk_tpl, h):
    iiter, iwlk = wlk_tpl
    parent = h["iterations/iter_%08d" % iiter]["seg_index"]["parent_id"][iwlk]
    if iiter > 2:
        return find_origin((iiter - 1, parent), h)
    else:
        print(iiter - 1, parent)
        return (iiter - 1, parent)


# We want to get the full ensemble starting from one of the starting states
h = h5py.File("../west.h5", "r")
# First let's find a parent that survives
iiter, selected_parent = find_origin((950, 0), h)
# Now find every path coming out of it for 10 iterations
paths = {}
paths[1] = {}
paths[1][selected_parent] = h["iterations/iter_%08d" % 1]["pcoord"][selected_parent]
selected_parents = [selected_parent]
for i in range(2, 101):
    print("Doing iteration %i" % i)
    paths[i] = {}
    ps = h["iterations/iter_%08d" % i]["seg_index"]["parent_id"][...]
    comp = ps == selected_parents[0]
    if len(selected_parents) > 1:
        for par in selected_parents[1:]:
            comp = np.logical_or(comp, ps == par)
    walks = np.where(comp)[0]
    print(walks)
    for j in walks:
        # paths[i][j] = h['iterations/iter_%08d'%i]['pcoord'][j][:,:]
        paths[i][j] = h["iterations/iter_%08d" % i]["pcoord"][j][[0, 3, 6, 9], :]
    selected_parents = walks
f = open("sample_paths.pkl", "w")
pickle.dump(paths, f)
f.close()
