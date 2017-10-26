from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import time
import numpy as np
from tqdm import tqdm
from pumha.pop import Population


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
        for population in self.populations:
            with open('Densities/t=' + str(
                    timestep) + '_' + population.kind + '.ppm',
                      'w+') as density_file:
                density_file.write(
                    str(population.density.shape[0]) + ' ' + str(population.density.shape[1]) + '\n')
                density_file.write('\n')
                density_file.write(
                    '\n'.join([' '.join(['{:.2f}'.format(num) for num in row])
                               for row in population.density]))

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
