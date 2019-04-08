BioNetGen and WESTPA pipeline

This pipeline requires [BioNetGen](https://www.csb.pitt.edu/Faculty/Faeder/?page_id=409) and [WESTPA](https://github.com/westpa/westpa) already installed on the machine you want to run the simulation on, I suggest using the [Anaconda python distribution](https://www.anaconda.com/download/) for WESTPA as well. For some of the analysis an additional requirement is [PyEMMA](http://emma-project.org/latest/). I suggest following the Jupyter notebook provided in the main folder of this repo to understand how to use the pipeline. 
  
I suggest using the following instructions (especially for Linux) for acquiring and installing dependencies: 

1. Install Anaconda python using (link is for linux, 64bit version):
```
wget https://repo.anaconda.com/archive/Anaconda2-5.2.0-Linux-x86_64.sh
chmod u+x Anaconda2-5.2.0-Linux-x86_64.sh
./Anaconda2-5.2.0-Linux-x86_64.sh
```
The last command will ask you where you want Anaconda python installed it will also ask if you want to make it the default python (I suggest doing so if you don't use another python). 

2. You then want to use "pip" command that comes with Anaconda python (specifically the one you just installed) to install PyEmma with:
```
pip install pyemma
```
If you are not sure if you are using the right pip you can try doing
```
which pip
```
to see if it points to the anaconda python 2.7 you installed.

3. Once both are installed, you want to clone and install WESTPA:
```
git clone https://github.com/westpa/westpa.git
cd westpa
./setup.sh
```
Before running setup.sh, I suggest checking to make sure you have the right python with
```
which python
```
and make sure it points to the anaconda python 2.7 you installed.

4. Install BioNetGen from and untar the folder, this is the folder you will point to later on (the one that contains the file BNG2.pl)

5. Once the setup is complete, clone this repo:
```
cd lib/examples
git clone https://github.com/ASinanSaglam/BNG_WESTPA_pipeline.git
cd BNG_WESTPA_pipeline
```

5. Now you are ready to setup a WESTPA simulation. You should edit the opts.yaml example file provided and point to WESTPA, BioNetGen and the .bngl model file you want to simulate. Here you can also edit the WE sampling options. 

```
```

This should create a folder named after the folder name you choose in the yaml file. 

6. You can now navigate to the WESTPA simulation folder. The following commands should run the simulation. 

```
./init.sh
./run.sh --n-workers X
```
where X is the number of cores you want WESTPA to use. This took about 15 minutes on 4 cores for me on a Xeon @3.5GHz. 
https://github.com/ASinanSaglam/BNG_WESTPA_pipeline/issues
7. Once the simulation is complete, you can either move the analysis folder or copy the files ```west.h5``` and ```system.py``` to the analysis folder (named WESTPA_BNG_analysis) and run all of the analysis using the following command: 

```
./run_all_analysis.sh 4
```

where the argument is the number of clusters you want. Please note, depending on the model you have used and/or the convergence of your simulation, PCCA+ clustering might not work because it expects a reversible transition matrix, see [here](http://www.emma-project.org/v2.4/api/generated/pyemma.msm.PCCA.html) for more information. You can try to get around this issue by skipping this check but that requires the modification of PyEMMA code and it's beyond the scope of this pipeline.

7. This repo is still heavily under construction, please let me know if you have any issues by reporting your issue under [github issues page](https://github.com/ASinanSaglam/BNG_WESTPA_pipeline/issues).
