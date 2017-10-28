from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import time
import numpy as np
from scipy import misc
from tqdm import tqdm
from pumha.pop import Population, HarePopulation, PumaPopulation
from pumha.env import Landscape


class Simulation():
    """Simulate time and space evolution of populations

    Only populations added to a populations list are simulated. If no
    populations are added the simulation will run using density arrays of
    zeroes. If only one population is added but its update method requires
    existance of another population the simulation will still run using zeros
    density array for missing population.
    
    This can be interpreted as follows:

    Lets add only hare population; its update method requires puma population,
    if there are no pumas hares death rate is 0 so they only increase in
    numbers until they rule a land!

    Similarly for pumas only - if there is no hares they all starve to death.

    :ivar populations: List of populations in a simulation
    :type populations: list of pumha.pop.Population types
    """

    def __init__(self, *args):
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]

    def add_population(self, pop):
        """Add population object to a simulation

        :param pop: population one  want to add to a simulation
        :type pop: pumha.pop.Population
        """
        if isinstance(pop, Population):
            self.populations.append(pop)
        else:
            print("Object is not of Population type")

    def remove_population(self, pop):
        """Remove population from a simulation

        :param pop: population one  want to remove from a simulation
        :type pop: pumha.pop.Population
        """
        print(pop.kind + ' removed')
        self.populations.remove(pop)

    def update(self, populations_old, populations_new):
        """One step update for all populations in a simulation

        :param populations_old: list of populations at time t
        :param populations_new: list of populations at time t+dt
        """
        for pop in self.populations:
            pop.update_density(populations_old, populations_new)

    def run(self, num_steps):
        """Run a simulation over given number of steps

        Instance population list is updated every second iteration. At the end
        of a simulation it is updated with the latest version.
        Method also provides simple timer for a loop which prints simulation
        time at the end of a simulation to the standard output.

        :param num_steps: Number of steps for a simulation
        :type num_steps: int
        """
        print('Running simulation')
        start = time.time()
        populations_old = np.copy(self.populations)
        # tqdm is used to provide progress bar
        for i in tqdm(range(num_steps)):
            if i % 2 == 0:
                self.update(populations_old, self.populations)
                self.save_density_grid_v2(i)
            else:
                self.update(self.populations, populations_old)

        # make sure we return last updated array
        if num_steps % 2 == 0:
            self.populations = np.copy(populations_old)
        end = time.time()
        print("Simulation time: %.2f s" % (end - start))

    def save_density_grid(self, timestep):
        """Write the densities on each landscape square to a ppm file

        This method writes the density of a population to a file in the folder
        'Densities' which has a name in a format 't=*timestep*_*population kind'.
        The first row in the file will give the dimensions of the density
        array. The density array is a 2D array consisting of float values that
        represent the average density on that square.

        :param timestep: the timestep to which the density matrix corresponds to
        :type timestep: float

        """
        land = environment.landscape
        # creating an array in in a format which could be converted to a ppm file
        ppm_grid = np.zeros((land.shape[0], land.shape[1], 3))
        # finding water and making it blue
        ppm_grid[:, :, 2][land == 0] = 225
        # colouring in densities
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                ppm_grid[:, :, 0] = 100*pop.density
            else:
                ppm_grid[:, :, 1] = 100*pop.density
        misc.imsave('Densities/t = '+str(timestep)+'.ppm', ppm_grid)


    def save_average_density(self, timestep):
        """Claculate the average density of animals in the whole landscape

        The average population is found by summing all the densities in the grid
        and dividing it by the area of the whole grid. The density is saved to a
        file 'average_densities.txt' in a format
        't = *timestep*
        *population kind* *average density*'
        For every timestep the densities are found for every density in the
        self.populations array.

        :param timestep: timestep at which the averages are calculated.
        :return:
        """
        with open('average_densities.txt',
                  'a+') as average_density_file:
            average_density_file.write('t = ' + str(timestep) + '\n')
            for population in self.populations:
                average_population = np.sum(population.density) / (
                    (population.density.shape[0] - 2) * (population.density.shape[1] - 2))
                average_density_file.write(
                    population.kind + ' ' + str(average_population) + '\n')

    def save_density_grid_v2(self, timestep):
        """Saves density grids

        extract density arrays from population list and assign to variables
        output this to a file
        P6 <---- raw ppm so we dont have to worry about 70 char limit
        cols rows <--- size of density array
        10 <---- this is actualy a scalling factor!!! I explain later
        Here comes density array <--- see comment below
        iterate over density grid (rows, cols = i,j)

        the format is
        R G B  R G B  R G B  R...
        one line corresponds to one line in density array than add print
        statement with new line and print another line and so on
        set B=0 always
        R = density of pumas for a given i,j grid square
        G = density of hares for a given i,j density grid square

        densities must be rounded as integers for ex
        str(int(round(density[i][j]))) before saving
        dont worry about scalling it should work as is

        for testing you can use new map1.dat will save you some time
        because it is smaller than islands2.dat
        
        any questions ask :)

        """

        #find puma and hare densities
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = pop.density
            else:
                puma_pop = pop.density

        with open('Densities/t = '+str(timestep)+'_plain.ppm', 'w+') as f:
            f.write('P3'+'\n')
            f.write('#da raw ppm file'+'\n')
            rows, cols = hare_pop.shape
            f.write('%s %s\n' % (rows, cols))
            f.write('5\n')
            for i in range(rows):
                for j in range(cols):
                    puma_pop_ij = int(round(puma_pop[i][j]))
                    hare_pop_ij = int(round(hare_pop[i][j]))
                    f.write(str(puma_pop_ij)+' '+str(hare_pop_ij)+ ' 255  ')
            f.write('\n')
