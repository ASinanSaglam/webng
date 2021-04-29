.. _analysis:

========
Analysis
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:
 

In the :code:`mysim.yaml` file you created you should see an analysis section. To 
learn more about the available options, please see :ref:`config` page. The analyses
can be ran using the command

.. code-block:: shell

   webng analysis --opts mysim.yaml

and webng will run the analyses using the configuration options given by the file. 

Average
~~~~~~~

:code:`average` will create a N by N set of plots where N is the number of observables 
you have in the BNG model after running the appropriate WESTPA tools. The results will 
be saved in the folder written under :code:`analyses/average/output` (by default it is set
to :code:`average.png`). The plot will look like a matrix of plots where the diagonal 
contains 1D probability distributions of each observable and every off-diagonal will be a 
2D probability heatmap of each pair of observables.

Evolution
~~~~~~~~~

The analysis :code:`evolution` will make a probability distribution evolution plot for 
each observable so you can track the progress of your simulation.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`