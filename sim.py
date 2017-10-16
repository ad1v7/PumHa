import numpy as np


class Landscape(object):
    def __init__(self, filename):
        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()

    def load_landscape(self, filename):
        print('Loading landscape')
        return []

    def find_dry_squares(self):
        print('calculating number of dry squares')
        return []


class Population(object):
    def __init__(self, Landscape, birth, death, diffusion, min_ro, max_ro):
        self.min_ro = min_ro
        self.max_ro = max_ro
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.density = self.random_density(Landscape)

    def random_density(self, Landscape):
        min_ro = self.min_ro
        max_ro = self.max_ro
        grid = Landscape.landscape
        print('Random distribution')
        return np.array([[1, 2], [3, 4]])


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
    def __init__(self, Landscape, *args):
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]
        print('Running simulation')

    # not sure is this function required
    def add_population(self, pop):
        return self.populations.append(pop)

    # not sure is this function required
    def remove_population(self, pop):
        print(pop.kind + ' removed')

    def update(self):
        for pop in self.populations:
            pop.update_density(self.populations)

# create new landscape from the file 'my_land'
env = Landscape('my_land')

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
