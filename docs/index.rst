.. webng documentation master file, created by
   sphinx-quickstart on Wed Apr 28 15:12:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

webng - WE sampling of BNGL models
=================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

`BioNetgen (BNG) <http://bionetgen.org/>`_ is a modelling language for rule-based 
modelling of complex biological systems. `WESTPA <https://github.com/westpa/westpa>`_ is a
python package that implements the weighted ensemble sampling scheme which focuses compuational
power to sample rare events in stochastic simulations. Models written with BioNetGen langauge 
(BNGL) can be simulated as ODEs or can be simulated stochastically using stochastic simulation 
algorightm (SSA). This can lead to rare events which are hard to sample and WESTPA can help
sample these events. 

webng is a command line tool designed to simplify the installation of BNG and WESTPA while 
also providing a simplepipeline to get a WESTPA simulation setup of a model written in BNGL. 
The tool also includes some sample analyses that are specifically tailored for BNGL models. 

Installation
############

The suggested python distribution to use is the `Anaconda python distribution <https://www.anaconda.com/download/>`_.
After that is installed, you can install webng directly from PyPI using pip

.. code-block:: shell

   pip install webng

which will also install WESTPA and BioNetGen python libraries which means you only need to 
run this command and have your model to run a WESTPA simulation. 

Usage
#####

After installation complete you can test to see if it's properly installed with

.. code-block:: shell

   webng -h

if this command prints out help, the command line tool is installed.

In order to use the tool, you will need a YAML configuration file. This tool comes with a 
subcommand that can generate a template YAML config file for you with the command

.. code-block:: shell

   webng template -i mymodel.bngl -o mysim.yaml

this should write a sample configuraion file to :code:`mysim.yaml`. The section that's relevant
for the simulation setup should look something like this:

.. code-block:: yaml

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

you can change various aspects of the simulation setup in this file. Once you are ready, 
you can setup the actual WESTPA simulation with the command

.. code-block:: shell

   webng setup --opts mysim.yaml

this will create a folder that corresponds to :code:`sim_name` in :code:`mysim.yaml` file. 
You can now initialize the simulation with

.. code-block:: shell

   cd mymodel
   ./init.sh

if this command completes successfuly you are ready to run your WESTPA simulation. 
You can run the simulation using a single core with

.. code-block:: shell

   w_run --serial

or you can use multiple cores with the command

.. code-block:: shell

   w_run --n-workers X

where :code:`X` is the number of cores you want to use. In order to extend the simulation further you 
will have to edit :code:`west.cfg` file, please read `WESTPA tutorials <https://github.com/westpa/westpa/wiki/Tutorials>`_
to learn how to run and manage these simulations.

Analysis
########

You should also see an analysis section in the :code:`mysim.yaml` file you created which should 
look like this

.. code-block:: yaml
   :linenos:

   analyses:
      enabled: false
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
         work-path: /home/USER/webng/testing/test/analysis # the folder to run the analysis under
      evolution:
         avg_window: null # number of iterations to average for each point in the plot
         dimensions: null # you can limit the tool to the first N dimensions
         enabled: false # this needs to be set to true to run the analysis
         normalize: false # normalizes the distributions
         output: evolution.png # output file name 
         plot-energy: false # plots -ln of probabilies
         plot-opts: # various plotting options like font sizes and line width
            name-font-size: 12
         work-path: /home/USER/webng/testing/test/analysis # the folder to run the analysis under

In this file you can set various analysis options. :code:`average` will create a 
N by N set of plots where N is the number of observables you have in the BNG model 
after running the appropriate WESTPA tools. The results will be saved in the folder 
written under :code:`analyses/average/output` (by default it's :code:`average.png`). 
The plot will look like a matrix of plots where the diagonal contains 1D probability 
distributions of each observable and every off-diagonal will be a 2D probability heatmap 
of each pair of observables.

The analysis :code:`evolution` will make a probability distribution evolution plot for 
each observable so you can track the progress of your simulation.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
