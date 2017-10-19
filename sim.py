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
        
        Accept_Default = raw_input("Accept default values? (Enter to accept, anything else to configure simulation.")
        if Accept_Default == "":
            print "Continuing with defaults."
        else:
            print "Enter a value or press enter to keep default:"
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


class Population(object):
    def __init__(self, Landscape, birth, death, diffusion, min_ro, max_ro):
        self.min_ro = min_ro
        self.max_ro = max_ro
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.density = self.random_density(Landscape)
        
    #Elen
    def random_density(self, Landscape):
        min_ro = self.min_ro
        max_ro = self.max_ro
        grid = Landscape.landscape
        print('Random distribution')
        #return np.array(of size landscape)

#Marcin
class PumaPopulation(Population):
    def __init__(self, Landscape, birth=1.01, death=2.02, diffusion=3.03,
                 min_ro=0, max_ro=5):
        self.kind = 'PumaPopulation'
        super(PumaPopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro)
        print('Puma population created')

    # alternatively
    # def update_density(self, puma_pop, hare_pop):
    # which is slightly more messy to implement as you need to keep track of
    # arguments and their order but is arguably more efficient (how much?)
    def update_density(self, populations):
        # set X_pop.density to zeroes if no pop in populations
        # this should allow computation to proceed (verify that)
        zero_density_arr = np.zeros(self.density.shape)
        puma_pop = next((pop.density for pop in populations if
                         pop.kind == 'PumaPopulation'), zero_density_arr)
        hare_pop = next((pop.density for pop in populations if
                         pop.kind == 'HarePopulation'), zero_density_arr)
        print(hare_pop)
        print(puma_pop)
        print(self.kind + ' density updated')
        # set ro=0 if ro<0


# class Environment() ?
class Simulation():
#Marcin
    def __init__(self, Landscape, *args):
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]
        print('Running simulation')

    # not sure is this function required
    def add_population(self, pop):
        return self.populations.append(pop)
#Marcin
    # not sure is this function required
    def remove_population(self, pop):
        print(pop.kind + ' removed')
    #Marcin
    def update(self):
        for pop in self.populations:
            pop.update_density(self.populations)
     
    def run(self):
        print('run')
        #for loop
    #Elen
    def save_state(self):
        print('save')
        #save densities to ppm file

# create new landscape from the file 'my_land'
env = Landscape('islands.dat')
config = Config('config.dat')

# create new population using default values
puma_pop = PumaPopulation(env)
print(puma_pop.birth)
print(puma_pop.death)
print(puma_pop.max_ro)
print('#######')

# create new population using specific values (config file...)
puma_pop = PumaPopulation(env, death=9.999, max_ro=55)
print(puma_pop.birth)
print(puma_pop.death)
print(puma_pop.max_ro)

# create new simulation with the landscape env and puma population
sim = Simulation(env, puma_pop)
# update one step
sim.update()
