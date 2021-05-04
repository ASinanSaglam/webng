.. _config:

#####################
Configuration Options
#####################

Simulation setup options
========================

The section that's relevant for the simulation setup should look something like this:

.. code-block:: yaml
   :linenos:

   binning_options:
      block_size: 10 # Number of trajectories to be processed in blocks
      center_freq: 1 # How frequently do we add new Voronoi centers?
      max_centers: 300 # Maximum number of Voronoi centers to be added
      traj_per_bin: 100 # Number of trajectories per Voronoi center
   path_options: # this entire section should be automatically set by the tool
      WESTPA_path: /home/USER/westpa
      bng_path: /home/USER/apps/anaconda3/lib/python3.7/site-packages/bionetgen/bng-linux
      bngl_file: /home/USER/webng/testing/test.bngl
      sim_name: /home/USER/webng/testing/test # you can adjust sim folder here
   propagator_options:
      pcoords: # These should match observables in your model
      - Atot
      - Btot
      propagator_type: libRoadRunner # this is the suggested propagator
   sampling_options:
      dimensions: 2 # Dimensionality of the WESTPA progress coordinates
      max_iter: 10 # Maximum number of WE iterations
      pcoord_length: 10 # Number of data points per WE iteration
      tau: 100 # Resampling frequency

you can change various aspects of the simulation setup in this file. 
Let's look at each block separately. 

.. _binning:

Binning
-------

.. code-block:: yaml
   :linenos:

   binning_options:
      block_size: 10 # Number of trajectories to be processed in blocks
      center_freq: 1 # How frequently do we add new Voronoi centers?
      max_centers: 300 # Maximum number of Voronoi centers to be added
      traj_per_bin: 100 # Number of trajectories per Voronoi center

:code:`block_size` refers to how many trajectories will be ran at a time. This is important for
multicore runs, try to keep the blocksize an integer multiple of the number of cores you have. 
:code:`center_freq` refers to how frequently voronoi bins will be placed, in units of WE 
iterations. :code:`max_centers` is the maximum number of voronoi centers that will be placed.
Finally, :code:`traj_per_bin` is the number of trajectories in each voronoi center. 

.. _path_options:

Path Options
------------

.. code-block:: yaml
   :linenos:

   path_options: # this entire section should be automatically set by the tool
      WESTPA_path: /home/USER/westpa
      bng_path: /home/USER/apps/anaconda3/lib/python3.7/site-packages/bionetgen/bng-linux
      bngl_file: /home/USER/webng/testing/test.bngl
      sim_name: /home/USER/webng/testing/test # you can adjust sim folder here

Most of these option should be set automatically if WESTPA and BNG are both python importable. 
:code:`WESTPA_path` is the path to WESTPA to be used, :code:`bng_path` is the path where BNG2.pl 
lives. :code:`bngl_file` is the bngl model and :code:`sim_name` is the folder that will be used 
for the WESTPA setup. 

.. _propagator_options:

Propagator Options
------------------

.. code-block:: yaml
   :linenos:

   propagator_options:
      pcoords: # These should match observables in your model
      - Atot
      - Btot
      propagator_type: libRoadRunner # this is the suggested propagator

:code:`pcoords` is the list progress coordinates to be used for WESTPA and should match the 
observables in your BNGL model. :code:`propagator_type` is the type of propagator to be used. If 
available, use libRoadRunner since it's currently significantly more efficient for WESTPA runs. 
If not, you can select "executable" propagator which uses BNG2.pl in combination with bash scripts
for each walker. 

.. _propagator_options:

Sampling Options
------------------

.. code-block:: yaml
   :linenos:

   sampling_options:
      dimensions: 2 # Dimensionality of the WESTPA progress coordinates
      max_iter: 10 # Maximum number of WE iterations
      pcoord_length: 10 # Number of data points per WE iteration
      tau: 100 # Resampling frequency

:code:`dimensions` is the number of dimensions to be used for WESTPA progress coordinates and 
should match the number of BNGL observables you are using. :code:`max_iter` is the maximum number
of WE iterations to be ran (this can be changed later from within the setup). :code:`pcoord_length`
is the number of data points each walker will return. :code:`tau` is the length of each BNGL
simulation/walker. 

Analysis options
================

When you first create a setup configuration file like :code:`mysim.yaml`, you will see
an analysis section like this

.. code-block:: yaml
   :linenos:

   analyses:
      enabled: false
      work-path: /home/USER/webng/testing/test/analysis # the folder to run the analysis under
      average:
         dimensions: null # you can limit the tool to the first N dimensions
         enabled: false # this needs to be set to true to run the analysis 
         first-iter: null # first iteration to start the averaging
         last-iter: null # first iteration to end the averaging
         mapper-iter: null # the iteration to pull the voronoi bin mapper from, last iteration by default
         normalize: false # normalizes the distributions
         output: average.png # output file name 
         plot-energy: false # plots -ln of probabilies
         plot-opts: # various plotting options like font sizes and line width
            name-font-size: 12
            voronoi-col: 0.75
            voronoi-lw: 1
         plot-voronoi: false # true if you want to plot voronoi centers
         smoothing: 0.5 # the amount of smoothing to apply
      evolution:
         avg_window: null # number of iterations to average for each point in the plot
         dimensions: null # you can limit the tool to the first N dimensions
         enabled: false # this needs to be set to true to run the analysis
         normalize: false # normalizes the distributions
         output: evolution.png # output file name 
         plot-energy: false # plots -ln of probabilies
         plot-opts: # various plotting options like font sizes and line width
            name-font-size: 12

Let's take a look at individual sections. 

.. code-block:: yaml
   :linenos:

   analyses:
      enabled: false
      work-path: /home/USER/webng/testing/test/analysis # the folder to run the analysis under

This is upper level analysis block and has a single option called :code:`enabled`. If set to false,
none of the analyses will run. Each analysis subsection will have the same :code:`enabled` option
to set if that particular analysis will be ran or not. :code:`work-path` is the folder where all 
analysis will be ran. 

.. _average:

Average
-------

.. code-block:: yaml
   :linenos:

   average:
      dimensions: null # you can limit the tool to the first N dimensions
      enabled: false # this needs to be set to true to run the analysis 
      first-iter: null # first iteration to start the averaging
      last-iter: null # first iteration to end the averaging
      mapper-iter: null # the iteration to pull the voronoi bin mapper from, last iteration by default
      normalize: false # normalizes the distributions
      output: average.png # output file name 
      plot-energy: false # plots -ln of probabilies
      plot-opts: # various plotting options like font sizes and line width
         name-font-size: 12
         voronoi-col: 0.75
         voronoi-lw: 1
      plot-voronoi: false # true if you want to plot voronoi centers
      smoothing: 0.5 # the amount of smoothing to apply

This is the block for :ref:`Average analysis`. :code:`dimensions` is normally set to null which
makes the tool plot all dimensions. If this is set to :code:`N` the tool will plot the first 
:code:`N` dimensions. :code:`first-iter` and :code:`last-iter` are the iterations to start and 
stop the averaging. :code:`mapper-iter` is the iteration to pull the voronoi mapper from, if you 
don't want the mapper from the final WE iteration. :code:`normalize` can be used to enable 
normalization of probability distributions before plotting. :code:`output` is the file name 
for the output and this can be set to a :code:`png` or :code:`pdf` file. :code:`plot-energy` 
takes the :code:`-ln` of the probabilities before plotting. :code:`plot-voronoi` controls 
if the voronoi centers are plotted on top of the probability distributions. :code:`smoothing`
can be changed to reduce or increase the gaussian smoothing used for probability distributions. 
:code:`plot-opts` contain some options for plotting. :code:`name-front-size` is the font-size used
in plotting. :code:`voronoi-col` is the color to be used for voronoi bins and :code:`voronoi-lw` 
is the line width for the same lines. 

.. _evolution:

Evolution
---------

.. code-block:: yaml
   :linenos:

   evolution:
      avg_window: 1 # number of iterations to average for each point in the plot
      dimensions: null # you can limit the tool to the first N dimensions
      enabled: false # this needs to be set to true to run the analysis
      normalize: false # normalizes the distributions
      output: evolution.png # output file name 
      plot-energy: false # plots -ln of probabilies
      plot-opts: # various plotting options like font sizes and line width
         name-font-size: 12

This is the block for :ref:`Evolution analysis`. :code:`avg_window` the number of iterations to
average over for every data point. :code:`dimensions` is normally set to null which
makes the tool plot all dimensions. If this is set to :code:`N` the tool will plot the first 
:code:`N` dimensions. :code:`normalize` can be used to enable normalization of probability 
distributions before plotting. :code:`output` is the file name for the output and this can be 
set to a :code:`png` or :code:`pdf` file. :code:`plot-opts` contain some options for plotting. 
:code:`name-front-size` is the font-size used in plotting. 

.. _cluster:

Cluster
-------

.. code-block:: yaml
   :linenos:

   cluster:
      assignments: null
      cluster-count: 4
      enabled: true
      first-iter: null
      last-iter: null
      metastable-states-file: null
      normalize: null
      states:
      - coords:
         - - 20.0
         - 4.0
         label: a
      - coords:
         - - 4.0
         - 20.0
         label: b
      symmetrize: null
      transition-matrix: null

This is the block for :ref:`Cluster analysis`. :code:`assignments` is the assignment file to be
used for clustering. This can be pointed to a assignment file you generated using :code:`w_assign`
or, if left null, the tool will attempt to generate an assignment file itself. :code:`states`
is where you can define states for :code:`w_assign` if you want the tool to run it for you. 
:code:`cluster-count` is the number PCCA+ will try to cluster the data into. :code:`first-iter` 
and :code:`last-iter` are WE iterations to pull the data for clustering. 
:code:`metastable-states-file` is a python pickle file that contains a dictionary which defined 
which bin is assigned to which metastable state. :code:`normalize` makes it so that the output 
text is normalized to percentages. :code:`symmetrize` controls if the transition matrix is 
made symmetrical or not. :code:`transition-matrix` can point to a binary numpy file where you
give the tool a custom transition matrix or, if left null, the tool will generate one for you
using the assignment file. 

.. _network:

Network
-------

.. code-block:: yaml
   :linenos:

   network:
      enabled: true
      metastable-states-file: null
      pcca-pickle: null
      state-labels: null

This is the block for :ref:`Network generation`. :code:`metastable-states-file` is a python 
pickle file that contains a dictionary which defined which bin is assigned to which metastable 
state. :code:`pcca-pickle` is the python pickle object that the cluster analysis generates (or
you can use `pyGPCCA <https://github.com/msmdev/pyGPCCA>`_ to generate one yourself). 
:code:`state-labels` is the labels you want to use for each cluster generated by :ref:`Cluster`