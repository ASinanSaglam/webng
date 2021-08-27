import IPython
import pickle, csn, h5py, sys
import numpy as np
import networkx as nx
import pyemma as pe

tm_file = sys.argv[1]
assign_file = sys.argv[2]
pcca_cluster_count = sys.argv[3]

tm = np.load(tm_file)
zt = np.where(tm.sum(axis=1) == 0)
ind = np.where(tm.sum(axis=1) != 0)[0]
np.save("halton_inds.npy", ind)
tm = tm[..., ind][ind, ...]
# tm = (tm + tm.T)/2.0
# print("tm loaded")
# print(tm)
# print((tm < 0).any())
def row_normalize(mat):
    for irow, row in enumerate(mat):
        if row.sum() != 0:
            mat[irow] /= row.sum()


row_normalize(tm)
# IPython.embed()
# print("row normalized tm")
# print(tm)
# print((tm < 0).any())
# mcsn = csn.CSN(tm, symmetrize=True)
# rtm = mcsn.transmat.toarray()
# print("symm tm")
# print(tm)
# print((tm < 0).any())
MSM = pe.msm.MSM(tm, reversible=True)
pcca = MSM.pcca(pcca_cluster_count)
p = pcca.coarse_grained_stationary_probability
ctm = pcca.coarse_grained_transition_matrix
print(ctm.sum(axis=1))
# print("MSM probs")
# print(p)
# print("MSM TM")
# print(ctm)
# print((ctm < 0).any())
metastab_ass = pcca.metastable_assignment
mstabs = []
li = 0
for i in zt[0]:
    mstabs += list(metastab_ass[li:i])
    # mstabs += [0]
    mstabs += [-1]
    li = i
mstabs += list(metastab_ass[li:])
mstabs = np.array(mstabs)
# print(metastab_ass, metastab_ass.shape)
f = open("metasble_assignments_halton_noind.pkl", "w")
pickle.dump(metastab_ass, f)
f.close()
f = open("metasble_assignments_halton.pkl", "w")
pickle.dump(mstabs, f)
f.close()

bin_labels = np.load("halton_centers.npy")
bin_labels = bin_labels[ind, ...]

print("metastab 0")
print(bin_labels[metastab_ass == 0].mean(axis=0))
print("metastab 1")
print(bin_labels[metastab_ass == 1].mean(axis=0))
print("metastab 2")
print(bin_labels[metastab_ass == 2].mean(axis=0))
print("metastab 3")
print(bin_labels[metastab_ass == 3].mean(axis=0))

# print(cents)
# print(bin_assignments)
# print(metastab_ass)
# print(bin_labels)
# IPython.embed()

print("hi/hi", "lo/hi", "hi/lo", "lo/lo")
state_labels = {1: "hi/hi", 2: "lo/hi", 3: "hi/lo", 0: "lo/lo"}
state_colors = {0: "#FF00FF", 2: "#0000FF", 3: "#FF0000", 1: "#000000"}
tm = pcca.transition_matrix
node_sizes = pcca.stationary_probability * 1000
edge_sizes = tm

G = nx.DiGraph()
for i in range(tm.shape[0]):
    # G.add_node(i, LabelGraphics={"text": state_labels[i], "fontSize": 40},
    if node_sizes[i] > 0:
        G.add_node(
            i,
            weight=float(node_sizes[i]),
            color=state_colors[metastab_ass[i]],
            LabelGraphics={"text": " "},  # )
            graphics={
                "type": "circle",
                "fill": state_colors[metastab_ass[i]],
                "w": node_sizes[i],
                "h": node_sizes[i],
            },
        )

for i in range(tm.shape[0]):
    for j in range(tm.shape[1]):
        if i != j:
            # G.add_edge(i, j, graphics={"type": "arc", "targetArrow": "none", "fill": edge_colors[i], "width":edge_sizes[i][j]})
            if edge_sizes[i][j] > 1e-2:
                # if edge_sizes[i][j] > 0:
                G.add_edge(
                    i,
                    j,
                    weight=float(edge_sizes[i][j]),
                    graphics={
                        "type": "arc",
                        "targetArrow": "none",
                        "fill": state_colors[metastab_ass[i]],
                    },
                )

nx.write_gml(G, "pcca_full_halton.gml")

tm = pcca.coarse_grained_transition_matrix
node_sizes = pcca.coarse_grained_stationary_probability * 1000
edge_sizes = tm
print("coarse tm")
print(edge_sizes)
print("coarse probs")
print(pcca.coarse_grained_stationary_probability)

G = nx.DiGraph()
for i in range(tm.shape[0]):
    # G.add_node(i, LabelGraphics={"text": state_labels[i], "fontSize": 40},
    if node_sizes[i] > 0:
        G.add_node(
            i,
            weight=float(node_sizes[i]),
            color=state_colors[i],
            LabelGraphics={"text": " "},  # )
            graphics={
                "type": "circle",
                "fill": state_colors[i],
                "w": node_sizes[i],
                "h": node_sizes[i],
            },
        )

for i in range(tm.shape[0]):
    for j in range(tm.shape[1]):
        if i != j:
            # G.add_edge(i, j, graphics={"type": "arc", "targetArrow": "none", "fill": edge_colors[i], "width":edge_sizes[i][j]})
            # if edge_sizes[i][j] > 1e-2:
            # if edge_sizes[i][j] > 0:
            if True:
                G.add_edge(
                    i,
                    j,
                    weight=abs(float(edge_sizes[i][j])),
                    graphics={
                        "type": "arc",
                        "targetArrow": "none",
                        "fill": state_colors[i],
                    },
                )

nx.write_gml(G, "pcca_coarse_halton.gml")
