# A weighted ensemble simulation setup tool for BioNetGen models


[![WEBNG build status](https://github.com/ASinanSaglam/webng/workflows/webng-main/badge.svg)](https://github.com/ASinanSaglam/webng/actions) [![WEBNG RTD documentation status](https://readthedocs.org/projects/webng/badge/?version=latest&style=plastic)](https://readthedocs.org/projects/webng/badge/?version=latest&style=plastic)

This is a command line tool to setup [WESTPA](https://github.com/westpa/westpa) simulations of [BioNetGen](http://bionetgen.org/) models. 

## Installation

The suggested python distribution is the [Anaconda python distribution](https://www.anaconda.com/download/). You can install the command line tool with

```
pip install webng
```

which should also install BioNetGen, WESTPA and all required packages for this command line tool. 

## Usage

After installation complete you can test to see if it's properly installed with

```
webng -h
```

if this command prints out help, the command line tool is installed.

In order to use the tool, you will need a YAML configuration file. This tool comes with a subcommand that can generate a template YAML config file for you with the command

```
webng template -i mymodel.bngl -o mysim.yaml
```

this should write a sample configuraion file to `mysim.yaml`. The section that's relevant for the simulation setup should look something like this

```
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
```

you can change various aspects of the simulation setup in this file. Once you are ready, you can setup the actual WESTPA simulation with the command

```
webng setup --opts mysim.yaml
```

this will create a folder that corresponds to `sim_name` in `mysim.yaml` file. You can now initialize the simulation with

```
cd mymodel
./init.sh
```

if this command completes successfuly you are ready to run your WESTPA simulation. You can run the simulation using a single core with

```
w_run --serial
```

or you can use multiple cores with the command

```
w_run --n-workers X
```

where X is the number of cores you want to use. In order to extend the simulation further you will have to edit `west.cfg` file, please read [WESTPA tutorials](https://github.com/westpa/westpa/wiki/Tutorials) to learn how to run these simulations.

## Analysis

You should also see an analysis section in the `mysim.yaml` file you created which should look like this

```
analyses:
  enabled: false
  average:
    dimensions: null
    enabled: false
    first-iter: null
    last-iter: null
    mapper-iter: null
    normalize: false
    output: average.png
    plot-energy: false
    plot-opts:
      name-font-size: 12
      voronoi-col: 0.75
      voronoi-lw: 1
    plot-voronoi: false
    smoothing: 0.5
    work-path: /home/USER/webng/testing/test/analysis
  evolution:
    avg_window: null
    dimensions: null
    enabled: false
    normalize: false
    output: evolution.png
    plot-energy: false
    plot-opts:
      name-font-size: 12
      voronoi-col: 0.75
      voronoi-lw: 1
    work-path: /home/USER/webng/testing/test/analysis
```

In this file you can set various analysis options. `average` will create a N by N set of plots where N is the number of observables you have in the BNG model after running the appropriate WESTPA tools. The results will be saved in the folder written under `analyses/average/output` (by default it's `average.png`). The plot will look like a matrix of plots where the diagonal contains 1D probability distributions of each observable and every off-diagonal will be a 2D probability heatmap of each pair of observables.

The analysis `evolution` will make a probability distribution evolution plot for each observable so you can track the progress of your simulation.

## Note

This repo is still heavily under construction, please let me know if you have any issues by reporting your issue under [github issues page](https://github.com/ASinanSaglam/webng/issues)
