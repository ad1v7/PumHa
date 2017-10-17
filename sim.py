import numpy as np
     

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

# ToDo
# where N array is comming from?
# where dT is stored?
# apart from that it is almost there...

class PumaPopulation(Population):
    def __init__(self, Landscape, birth=.02, death=.06, diffusion=.02,
                 min_ro=0., max_ro=5.):
        super(PumaPopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro)
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
        return P[i][j] + dT * (b * H[i][j] * P[i][i] - m * P[i][j]
                               + l * ((P[i-1][j] + P[i+1][j] + P[i][j-1] + P[i][j+1])
                                      - N[i][j] * P[i][j]))

class HarePopulation(Population):
    def __init__(self, Landscape, birth=.08, death=.04, diffusion=.02,
                 min_ro=0., max_ro=5.):
        super(HarePopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro)
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
        return H[i][j] + dT * (r * H[i][j] - a * H[i][j] * P[i][j]
                               + k * ((H[i-1][j] + H[i+1][j] + H[i][j-1] + H[i][j+1])
                                      - N[i][j] * H[i][j]))



class Simulation():
    def __init__(self, Landscape, *args):
        # create populations list but ignore args which are not populations
        self.populations = [pop for pop in args if isinstance(pop, Population)]

    # not sure is this function required
    def add_population(self, pop):
        self.populations.append(pop)

    # not sure is this function required
    def remove_population(self, pop):
        self.populations.remove(pop)

    def update(self, old_populations, populations):
        for pop in populations:
            pop.update_density(old_populations, populations)

    def run(self, num_steps):
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

# create new population using default values
puma_pop = PumaPopulation(env)
print(puma_pop.birth)
print(puma_pop.death)
print(puma_pop.max_ro)
print('#######')

# create new population using specific values (config file...)
hare_pop = HarePopulation(env)
print(hare_pop.birth)
print(hare_pop.death)
print(hare_pop.max_ro)

# create new simulation with the landscape env and puma population
sim = Simulation(env, puma_pop)
# update one step
#sim.run(20)
