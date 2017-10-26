import numpy as np
import simplejson as json
from collections import OrderedDict


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
        self._land_idx = landscape_inp.land_indices

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
                                             diffusion, min_ro, max_ro, dt)
        self.kind = 'PumaPopulation'
        print('Puma population created')

    def update_density(self, populations_old, populations_new):
        # extract required populations density arrays for update
        P_new = self.find_density_arr(PumaPopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update all landscape ij
        for i,j in self._land_idx:
            P_new[i][j] = self.update_density_ij(i, j, P, H)

    def update_density_ij(self, i, j, P, H):
        b = self.birth
        m = self.death
        l = self.diffusion
        dt = self.dt
        N = self._N
        return P[i][j] + dt * (b * H[i][j] * P[i][j] - m * P[i][j]
                               + l * ((P[i - 1][j] + P[i + 1][j] + P[i][j - 1] +
                                       P[i][j + 1])
                                      - N[i][j] * P[i][j]))


class HarePopulation(Population):
    def __init__(self, Landscape, birth=.08, death=.04, diffusion=.02,
                 min_ro=0., max_ro=5., dt=.4):
        super(HarePopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt)
        print('Hare population created')
        self.kind = 'HarePopulation'

    def update_density(self, populations_old, populations_new):
        # extract required populations density arrays for update
        H_new = self.find_density_arr(HarePopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update all landscape ij
        for i,j in self._land_idx:
            H_new[i][j] = self.update_density_ij(i, j, P, H)

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



