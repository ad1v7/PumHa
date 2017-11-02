"""Simulation module

Module contains only one class::

    Simulation

and one function::

    create_output_dir

The module is used to build new simulations using
extended Population classes and create the output data.

To run a simulation, use run() method.
"""
from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import time
import os
import numpy as np
from tqdm import tqdm
from pumha.pop import Population, HarePopulation


class Simulation(object):
    """Simulate time and space evolution of populations

    Only populations added to a populations list are simulated. If no
    populations are added, the simulation will run using density arrays of
    zeroes. If only one population is added but its update method requires
    existence of another population, the simulation will still run using zero
    density array for missing population.

    This can be interpreted as follows:

    Lets add only hare population; its update method requires puma population,
    if there are no pumas, since hare death rate is 0, they only increase in
    numbers until they rule a land!

    Similarly, if there is no hares, pumas will all starve to death.

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
        self.out_dir = create_output_dir()
        self.num_steps = 1  # redefined in run()

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
        try:
            self.populations.remove(pop)
            print(pop.kind + ' removed')
        except ValueError as ve:
            msg = ("No such a population in a list: %s, %s" % (pop, ve))
            print(msg)
            return msg

    def update(self, populations_old, populations_new):
        """One step update for all populations in a simulation

        :param populations_old: list of populations at time t
        :param populations_new: list of populations at time t+dt
        """
        for pop in self.populations:
            pop.update_density(populations_old, populations_new)

    def run(self, num_steps, save_freq):
        """Run a simulation over given number of steps and save an output to PPM

        Instance population list is updated every second iteration. At the end
        of a simulation it is updated with the latest version.
        The method invokes save_density_grid_interface() every save_freq step
        in attempt to save output to a ppm file.
        At the end of the simulation rescale_ppm_files() method is invoked to
        rescale all ppm files using highest value of the density.
        Method also includes a simple timer for a loop which prints the
        total elapsed time at the end of a simulation to the standard output.

        :param num_steps: Number of steps for a simulation
        :type num_steps: int
        :param save_freq: Number of time steps between outputs
        :type num_steps: int
        """
        self.num_steps = num_steps
        print('''
              Running simulation over %s steps\n
              ppm output is saved every %s steps\n''' % (num_steps, save_freq))
        start = time.time()
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

    def rescale_ppm_files(self, max_density):
        """Rescale all PPM files using common PPM color value (Maxval)

        The method takes the highest recorded density from the entire
        simulation and uses it as common scaling factor for all PPM files.
        In this way the whole simulation is scaled properly.

        :param max_density: maximum density for a single square from the run
        :type max_density: int, float
        """
        max_density = int(max_density)+1
        ppm_maxval = 65536  # maxmimum allowed color value for ppm format
        colorline = 3   # 4th line in a file is a color max value

        # make sure color value is below ppm format allowed maximum
        if max_density > ppm_maxval:
            max_density = ppm_maxval

        # list all files, open, edit color value line and save
        for item in os.listdir(self.out_dir):
            item = os.path.join(self.out_dir, item)
            if item.endswith(".ppm"):
                with open(item, 'r') as my_file:
                    filedata = my_file.readlines()
                    filedata[colorline] = str(max_density)+'\n'
                with open(item, 'w') as my_file:
                    my_file.writelines(filedata)

    def save_density_grid_interface(self, i):
        """Simple interface to save_density_grid method

        Provides extendable interface to potential group of save_density_grid
        methods, each one to cover specific case for a simulation. This is
        mostly because of the limitation of the PPM file format. Currently only
        the case of simulation containing puma and hare populations is
        implemented.

        :param timestep: the timestep to which the density \
                matrix corresponds to
        :type timestep: int
        """
        info = '''
        Save to PPM file method requires exactly 2 populations
        in a simulation, one of hares and one of pumas.
        Other cases are not yet implemented. In fact they will never be.
        The simulation will continue without PPM visualisation.

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
        """Write the densities on each landscape square to a plain PPM file

        The method writes the density of a population to a file in the output
        folder. The name of a file is in a format timestep.ppm.

        The files are in a plain PPM format - each line is separated into
        a group of 3 values corresponding to a pixel, each value in those
        triplets represents either red, green or blue. The dimension
        of the landscape is given in the head of the file. The value after
        the dimensions is a scaling factor which is updated in every file
        in the end of the simulation, based on the highest maximum density
        encountered in the simulation. That is done with the
        rescale_ppm_files method.

        Example::

            P3
            # some comment
            4 4

            0 0 255  0 0 255  0 0 255  0 0 255
            0 0 255  34 56 255  28 60 255  0 0 255
            0 0 255  30 50 255  30 57 225  0 0 255
            0 0 255  0 0 255  0 0 255  0 0 255

        This PPM file represents a small island surrounded by water.
        Since lines in a PPM file must be no longer than 70 characters,
        the function creates an array of strings, every string representing
        a pixel and then writes those strings to a file.

        :param timestep: the timestep to which the density matrix \
                corresponds to
        :type timestep: int

        """
        # find puma and hare densities
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = pop.density
            else:
                puma_pop = pop.density

        # get nicely formatted step number for printing
        time_st = str(timestep).zfill(len(str(self.num_steps)))
        # get output file name
        density_file = os.path.join(self.out_dir, time_st+'.ppm')

        density_arr = []
        rows, cols = hare_pop.shape
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                puma_pop_ij = int(round(puma_pop[i][j]))
                hare_pop_ij = int(round(hare_pop[i][j]))
                density_arr.append(str(puma_pop_ij) +
                                   ' ' + str(hare_pop_ij) + ' 255')

        # writing pixels on a file in a plain ppm format
        with open(density_file, 'w+') as out:
            out.write('P3' + '\n')
            out.write('#da plain ppm file' + '\n')
            out.write('%s %s\n' % (cols-2, rows-2))
            out.write('5\n')
            i = 3
            for segment in density_arr:
                out.write(segment + '  ')
                i = (i + 1) % 4
                if i == 3:
                    out.write('\n')
            out.write('\n')

    def save_average_density(self, timestep):
        """Calculate the average density of animals in the whole landscape

        The average population is found by summing all the densities in
        the grid and dividing it by the numbers of squares in the grid.
        The density is saved to a file 'average_densities.txt', where the first
        column gives the timestep and second and third columns hare and puma
        densities at that time step respectively.

        :param timestep: timestep at which the averages are calculated.
        """
        for pop in self.populations:
            if isinstance(pop, HarePopulation):
                hare_pop = pop.density
            else:
                puma_pop = pop.density

        populations = [hare_pop, puma_pop]
        out_file = os.path.join(self.out_dir, 'average_densities.dat')
        with open(out_file, 'a+') as out:
            out.write(str(timestep) + '           ')
            for pop in populations:
                average_pop = np.sum(pop) / (
                    (pop.shape[0] - 2) * (pop.shape[1] - 2))
                out.write(str(average_pop) + '          ')
            out.write('\n')


def create_output_dir():
    """Create directory for output PPM and dat files

    Directory is created using current date and time. All simulation output
    files are saved into this folder. The output directory is created in the
    directory where the script is running. The naming convention is as follows:

        PumHa_out_%Y-%m-%d-%H-%M-%S
    """
    timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
    new_dir_name = 'PumHa_out_' + timestr
    new_dir = os.path.abspath(new_dir_name)
    print('Creating new output directory:\n %s' % new_dir)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return new_dir
