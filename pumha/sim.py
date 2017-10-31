from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import time
import os
import numpy as np
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
        At the end of the simulation rescale_ppm_files() method is invoked to
        rescale all ppm files using highest value of the density.
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
        #self.create_output_dir()
        print(os.path.dirname(__file__))
        populations_old = np.copy(self.populations)
        # tqdm is used to provide progress bar
        max_density = 0
        for i in tqdm(range(num_steps)):
            if i % 2 == 0:
                self.update(populations_old, self.populations)
            else:
                self.update(self.populations, populations_old)
            # saving ppm file every T steps
            if i % save_freq == 0:
                # save output
                self.save_density_grid_interface(i)
                self.save_average_density(i)
                # find max value of density
                new_max_ro = np.amax([p.density for p in self.populations])
                if new_max_ro > max_density:
                    max_density = new_max_ro

        # use max density value to rescale all ppm files
        self.rescale_ppm_files(max_density)

        # make sure we return last updated array
        if num_steps % 2 == 0:
            self.populations = np.copy(populations_old)
        end = time.time()
        print("Simulation time: %.2f s" % (end - start))

    def create_output_dir(self):
        timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
        new_dir = 'densities-' + timestr
        print('Creating new output directory:')
        print(os.path.abspath(new_dir))
        if not os.path.exists(new_dir):
                os.makedirs(new_dir)

    def rescale_ppm_files(self, max_density):
        max_density = int(max_density)

    def save_density_grid_interface(self, i):
        """Simple interface to save_density_grid method

        Provides extandable interface to potential group of save_density_grid
        methods each one to cover specific case for a simulation. This is
        mostly because of the limitation of the ppm file format. Currently only
        the case of simulation containing pumas and hares population is
        implemented.

        :param timestep: the timestep to which the density matrix corresponds to
        :type timestep: int
        """
        info = '''
        Save to ppm file method requires exactly 2 populations
        in a simulation. One of hares and one of pumas.
        Other cases are not yet implemented. In fact they will never be.
        The simulation will continue without ppm visualisation

        Current population(s):
        '''
        
        if len(self.populations) == 2 and self._print_info:
            try:
                self.save_density_grid(i)
            except UnboundLocalError:
                print("%s\n %s" % (info, self.populations))
                self._print_info = False
        elif self._print_info:
            print("%s\n %s" % (info, self.populations))
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
        :type timestep: int

        """
        #find puma and hare densities and scaling
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = 10 * pop.density
                #all values greater than 255 will be assigned value 255
                hare_pop[hare_pop > 255] = 255
            else:
                puma_pop = 10 * pop.density
                puma_pop[puma_pop > 255] = 255

        density_file = 'densities/t = '+str(timestep)+'_plain.ppm'

        density_arr = []
        rows, cols = hare_pop.shape
        for i in range(rows):
            for j in range(cols):
                puma_pop_ij = int(round(puma_pop[i][j]))
                hare_pop_ij = int(round(hare_pop[i][j]))
                density_arr.append(str(puma_pop_ij)+' '+str(hare_pop_ij)+ ' 255')
        # writing pixels on a file in a plain ppm format
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
        and dividing it by the numbers of squares in the grid. The density is
        saved to a file 'average_densities.txt', where the first column gives
        the timestep and second and third columns hare and puma densities at that
        time step respectively.

        :param timestep: timestep at which the averages are calculated.
        """
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = pop.density
            else:
                puma_pop = pop.density

        populations = [hare_pop, puma_pop]
        with open('average_densities.txt', 'a+') as f:
            f.write(str(timestep) + '           ')
            for pop in populations:
                average_pop = np.sum(pop) / (
                    (pop.shape[0] - 2) * (pop.shape[1] - 2))
                f.write(str(average_pop) + '          ')
            f.write('\n')


