.. webng documentation master file, created by
   sphinx-quickstart on Wed Apr 28 15:12:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

webng: A command line tool for setting up WESTPA simulations of BioNetGen models
=================================

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

TODO: Links for SSA

This tool is designed to simplify the installation of BNG and WESTPA while also providing a simple
pipeline to get a WESTPA simulation setup of a model written in BNGL. 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
