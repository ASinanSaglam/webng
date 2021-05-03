.. _analysis:

########
Analysis
########

.. toctree::
   :maxdepth: 2
   :caption: Contents:
 
In the :code:`mysim.yaml` file you created you should see an analysis section. To 
learn more about the available options, please see :ref:`config` page. The analyses
can be ran using the command

.. code-block:: shell

   webng analysis --opts mysim.yaml

and webng will run the analyses using the configuration options given by the file. 

Probability distribution analyses
=================================

Average analysis
----------------

:code:`average` will create a N by N set of plots where N is the number of observables 
you have in the BNG model after running the appropriate WESTPA tools. The results will 
be saved in the folder written under :code:`analyses/average/output` (by default it is set
to :code:`average.png`). The plot will look like a matrix of plots where the diagonal 
contains 1D probability distributions of each observable and every off-diagonal will be a 
2D probability heatmap of each pair of observables.

Evolution analysis
------------------

The analysis :code:`evolution` will make a probability distribution evolution plot for 
each observable so you can track the progress of your simulation.

Clustering and network analyses
===============================

Clustering analysis
-------------------

:code:`cluster` analysis will allow you to use the transition matrix estimated from your 
simulation and do `PCCA+ clustering <https://link.springer.com/article/10.1007/s11634-013-0134-6>`_.
This type of clustering is useful to maximize transition within stable states and minimize transitions 
between unstable states and in this way it takes kinetics of the system into account. For various
options available to you, see :ref:`Average` page.

Network generation
------------------
:code:`network` analysis will use the results of your clustering and give you :code:`gml` files 
that can be used to visualize the clusters. This analysis will give you two files, one for the 
full transition matrix and one for the clustered result. For various options available to you, 
see :ref:`Evolution` page.