import numpy as np
import simplejson as json
from scipy.ndimage import convolve
from collections import OrderedDict


    # Chloe
class Config():
    def __init__(self, config_file):

        try:
            My_File = open('data.cfg')
        except IOError:
            self.create_config()

	self.config = self.load_from_file()

    def load_from_file(self):
        #parse config file and assign self.r etc

        with open('data.cfg', 'r') as My_File:
            Config = json.load(My_File, object_pairs_hook=OrderedDict)
        
        for key in Config:
            value = Config[key]
            print("{} ({})".format(key, value))
        
        Accept_Default = raw_input('Accept default values? (Enter to accept, anything else to configure simulation.')
        if Accept_Default == "":
            print('Continuing with defaults.')
        else:
            print('Enter a value or press enter to keep default:'
            for key in Config:
                value = Config[key]
                User_Setting = raw_input("{} ({}): ".format(key, value))
                if not User_Setting == "":
                    Config[key] = User_Setting

        self.r = Config["Hare_birth"]
        self.a = Config["Hare_predation"]
        self.b = Config["Hare_diffusion"]
        self.m = Config["Puma_birth"]
        self.k = Config["Puma_mortality"]
        self.l = Config["Puma_diffusion"]
        self.deltat = Config["Time_Step"]
	
        return Config

    def create_config(self):
        default = {
            'Hare_birth': 0.08,
            'Hare_predation': 0.04,
            'Hare_diffusion': 0.2,
            'Puma_birth': 0.02,
            'Puma_mortality': 0.06,
            'Puma_diffusion': 0.2,
            'Time_Step': 0.4
        }

        with open('data.cfg', 'w') as outfile:
            json.dump(default, outfile, sort_keys=True)

        return


class Landscape(object):
    def __init__(self, filename):
        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()

    def load_landscape(self, filename):
        print('Loading landscape')

	return np.pad(np.loadtxt(filename,skiprows=1), ((1,1),(1,1)), mode='constant', constant_values=0)


    def find_dry_squares(self):
        print('calculating number of dry squares')
        kernel =  [[0,1,0], [1,0,1], [0,1,0]]
        return convolve(self.landscape, kernel, mode='constant')

    # find and save indices of an landscape array
    # as tuples
    # eg [(0,0), (1,1), (2,3)]
    # Why bother?
    # Any iteration over landscape can be replaced
    # with iteration over land idices which will make
    # life easier (no need to check each time are we on land)
    # and way faster
    # also add new Landscape class variable to store it
    # so other classes can access it
    def find_land_squares_indices():
        return []


class Population(object):
    def __init__(self, Landscape, birth, death, diffusion, min_ro, max_ro):
        self.min_ro = min_ro
        self.max_ro = max_ro
        self.birth = birth
        self.death = death
        self.diffusion = diffusion

        self.density = self.random_density(landscape_in)

    # Elen
    def random_density(self, landscape_inp):
        min_ro = self.min_ro
        max_ro = self.max_ro
        # turning the array of integers into an array of floats
        grid = landscape_inp.landscape.astype(np.float32)
        # assigning a random density to every cell between min_ro and max_ro
        grid[grid == 1] = np.random.uniform(min_ro, max_ro,
                                            grid[grid == 1].shape)
        return grid


#Marcin

class PumaPopulation(Population):
    def __init__(self, Landscape, birth=.02, death=.06, diffusion=.02,
                 min_ro=0., max_ro=5., dt=.4):
        super(PumaPopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt=.4)
        print('Puma population created')

    def update_density(self, old_populations, populations):
        # extract required populations density arrays for update
        # and assign to reference arrays
        # if no populations found assign zero density array
        rows, cols = self.density.shape
        zero_density_arr = np.zeros((rows, cols))
        P_new = next((pop.density for pop in populations if
                      isinstance(pop, PumaPopulation)), zero_density_arr)
        P = next((pop.density for pop in old_populations if
                  isinstance(pop, PumaPopulation)), zero_density_arr)
        H = next((pop.density for pop in old_populations if
                  isinstance(pop, HarePopulation)), zero_density_arr)

        for i in range(rows):
            for j in range(cols):
                P_new[i][j] = self.update_density_ij(i, j, P, H)

    def update_density_ij(self, i, j, P, H):
        b = self.birh
        m = self.death
        l = self.diffusion
        dt = self.dt
        N = self._N
        return P[i][j] + dt * (b * H[i][j] * P[i][i] - m * P[i][j]
                               + l * ((P[i-1][j] + P[i+1][j] + P[i][j-1] + P[i][j+1])
                                      - N[i][j] * P[i][j]))

class HarePopulation(Population):
    def __init__(self, Landscape, birth=.08, death=.04, diffusion=.02,
                 min_ro=0., max_ro=5., dt=.4):
        super(HarePopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt=.4)
        print('Hare population created')

    def update_density(self, old_populations, populations):
        # extract required populations density arrays for update
        # and assign to reference arrays
        # if no populations assign zero density array
        rows, cols = self.density.shape
        zero_density_arr = np.zeros((rows, cols))
        H_new = next((pop.density for pop in populations if
                      isinstance(pop, HarePopulation)), zero_density_arr)
        P = next((pop.density for pop in old_populations if
                  isinstance(pop, PumaPopulation)), zero_density_arr)
        H = next((pop.density for pop in old_populations if
                  isinstance(pop, HarePopulation)), zero_density_arr)

        # update array but ommit water boundary
        # ToDo
        # iterate i,j which are land only (skip water)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                H_new[i][j] = self.update_density_ij(i, j, P, H)

    def update_density_ij(self, i, j, P, H):
        r = self.birh
        a = self.death
        k = self.diffusion
        dt = self.dt
        N = self._N
        return H[i][j] + dt * (r * H[i][j] - a * H[i][j] * P[i][j]
                               + k * ((H[i-1][j] + H[i+1][j] + H[i][j-1] + H[i][j+1])
                                      - N[i][j] * H[i][j]))



class Simulation():

    """This is class docstring
    Blaaa
    """
    def __init__(self, Landscape, *args):
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
  

        return self.populations.append(pop)
#Marcin
    # not sure is this function required
    def remove_population(self, pop):
        print(pop.kind + ' removed')
    #Marcin

    def update(self):
        for pop in self.populations:
            pop.update_density(self.populations)
		  

def save_density_grid(self, timestep, *args):
        # creating a new file in directory "Densities", assuming it has been
        # created through a makefile (?)
        # args consists of class instances of either HarePopulation or
        # PumaPopulation. Assuming that somewhere
        # in these classes there is a variable self.density which is a numpy
        # array that holds the array that needs to go to the file.
        for population in args:
            with open('Densities/t=' + str(timestep) + '_' + population.kind + '.ppm',
                      'w+') as density_file:
                density_file.write(str(population.density))

    def save_average_density(self, timestep, *args):
        # args again PumaPopulation or HarePopulation class instances.
        # Creating a file for average densities in the same folder, no new
        # folder needed for one file, I think
        with open('average_densities.txt',
                          'a+') as average_density_file:
            average_density_file.write('t = ' + str(timestep) + '\n')
            for population in args:
                average_population = np.sum(population) / (
                (population.shape[0]-2) * (population.shape[1]-2))
                average_density_file.write(population.kind + ' ' + str(average_population) + '\n')		  
		  
     
# create new landscape from the file 'my_land'
env = Landscape('islands.dat')
config = Config('config.dat')

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

# create new population using specific values (config file...)
#......
# create new simulation with the landscape env and puma population
sim = Simulation(env, puma_pop)
# update one step
#sim.run(20)
