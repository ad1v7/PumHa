import numpy as np
"""
This is module docstring
"""
     

    # Chloe
class Config():
    def __init__(self, config_file):
        self.r = 0.
        self.d = 0.

    def load_from_file(self):
        pass


class Landscape(object):
    def __init__(self, filename):
        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()

    def load_landscape(self, filename):
        print('Loading landscape')

    def find_dry_squares(self):
        print('calculating number of dry squares')
        return []

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
    def __init__(self, Landscape, birth, death, diffusion, min_ro, max_ro, dt):
        self.min_ro = min_ro
        self.max_ro = max_ro
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.density = self.random_density(Landscape)
        self.dt = dt
        self._N = Landscape.dry_squares
        
    #Elen
    def random_density(self, Landscape):
        min_ro = self.min_ro
        max_ro = self.max_ro
        grid = Landscape.landscape
        print('Random distribution')

    def load_config(self, Config):
        self.min_ro = Config.min_ro
        self.max_ro = Config.max_ro
        self.birth = Config.birth
        self.death = Config.death
        self.diffusion = Config.diffusion
        self.dt = Config.dt


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
        """This is public method docstring
        ("Do this", "Return that")
        """
        self.populations.remove(pop)

    # not public method - no dosctring
    def update(self, old_populations, populations):
        for pop in populations:
            pop.update_density(old_populations, populations)

    def run(self, num_steps):
        """This is public method docstring
        ("Do this", "Return that")
        """
        print('Running simulation')
        old_populations = np.copy(self.populations)
        for i in range(num_steps):
            if i % 2 == 0:
                self.update(old_populations, self.populations)
            else:
                self.update(self.populations, old_populations)

        # make sure we return last updated array
        if num_steps % 2 == 0:
            self.populations = np.copy(old_populations)

    #Elen
    def save_state(self):
        pass

# create new landscape from the file 'my_land'
env = Landscape('my_land')

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
