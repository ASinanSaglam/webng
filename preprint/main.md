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

Outline
=======

1. What is a BNG model?
2. What is WE and WESTPA?
3. Why do we want to use both?
4. What does WEBNG do? 
5. How to use WEBNG?

Models of biochemical systems can get complicated, resulting in a large number of chemical species. Frequently these models result in combinatorial complexity when species have multiple states that they can be in. A rule-based modelling approach was developed to avoid manually enumerating every possible species. Rule-based models define rules which specify how species can interact and all possible reactions and species are generated off of these rules. BioNetGen (BNG) is an open-source rule-based modelling software package that allows for model construction in BioNetGen language (BNGL) and simulation.



Rule-based modeling is an approach for addressing combinatorial complexity in models of biochemical systems (Chylek et al., 2014, 2015). Instead of manually enumerating all possible species and reactions that can exist within a system, a rule-based model defines only the reactive motifs within macromolecular complexes and the interactions and modifications that involve those motifs. BioNetGen is an open-source software package for constructing and simulating rule-based models (Blinov et al., 2004; Faeder et al., 2009). It has been used to model a variety of biological processes, including cell signaling, gene regulation and metabolism (Chylek et al., 2014, 2015, and references therein; see also bionetgen.org/index.php/Model_Examples). Models are written in a human-readable, textbased modeling language known as BNGL (BioNetGen language). 

Numerous user-specified actions can be added to a BNGL model file, including generating a reaction network and performing deterministic or stochastic simulations. Models can also be exported to different formats, such as SBML (Hucka et al., 2003) and MATLAB language (The MathWorks Inc., Natick, MA). Furthermore, BioNetGen interfaces with NFsim (Sneddon et al., 2011), a ‘network-free’ simulator that avoids enumeration of species and reactions, which may be intractable for large models. 