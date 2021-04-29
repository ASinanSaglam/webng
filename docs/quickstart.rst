.. _quickstart:

###########
Quick Start
###########

Installation
============

The suggested python distribution to use is the `Anaconda python distribution <https://www.anaconda.com/download/>`_.
After that is installed, you can install webng directly from PyPI using pip

.. code-block:: shell

    pip install webng

which will also install WESTPA and BioNetGen python libraries which means you only need to 
run this command and have your model to run a WESTPA simulation. 

Usage
=====

After installation complete you can test to see if it's properly installed with

.. code-block:: shell

   webng -h

if this command prints out help, the command line tool is installed.

In order to use the tool, you will need a YAML configuration file. This tool comes with a 
subcommand that can generate a template YAML configuration file for you with the command

.. code-block:: shell

   webng template -i mymodel.bngl -o mysim.yaml

this should write a sample configuration file to :code:`mysim.yaml`. See :ref:`config` page to
learn more about what is contained in this file. Next let's actually make the WESTPA simulation 
folder with

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

See :ref:`analysis` page to learn more about the available analyses in webng.