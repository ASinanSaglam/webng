.. webng documentation master file, created by
   sphinx-quickstart on Wed Apr 28 15:12:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
WEBNG - WE sampling of BNGL models
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   config
   analysis

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

Please see :ref:`quickstart` page to learn how to use webng.

..  Warning::  This documentation is still a work in progress and is incomplete.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
