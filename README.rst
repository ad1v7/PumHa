*****
PumHa
*****
PumHa package simulates the population dynamics of hares and pumas in a user-specified landscape. The population densities depend on a number of parameters, such as birth, death and diffucion rates, also on a rate at which pumas eat hares. For more in-depth mathematical formualtion, see ``PumaPopulation`` and ``HarePopulation`` classes in the ``pumha.pop`` module.

PumHa is written in Python and it is compatible with any version of Phython 2.7 or higher. Provided the package is correctly installed, it can be run in variety of operating systems, including Scientific Linux [comp lab serial number], Windows 10 and Ubuntu [serial number]. The code complies with the `PEP 257`_ and `PEP 8`_ conventions. PumHa package was developed with the help of `GitHub`_ and the tests were created using Python's `unittest`_ framework.

.. _PEP 257: https://www.python.org/dev/peps/pep-0257/ 
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _GitHub: https://github.com/
.. _unittest: https://docs.python.org/2/library/unittest.html


User can set the values of these parameters on a configuration file called config.dat, located in the data folder. 

The input landscape file must be a bitmask ASCII file with the first row giving the dimensions of the landscape and rest of the rows representing landscape (1 for land square and 0 for water), as an example,

  5 5

  1 1 1 1 1 

  1 1 1 1 0  

  1 0 0 0 0  

  1 1 0 0 0  

  1 1 0 0 0 


The simulation can be run from the pumha folder with a command

[command]

some stuff :)
cplab: Scientific Linux release 7.3 (Nitrogen)
Marcin's Ubuntu 16.04.3 LTS

How to install
##############
To install PumHa package on a Linux machine:

Change directory to your install directory (or create one).
Copy repository running the following command:
    git clone https://github.com/ad1v7/PumHa

::

    Alternatively if you are the lucky one to have a tar.gz package
    (in fact very lucky because only 4 people out of 7+ billions have it!)
    Extract archive content using:
        tar zxvf pumha.tar.gz
    where pumha.tar.gz is replaced with your archive name


make sure you are in a directory which contains setup.py
and use `pip <http://pip-installer.org>`_ ::
    pip install .
You might need to run above command as super user (root) ::
    sudo pip install .
If you can't run it as a root you can try::
    pip install --user .
In a latter case pip will install command line script into
    ~/.local/bin
directory (this is the case for Scientific Linux and Ubuntu)

::

If ~/.local/bin is not in your $PATH (run echo $PATH to check it put)
You can export it running the following command:
    export PATH=$PATH:~/.local/bin
You may want to add above line to ~/.profile so ~/.local/bin is added to path at login





How to use
########

How to  run tests
########
to run tests:

python setup.py test

See test directory for how to write unittests


Key design decisions
########

ToDo
########
Make sure that below tasks are distributed evenly

* Check is density array type of double precision float (float64)

  - answer: is not -> change to float64
* Add unit tests

  - how can we verify that the simulation does what it supposed to do?
* Add comments if necessary

  - comment other people code: this is the best way to improve!
  - ask if something is unclear -> this could be a bug
* add docstring to each module (top of each .py file)
* Add docstrings to each class and every public method

  - build documentation with Sphinx and add to docs directory
  - ...but wait for:
* Check code compliance with pep8 and pep257

  - Do it but after all unittests and docstrings are added
* Prepare Readme file

  - discuss content
  - find a volunteer :-)
* what data we want to include with the package
* Check, verify and discuss output
* Discuss module structure
* Go over requirements and make sure all tasks are either assigned or completed
* time step attribute in Population looks rather awkward; add it to Simulation?
* make sure output is saved every T step
* decide format of ppm file, how to get round 70 characters per line limit?

Puma Package
########
* should simulation continue after default config is created?
* clarify input and output
* what data include with the package
* add print frequency to the config
* scaling for ppm files
* probably need to have variable to store absolute path to output directory


* Information on the programming language, revision control, debuggers, build tools, and test tools you
have used.

* Where to get, and how to build and install, any third-party packages needed by your code (for
packages that are not already on the Physics Computational Lab machines).
* How to build your code.

* How to run your code.

* How to run your tests.

* Summary of key design decisions and reasons for these.

