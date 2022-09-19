---
from: markdown+yaml_metadata_block+tex_math_dollars+raw_tex
to: latex
bibliography: main.bib
output:
  pdf_document: 
    latex_engine: xelatex
documentclass: frontiersSCNS
title: Generating weighted ensemble templaets of BioNetGen language models
# this is not working right now
metadata:
  author:
  - Ali Sinan Saglam
  - James R. Faeder
abstract: |
  WEBNG is schnasty
...

Outline
=======

1. Let's try to see what works and what doesn't

These are my references [@chelliah2013biomodels,@olivier2004web].

![Here is an example image](simpleCellDesigner.pdf)

Some tex math

$$\begin{aligned}
\mathtt{0} & \rightarrow \mathtt{A} \hspace{1em} k_A^+  \\ 
\mathtt{B} & \rightarrow \mathtt{0}  \hspace{1em} k_B^-\\
\mathtt{A + B} & \rightarrow  \mathtt{A\_B} \hspace{1em} k_{AB}^+ \\
\mathtt{A\_B} & \rightarrow  \mathtt{A + B}  \hspace{1em} k_{AB}^-\\
\mathtt{C + A\_B} & \rightarrow  \mathtt{A\_B\_C} \hspace{1em} k_{ABC}^+\\
\mathtt{A\_B\_C} & \rightarrow  \mathtt{C + A\_B}  \hspace{1em} k_{ABC}^-\\
\mathtt{A\_B} & \rightarrow \mathtt{A\_P + B} \hspace{1em} k_{cat} \end{aligned}$$

This is a new line 

&nbsp;

And a table

    Reactant       Product     Interpretation        SCT Entry
  ------------- ------------- ---------------- ---------------------
    $\tt{0}$      $\tt{A}$       Synthesis           No entry
    $\tt{B}$      $\tt{0}$      Degradation          No entry
   $\tt{A, B}$   $\tt{A\_B}$         NA              No entry
   $\tt{A\_B}$   $\tt{A,B}$     Complexation    $\tt{A\_B = [A,B]}$
    $\tt{X}$     $\tt{X\_m}$    Modification     $\tt{A\_P = [A]}$

Table: Interpretation of reaction activity based on stoichiometry