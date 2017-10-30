from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
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
    """ Base class for creating specific population classes

    Class stores instance attributes and provides methods which are universal
    for derived subclasses. It is not intended to be used on its own rather it
    should be extended by specific population subclasses (e.g. PumaPopulation)

    :ivar min_ro: minimum density per ij square in the density array
    :type min_ro: float
    :ivar max_ro: maximum density per ij square in the density array
    :type max_ro: float
    :ivar birth: birth rate for a given population
    :type birth: float
    :ivar death: death rate for a given population
    :type death: float
    :ivar diffusion: diffusion rate for a given population
    :type diffusion: float
    :ivar dt: time step in arbitrary units
    :type dt: float
    :ivar density: population density in a given landscape \
            initialized at random
    :type density: numpy.ndarray containing data with float64 type
    """

    def __init__(self, landscape_inp, birth, death,
                 diffusion, min_ro, max_ro, dt):
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
        """Assing a random density between min_ro and max_ro to every land square

        The method uses the Landscape object to return a grid where there
        is assigned a random density between minimum and maximum densities for
        every land square.

        :param landscape_inp: Instance of a Landscape object
        :type landscape_inp: Landscape
        :return: a 2D array of random densities
        :rtype: numpy.ndarray containing data with float64 type

        """
        min_ro = self.min_ro
        max_ro = self.max_ro
        # turning the array of integers into an array of floats
        grid = landscape_inp.landscape.astype(np.float32)
        # assigning a random density to every cell between min_ro and max_ro
        grid[grid == 1] = np.random.uniform(min_ro, max_ro,
                                            grid[grid == 1].shape)
        return grid

    def load_config(self, birth, death, diffusion, dt):
        """Set instance attributes using provided parameters

        :param birth: birth rate for a given population
        :type birth: float
        :param death: death rate for a given population
        :type death: float
        :param diffusion: diffusion rate for a given population
        :type diffusion: float
        :param dt: time step in arbitrary units
        :type dt: float
        """
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.dt = dt

    def find_density_arr(self, pop_class, pop_list):
        """Return required population density array from a list of populations

        Returns density array of a first found element matching pop_class from
        a list of provided populations. If no element is found it returns
        density matrix of zeros.

        :param pop_class: required population object
        :type pop_class: Extended Population class
        :param pop_list: list of all populations
        :type pop_list: list
        :return: required population density array (array of zeros if not found)
        :rtype: numpy.ndarray of float type
        """
        rows, cols = self.density.shape
        return next((p.density for p in pop_list if
                     isinstance(p, pop_class)), np.zeros((rows, cols),
                                                         dtype=float))


class PumaPopulation(Population):
    """Puma population class with its specific update method

    This class represents puma population living in some landscape therefore it
    requires Landscape object as a parameter. Remaining parameters are set to
    defaults and can be changed later either using provided method load_config
    or by simply assigning required values to instance attributes.

    :Example:

        Create puma population using default values

        >>> from pumha.pop import PumaPopulation
        >>> from pumha.env import Landscape
        >>> land = Landscape('my_land_file.dat')
        >>> puma = PumaPopulation(land)

        Create puma population using specifig values

        >>> from pumha.pop import PumaPopulation
        >>> from pumha.env import Landscape
        >>> land = Landscape('my_land_file.dat')
        >>> puma = PumaPopulation(land, birth=0.03, death=0.01)

    :See Also:

    pumha.pop.Population
    """

    def __init__(self, Landscape, birth=.02, death=.06, diffusion=.2,
                 min_ro=0., max_ro=5., dt=.4):
        super(PumaPopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt)
        self.kind = 'PumaPopulation'
        print('Puma population created')

    def update_density(self, populations_old, populations_new):
        """Update density array of puma population instance

        Method updates entire density array of puma population instance based
        on densities of current populations living in a landscape. Only land
        squares in the density array are updated.

        :param populations_old: list of populations at current timestep
        :type populations_old: list of Population type
        :param populations_new: list of populations with updated \
                density array at t+dt
        :type populations_new: list of Population type
        """
        # extract required populations density arrays for update
        P_new = self.find_density_arr(PumaPopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update all landscape ij
        for i, j in self._land_idx:
            P_new[i][j] = self.update_density_ij(i, j, P, H)

    def update_density_ij(self, i, j, P, H):
        """Return updated puma density at one (i,j) square

        Method implements discrete approximation of the following equation:

        .. math::
            \\frac{\partial P}{\partial t} = bHP-mP+l(\\frac{\partial^2 P} \
                    {\partial x^2} + \\frac{\partial^2 P}{\partial y^2})

        where,

        * P = density of pumas
        * H = density of hares
        * b = birth rate of pumas
        * m = death rate of pumas
        * l = diffusion rate of pumas

        :param i: density array row number (first row is i=0)
        :type i: int
        :param j: density array column number (first column is j=0)
        :type j: int
        :param P: density array of pumas
        :type P: numpy.ndarray of float type
        :param H: density array of hares
        :type H: numpy.ndarray of float type
        :return: updated density i, j square
        :rtype: float
        """
        b = self.birth
        m = self.death
        l = self.diffusion
        dt = self.dt
        N = self._N
        return P[i][j] + dt * (b * H[i][j] * P[i][j] - m * P[i][j]
                               + l * ((P[i - 1][j] + P[i + 1][j] + P[i][j - 1]
                                       + P[i][j + 1]) - N[i][j] * P[i][j]))


class HarePopulation(Population):
    """Hare population class with its specific update method

    This class represents hare population living in some landscape therefore it
    requires Landscape object as a parameter. Remaining parameters are set to
    defaults and can be changed later either using provided method load_config
    or by simply assigning required values to instance attributes. For example
    use see PumaPopulation.

    *See Also*
        * pumha.pop.Population
        * pumha.pop.PumaPopulation
    """

    def __init__(self, Landscape, birth=.08, death=.04, diffusion=.2,
                 min_ro=0., max_ro=5., dt=.4):
        super(HarePopulation, self).__init__(Landscape, birth, death,
                                             diffusion, min_ro, max_ro, dt)
        print('Hare population created')
        self.kind = 'HarePopulation'

    def update_density(self, populations_old, populations_new):
        """Update density array of hare population instance

        Method updates entire density array of hare population instance based
        on densities of current populations living in a landscape. Only land
        squares in the density array are updated.

        :param populations_old: list of populations at current timestep
        :type populations_old: list of Population type
        :param populations_new: list of populations with updated \
                density array at t+dt
        :type populations_new: list of Extended Population type
        """
        # extract required populations density arrays for update
        H_new = self.find_density_arr(HarePopulation, populations_new)
        P = self.find_density_arr(PumaPopulation, populations_old)
        H = self.find_density_arr(HarePopulation, populations_old)

        # update all landscape ij
        for i, j in self._land_idx:
            H_new[i][j] = self.update_density_ij(i, j, P, H)

    def update_density_ij(self, i, j, P, H):
        """Return updated hare density at one (ij) square

        Method implements discrete approximation of the following equation:

        .. math::
            \\frac{\partial H}{\partial t} = rH-aHP+k(\\frac{\partial^2 H} \
            {\partial x^2} + \\frac{\partial^2 H}{\partial y^2})

        where,

        * P = density of pumas
        * H = density of hares
        * r = birth rate of hares
        * a = death rate of hares
        * k = diffusion rate of hares

        :param i: density array row number (first row is i=0)
        :type i: int
        :param j: density array column number (first column is j=0)
        :type j: int
        :param P: density array of pumas
        :type P: numpy.ndarray of float type
        :param H: density array of hares
        :type H: numpy.ndarray of float type
        :return: updated density ij square
        :rtype: float

        """

        r = self.birth
        a = self.death
        k = self.diffusion
        dt = self.dt
        N = self._N
        return H[i][j] + dt * (r * H[i][j] - a * H[i][j] * P[i][j]
                               + k * ((H[i - 1][j] + H[i + 1][j] + H[i][j - 1]
                                       + H[i][j + 1]) - N[i][j] * H[i][j]))
