---
from: markdown+yaml_metadata_block+tex_math_dollars+raw_tex
to: latex
output:
  pdf_document: 
    latex_engine: xelatex
documentclass: article
title: Generating WESTPA templates of BioNetGen language models
# this is not working right now
metadata:
  author:
  - Ali Sinan Saglam
  - James R. Faeder
abstract: |
  WEBNG is a tool to simplify WESTPA simulations of BNGL models.
...


Introduction
============

Models of biochemical systems can get complicated, resulting in a large number of chemical species. Frequently these models result in combinatorial complexity when species have multiple states that they can be in. A rule-based modelling approach was developed to avoid manually enumerating every possible species and reactions. Rule-based models define rules which specify how species can interact and all possible reactions and species are generated off of these rules. BioNetGen (BNG) is an open-source rule-based modelling software package that allows for model construction in BioNetGen language (BNGL) and simulation of BNGL models.

Rare events in modelling are events that take a long time to occur compared to the time scale of the fastest proccess in the model. For some models, rare events are unavoidable because the fastest process in the system must be modelled for accuracy. This is frequently the case for biological models and while some modelling methods allow for simplification of the fastest process, it's generally ideal to model everything if possible. Models with rare events are also frequently hard to simulate because it takes many events to get a statistically robust estimate of any aspect of a biological process which means the simulations need to run for a long time to get enough rare events to occur. 

Tackling this problem has been a focus of the computational modelling field for a while and many rare event sampling methods have been developped. One of these methods is called weighted ensemble method. Weighted ensemble path sampling works by organizing multiple parallel trajectories, resampling them at a fixed time interval. Each trajectory is assigned a statistical weight that are tracked during WE resampling. This allows WE resampling scheme to keep model kinetics statistically rigorous while replicating trajectories making progress towards the rare event of interest and terminating trajectories that aren't. 

WESTPA is an open-source, scalable and interoperable softare package that applies the WE strategy. WESTPA has been successfully used to study multiple challanging biological processes and is being actively maintained. WESTPA is interoperable and is designed to interface with any stochastic simulator, which makes it ideal to use with BNG stochastic simulation methods. 

In bioinformatics modelling, researchers frequently avoid working with models that contains rare events because it is easier to coarse grain the fastest processes and keep the timescale separation in a model relatively small, reducing computational cost. However, this does come at the cost of accuracy and not being able to understand how the kinetics of the fast processes in a model affect the slow ones. Rare event sampling methods can alleviate this issue, allowing researchers to tackle more detailed, challenging models that contain rare events. 

To this end we have developped a templating tool named WEBNG that makes it easier to setup WESTPA simulations of a BNGL model. The user needs to supply parameters for a WESTPA simulation along with a BNGL model and the tool creates a WESTPA simulation folder which can then be ran like any other WESTPA simulation. The tool also comes with some analyses built-in and is designed to tackle high dimensional WE simulations which is common for BNG models. WEBNG tries to lower the entry barrier for bioinformatics researchers to use weighted ensemble rare event sampling method and explore more models where rare events occur without having to worry about the computational cost.

How to use WEBNG
================


Validation and efficiency
=========================


Conclusion and future directions
================================

WEBNG is a simple templating tool that bridges two open software packages, WESTPA and BioNetGen, and lowers the barrier to entry to weighted ensemble rare event sampling of rule-based models. WESTPA, BNG and WEBNG are all well documented which helps any potential researcher that wants to make BNG models that containt rare events to get a simple starting point. Using python package index as the distribution point not only makes installation simple but also allows for all three software packages to be kept up-to-date and in sync easily.

New analyses, better efficiency and simpler ways to generate templates are currently in development and as WESTPA and BNG packages get updated, WEBNG will be kept in sync with both software packages. More information on the documentation of WEBNG, WESTPA and BNG can be found in the supplementary information. 