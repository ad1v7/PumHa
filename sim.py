import time
import numpy as np
import sys
import simplejson as json
from scipy.ndimage import convolve
from collections import OrderedDict
from tqdm import tqdm


# Chloe
class Configuration():
    def __init__(self, config_file):

        try:
            my_file = open(config_file)
        except IOError:
            self.create_config(config_file)

        self.config = self.load_from_file(config_file)

    def load_from_file(self, config_file):
        # parse config file and assign values

        with open(config_file, 'r') as f:
            config = json.load(f, object_pairs_hook=OrderedDict)

        for key in config:
            value = config[key]
            print("{} ({})".format(key, value))

        self.hare_birth = config["Hare_birth"]
        self.hare_predation = config["Hare_predation"]
        self.hare_diffusion = config["Hare_diffusion"]
        self.puma_birth = config["Puma_birth"]
        self.puma_mortality = config["Puma_mortality"]
        self.puma_diffusion = config["Puma_diffusion"]
        self.time_Step = config["Time_Step"]

        return config

    #Create a default configuration set up as JSON.
    def create_config(self, config_file):
        default = {
            'Hare_birth': 0.08,
            'Hare_predation': 0.04,
            'Hare_diffusion': 0.2,
            'Puma_birth': 0.02,
            'Puma_mortality': 0.06,
            'Puma_diffusion': 0.2,
            'Time_Step': 0.4
        }

        with open(config_file, 'w') as outfile:
            json.dump(default, outfile, sort_keys=True)


class Landscape(object):
    def __init__(self, filename):
        #Check if the landscape exists.
        try:
            my_file = open(filename)
        except IOError:
            print('No such landscape file.')
            sys.exit(1)

        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()
        self.land_indices = self.find_land_squares_indices()

    #Load landscape from file, in to an array padded with a border of water.
    def load_landscape(self, filename):
        print('Loading landscape')
        return np.pad(np.loadtxt(filename, skiprows=1), ((1, 1), (1, 1)),
                      mode='constant', constant_values=0)


    #This gives every element of an array a value equal to the value of it's
    #neighbours multiplied by the kernel.  Since land is 1 and water is 0,
    #multiplying + neighbours by one gives the sum of the land neighbours
    #minus the diagals.  This means we can calculate this value just once.
    def find_dry_squares(self):
        print('calculating number of dry squares')
        kernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        return convolve(self.landscape, kernel, mode='constant')

    #Return tuples of all non-zero elements of landscape (ie, the land)
    def find_land_squares_indices(self):
        return np.transpose(np.nonzero(self.landscape))


class Population(object):
    def __init__(self, landscape_inp, birth, death, diffusion, min_ro, max_ro, dt):
        self.min_ro = min_ro
        self.max_ro = max_ro
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.dt = dt
        self.density = self.random_density(landscape_inp)
        self._N = landscape_inp.dry_squares
        self._landscape = landscape_inp.landscape

    def random_density(self, landscape_inp):
        min_ro = self.min_ro
        max_ro = self.max_ro
        # turning the array of integers into an array of floats
        grid = landscape_inp.landscape.astype(np.float32)
        # assigning a random density to every cell between min_ro and max_ro
        grid[grid == 1] = np.random.uniform(min_ro, max_ro,
                                            grid[grid == 1].shape)
        return grid


    def load_config(self, birth, death, diffusion, dt):
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.dt = dt

    def find_density_arr(self, pop_class, pop_list):
        rows, cols = self.density.shape
        return next((p.density for p in pop_list if
                     isinstance(p, pop_class)), np.zeros((rows, cols)))


class PumaPopulation(Population):
    def __init__(self, Landscape, birth=.02, death=.06, diffusion=.02,
                 min_ro=0., max_ro=5., dt=.4):
        super(PumaPopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt=.4)
        self.kind = 'PumaPopulation'
        print('Puma population created')

    def update_density(self, populations_old, populations_new):
        # extract required populations density arrays for update
        P_new = self.find_density_arr(PumaPopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update all landscape ij
        # do not update boundary
        rows, cols = self.density.shape
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                P_new[i][j] = self.update_density_ij(i, j, P, H) * self._landscape[i][j]

    def update_density_ij(self, i, j, P, H):
        b = self.birth
        m = self.death
        l = self.diffusion
        dt = self.dt
        N = self._N
        return P[i][j] + dt * (b * H[i][j] * P[i][i] - m * P[i][j]
                               + l * ((P[i - 1][j] + P[i + 1][j] + P[i][j - 1] +
                                       P[i][j + 1])
                                      - N[i][j] * P[i][j]))


class HarePopulation(Population):
    def __init__(self, Landscape, birth=.08, death=.04, diffusion=.02,
                 min_ro=0., max_ro=5., dt=.4):
        super(HarePopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt=.4)
        print('Hare population created')
        self.kind = 'HarePopulation'

    def update_density(self, populations_old, populations_new):
        # extract required populations density arrays for update
        H_new = self.find_density_arr(HarePopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update array but ommit water boundary
        # ToDo
        # iterate i,j which are land only (skip water)
        rows, cols = self.density.shape
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                H_new[i][j] = self.update_density_ij(i, j, P, H) * self._landscape[i][j]

    def update_density_ij(self, i, j, P, H):
        r = self.birth
        a = self.death
        k = self.diffusion
        dt = self.dt
        N = self._N
        return H[i][j] + dt * (r * H[i][j] - a * H[i][j] * P[i][j]
                               + k * ((H[i - 1][j] + H[i + 1][j] + H[i][j - 1] +
                                       H[i][j + 1])
                                      - N[i][j] * H[i][j]))


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



# create new landscape from the file 'my_land'
env = Landscape('islands2.dat')
config = Configuration('config.dat')

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
sim = Simulation(env, puma_pop)
sim.run(5)
print(puma_pop.density)
# update one step
# sim.run(20)
sim.save_average_density(34)
