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

Tackling this problem has been a focus of the modelling field for a while and many rare event sampling methods have been developped. One of these methods is called weighted ensemble method. Weighted ensemble is... . WESTPA is a softare that implements weighted ensemble and is ... 

In bioinformatics modelling researchers frequently ignore rare events because it is easier to coarse grain the fastest processes and keep the timescale separation in a model relatively small, reducing computational cost. However, this does come at the cost of accuracy and not being able to understand how the kinetics of the fast processes in a model affect the slow ones. Rare even sampling methods can alleviate this issue to some extent, allowing researchers to tackle more models that contain rare events. 

To this end we have developped a templating tool named WEBNG that makes it easier to setup WESTPA simulations of a BNGL model. The user needs to supply WESTPA parameters along with a BNGL model and the tool creates a WESTPA simulation folder which can then be ran like any other WESTPA simulation. The tool also comes with some analyses built-in and is designed to tackle high dimensional WE simulations. WEBNG tries to lower the entry barrier for bioinformatics researchers to use weighted ensemble rare event sampling method and explore more models where rare events occur without having to worry about the computational cost.

How to use WEBNG
================

Validation and efficiency
=========================

Conclusion and future directions
================================