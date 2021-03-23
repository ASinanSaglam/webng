# Anything that uses bin mapper will need the system.py to be in the folder
if [ ! -e system.py ];then
  cp ../system.py .
fi
if [ ! -e west.h5 ];then
  ln -s ../west.h5 .
fi

# First check the probability distributions
echo "### Plotting every prob dist ###"
python highdimplotter.py -W west.h5 --name-file full_names.txt -o pdists.png --smooth-data 0.5

# Check steady state for each dimension
echo "### Plotting prob dist evolutions ###"
python evoPlotter.py -W west.h5 --name-file full_names.txt -o evolution.png

# Do a PCA to figure out the number of states
#echo "### Doing PCA ###"
#python PCAer.py -W west.h5 --name-file full_names.txt

# now let's do PCCA+ and get some states
## assignment first, need to assign to original voronoi bins
echo "### Assigning to voronoi bins ###"
w_assign -W west.h5 --states-from-file states.yaml -o assign_voronoi.h5 || exit 1
## then we need to calculate transition matrix
echo "### Making the transition matrix ###"
w_reweight init -W west.h5 -a assign_voronoi.h5 -o tmat.h5 || exit 1
## use PCCA+ to get the coarse grained system
echo "### Doing PCCA+ ###"
COUNT=$1
python clusterer.py -TM tmat.h5 -A assign_voronoi.h5 --pcca-count $COUNT --name-file full_names.txt || exit 1
# Use the pcca to get GML files to plot networks
echo "### Making graphs ###"
python networker.py -PCCA pcca.pkl --mstab-file metasble_assignments.pkl --state-labels state_labels.txt
mv pcca_coarse.gml vor_coarse.gml
mv pcca_full.gml vor_full.gml

# Let's reanalyze with halton seq
echo "### Assigning to halton centers ###"
w_assign -W west.h5 --states-from-file states.yaml \
        --bins-from-function assignment.assign_halton -o assign_halton.h5 || exit 1
echo "### Making the transition matrix ###"
w_reweight init -W west.h5 -a assign_halton.h5 -o tmat_halton.h5 || exit 1
echo "### Doing PCCA+ ###"
python clusterer.py -TM tmat_halton.h5 -A assign_halton.h5 --mstab-file mstab_halton.pkl \
                    --pcca-count $COUNT --name-file full_names.txt --halton-centers halton_centers.npy || exit 1
echo "### Making graphs ###"
python networker.py -PCCA pcca.pkl --mstab-file mstab_halton.pkl --state-labels state_labels.txt 
mv pcca_coarse.gml halt_coarse.gml
mv pcca_full.gml halt_full.gml
