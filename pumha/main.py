"""Pumas and hares simulation

Usage: main.py <landscape_file> [<config_file>]
       main.py (-h | --help | --version)

The program requires landscape file in the following format:

    4 3
    0 1 1 0
    0 1 0 0
    0 1 1 0

The first line specify size of the landscape grid.
Land is represented by 1 and water by 0.
The program can simulate arbitrary size grids subject to
hardware restrictions.

If config file is not provided the program will display warning
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
from pumha.env import Landscape
from pumha.pop import (Configuration,
                       PumaPopulation,
                       HarePopulation)
from pumha.sim import Simulation
import os
import sys
from docopt import docopt

import pkg_resources
# get version from setup.py
version = pkg_resources.require("PumHa")[0].version

def main():
    arguments = docopt(__doc__, version=version)
    directory = os.path.dirname(os.path.abspath(__file__))
    #print(arguments)
    config_file = arguments.get("<config_file>")

    ''' idea here is:
        ------------------------
        case 1)
        if no config is specified check if
        data/default.dat exists.
        if yes load it and warn user that defaults are used
        if no create it then load it + warning

        case 2)
        if config file is specified load it

        case 3)
        if specified config file does not exist
        or is of wrong format (not implemented)
        exit and print message
        ------------------------

        If some of those cases can be handled by the Config class it is even
        better but what's here should work fine.

        Also I'm not sure have I implemented Config class the right way.
        Please correct me if I'm wrong

    '''
    # case 1) if no config argument given
    if config_file is None:
        print("\nNo config file specified...")
        print("Using default config values...\n")
        config = Configuration(os.path.join(directory, "data/default.dat"))
    # case 2) and 3)
    else:
        if os.path.isfile(config_file):
            config = Configuration(os.path.abspath(config_file))
        else:
            print("Config file does not exist")
            print('Try \'pumha --help\' for help')
            sys.exit(1)

    map_file = arguments.get('<landscape_file>')
    env = Landscape(map_file)
    puma_pop = PumaPopulation(env)
    hare_pop = HarePopulation(env)

    hare_pop.load_config(config.hare_birth,
                         config.hare_predation,
                         config.hare_diffusion,
                         config.time_Step)

    puma_pop.load_config(config.puma_birth,
                         config.puma_mortality,
                         config.puma_diffusion,
                         config.time_Step)

    sim = Simulation(env, puma_pop, hare_pop)
    sim.run(config.steps, config.output_interval)

if __name__ == "__main__":
    main()
    '''
    # create new landscape from the file 'my_land'
    directory = os.path.dirname(os.path.abspath(__file__))
    map_file = os.path.join(directory, 'data/map1.dat')
    env = Landscape(map_file)
    config_file = os.path.join(directory, 'data/config.dat')
    config = Configuration(config_file)

    print(env.landscape)
    print(env.dry_squares)

    # create new populations using default values
    puma_pop = PumaPopulation(env)
    print(puma_pop.birth)
    print(puma_pop.death)
    print(puma_pop.max_ro)
    print('#######')

    hare_pop = HarePopulation(env)
    print(hare_pop.birth)
    print(hare_pop.death)
    print(hare_pop.max_ro)

    #hare_pop.load_config(config.hare_birth, config.hare_predation, config.hare_diffusion, config.time_Step)

    print(hare_pop.birth)
    print(hare_pop.death)
    print(hare_pop.max_ro)


    print(puma_pop.density)
    # create new population using specific values (config file...)
    #......
    # create new simulation with the landscape env and puma population


    sim = Simulation(env, puma_pop, hare_pop)
    sim.run(400, 8)
    print(puma_pop.density)

    # sim.run(20)
    #sim.save_density_grid_v2(34, env)
    '''



