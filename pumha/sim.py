import time
import numpy as np
from tqdm import tqdm
from pumha.pop import Population

class Simulation():
    """This is class docstring
    Blaaa
    """

    def __init__(self, *args):
        """ This is constructor docstring
        Blaaa
        """
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]

    def add_population(self, pop):
        """This is public method docstring
        ("Do this", "Return that")
        """
        self.populations.append(pop)

    def remove_population(self, pop):
        print(pop.kind + ' removed')
        return self.populations.remove(pop)

    def update(self, old_populations, populations):
        for pop in populations:
            pop.update_density(old_populations, populations)

    def run(self, num_steps):
        """This is public method docstring
        ("Do this", "Return that")
        """
        print('Running simulation')
        start = time.time()
        populations_old = np.copy(self.populations)
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
