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

if __name__ == "__main__":
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

    hare_pop.load_config(config.hare_birth, config.hare_predation, config.hare_diffusion, config.time_Step)

    print(hare_pop.birth)
    print(hare_pop.death)
    print(hare_pop.max_ro)


    print(puma_pop.density)
    # create new population using specific values (config file...)
    #......
    # create new simulation with the landscape env and puma population

    # Clearing the contents of an average density file
    f = open('average_densities.txt', 'w')
    f.close()
    with open('average_densities.txt', 'w')as f:
        f.write('timestep    hare population        puma population\n')
        f.write('-----------------------------------------------------\n')

    sim = Simulation(env, puma_pop, hare_pop)
    sim.run(400, 8)
    print(puma_pop.density)

    # sim.run(20)
    #sim.save_density_grid_v2(34, env)
    

def main():
    print('Hello')
