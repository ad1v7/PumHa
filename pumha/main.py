"""Pumas and hares simulation

Usage: pumha <landscape_file> [<config_file>]
       pumha (-h | --help | --version)

The program requires landscape file in the following format::

    4 3

    0 1 1 0
    0 1 0 0
    0 1 1 0

The first line in the input file specifies size of the landscape grid.
Land is represented by 1 and water by 0. The program can simulate arbitrary
size grids subject to hardware restrictions.

If config file is not provided, the program will display warning
and will continue using default values.

Arguments:

    landscape_file  required argument
    config_file     optional config file

Options:

    -h --help    Show this screen and exit.
    --version    Print current version
"""

from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
from docopt import docopt
import pkg_resources
from pumha.pop import (Configuration,
                       PumaPopulation,
                       HarePopulation)
from pumha.env import Landscape
from pumha.sim import Simulation


def main():
    """Entry point function for the PumHa program

    The function parses user input from the terminal and then sets up,
    configures and runs simulation using values in the config file.
    """
    # get version from setup.py
    version = pkg_resources.require("PumHa")[0].version
    # taking user input
    arguments = docopt(__doc__, version=version)
    config_file = arguments.get("<config_file>")
    map_file = arguments.get('<landscape_file>')

    # creating new simulation
    config = Configuration(config_file)

    env = Landscape(map_file)

    puma_pop = PumaPopulation(env,
                              birth=config.puma_birth,
                              death=config.puma_mortality,
                              diffusion=config.puma_diffusion,
                              dt=config.time_step)

    hare_pop = HarePopulation(env,
                              birth=config.hare_birth,
                              death=config.hare_predation,
                              diffusion=config.hare_diffusion,
                              dt=config.time_step)

    sim = Simulation(env, puma_pop, hare_pop)
    sim.run(config.steps, config.output_interval)

if __name__ == "__main__":
    main()
