from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import time
import numpy as np
from scipy import misc
from tqdm import tqdm
from pumha.pop import Population, HarePopulation, PumaPopulation


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

    :Example:

        Create new simulation with two populations: puma, hare

        Each population is of extended puma.pop.Population type

        Run a population over 500 steps and save ppm output every 4th step

        >>> from pumha.sim import Simulation
        >>> sim = Simulation(puma, hare)
        >>> sim.run(500, 4)

    :ivar populations: List of populations in a simulation
    :type populations: list of pumha.pop.Population types
    """

    def __init__(self, *args):
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]
        self._print_info = True

    def add_population(self, pop):
        """Add population object to a simulation

        :param pop: a population to be added to a simulation
        :type pop: pumha.pop.Population
        """
        if isinstance(pop, Population):
            self.populations.append(pop)
        else:
            print("Object is not of Population type")

    def remove_population(self, pop):
        """Remove population from a simulation

        :param pop: apopulation to be removed from a simulation
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

    def run(self, num_steps, save_freq):
        """Run a simulation over given number of steps and save ppm output

        Instance population list is updated every second iteration. At the end
        of a simulation it is updated with the latest version.
        The method invokes save_density_grid_interface() every save_freq step
        in attempt to save ppm output.
        Method also provides simple timer for a loop which prints total elapsed
        time at the end of a simulation to the standard output.

        :param num_steps: Number of steps for a simulation
        :type num_steps: int
        :param save_freq: Number of time steps between outputs
        :type num_steps: int
        """
        print('''
              Running simulation over %s steps\n
              ppm output is saved every %s steps\n''' % (num_steps, save_freq))
        start = time.time()
        populations_old = np.copy(self.populations)
        # tqdm is used to provide progress bar
        for i in tqdm(range(num_steps)):
            if i % 2 == 0:
                self.update(populations_old, self.populations)
            else:
                self.update(self.populations, populations_old)
            # saving ppm file every T steps
            if i % save_freq == 0:
                self.save_density_grid_interface(i)
                self.save_average_density(i)

        # make sure we return last updated array
        if num_steps % 2 == 0:
            self.populations = np.copy(populations_old)
        end = time.time()
        print("Simulation time: %.2f s" % (end - start))

    def save_density_grid_interface(self, i):
        info = '''
        Save to ppm file method requires exactly 2 populations
        in a simulation. One of hares and one of pumas.
        Other cases are not yet implemented. In fact they will never be.
        The simulation will continue without ppm visualisation
        '''
        if len(self.populations) == 2 and self._print_info:
            try:
                self.save_density_grid(i)
            except UnboundLocalError:
                print(info)
                self._print_info = False
        elif self._print_info:
            print(info)
            self._print_info = False

    def save_density_grid(self, timestep):

        """Write the densities on each landscape square to a plain ppm file

        The function writes the density of a population to a file in the folder
        'densities' which has a name in a format 't = *timestep*_plain.ppm
        All the squares with water are assigned blue RGB value (0 0, 225).

        The files are in a plain PPM format - each line is separated into
        a group of 3 values correpsonding to a pixel, each value in those
        triplets represents either red, green or blue value. The dimension
        of the landscape is given in the head of the file.

        Example:

        P3
        # some comment
        4 4

        0 0 255  0 0 255  0 0 255  0 0 255
        0 0 255  34 56 255  28 60 255  0 0 255
        0 0 255  30 50 255  30 57 225  0 0 255
        0 0 255  0 0 255  0 0 255  0 0 255

        This PPM file represents a small island surrounded by water. Since lines
        in a PPM file must be no longer than 70 characters, the function creates
        an array of strings, every string representing a pixel and then writes
        those strings to a file, 5 pixels on every line (since in case every RGB
        value is a 3 digit number, at most five of them would fit to a line of
        a length 70 characters).

        :param timestep: the timestep to which the density matrix corresponds to
        :type timestep: float

        """
        #find puma and hare densities
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = pop.density
            else:
                puma_pop = pop.density

        density_file = 'densities/t = '+str(timestep)+'_plain.ppm'

        # creating an array of strings where every string represents a pixel
        density_arr = []
        rows, cols = hare_pop.shape
        for i in range(rows):
            for j in range(cols):
                puma_pop_ij = int(round(puma_pop[i][j]))
                hare_pop_ij = int(round(hare_pop[i][j]))
                density_arr.append(str(puma_pop_ij)+' '+str(hare_pop_ij)+ ' 255')
        #writing pixels on a file in a plain ppm format.
        with open(density_file, 'w+') as f:
            f.write('P3'+'\n')
            f.write('#da raw ppm file'+'\n')
            rows, cols = hare_pop.shape
            f.write('%s %s\n' % (rows, cols))
            f.write('5\n')
            i = 4
            for segment in density_arr:
                f.write(segment + '  ')
                i = (i + 1) % 5
                if i == 4:
                    f.write('\n')
            f.write('\n')



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
        """
        with open('average_densities.txt',
                  'a+') as f:
            f.write('----------------------------\n')
            f.write('t = ' + str(timestep) + '\n')
            for pop in self.populations:
                average_pop = np.sum(pop.density) / (
                    (pop.density.shape[0] - 2) * (pop.density.shape[1] - 2))
                f.write(pop.kind + ' ' + str(average_pop) + '\n')


