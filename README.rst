*****
PumHa
*****
Description what package does...

How to install
########
git clone https://github.com/ad1v7/PumHa

cd to directory which contains setup.py

pip install -e .

You might need to run above command as super user (root):
e.g. on Linux (Debian):
sudo pip install -e .

Testing
########
to run tests:

python setup.py test

See test directory for how to write unittests

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
