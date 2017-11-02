'''Population module

The module contains two classes::

    Configuration
    Population

and two subclasses of the Population class::

    HarePopulation(Population)
    PumaPopulation(Population)

The Configuration class consists of several methods for handling and parsing
the input files and Population class with its subclasses are responsible
for doing all the maths in the density change dynamics.

'''


from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import numpy as np
import simplejson as json
import jsonschema
import sys
import os
from jsonschema import validate
from collections import OrderedDict


class Configuration():
    """ Class for loading simulation parameters

    Class checks that a valid configuration file has been parsed as an
    argument and if not, creates a default one. If a config file is given by
    the user, it is checks if it contains a valid JSON object for the
    simulation, then loads it as the configuration data and does few more data
    validation checks.

    :ivar filename: name of file holding the configuration JSON
    :type filename: string
    """
    def __init__(self, config_file):

        if config_file is None:
            directory = os.path.dirname(os.path.abspath(__file__))
            default_file = os.path.join(directory, "data/default.dat")

            try:
                self.load_from_file(default_file)
            except IOError:
                print("\nNo default config file found")
                self.create_config(default_file)
                self.load_from_file(default_file)

            print("\nDefault config file loaded:\n%s\n" % default_file)

        else:
            try:
                self.valid_config(config_file)
                config = self.load_from_file(config_file)
                print("\nConfig file loaded:\n%s\n" %
                      os.path.abspath(config_file))

            except IOError:
                print("Config file does not exist:\n%s" % os.path.abspath(config_file))
                sys.exit(1)

    def load_from_file(self, config_file):
        """Load the configuration file as a JSON object and check
        that the loaded object has all the correct keys.

        :param config_file: Name of file containing coniguration
        :type config_file: String
        """
        with open(config_file, 'r') as f:
            # Check is config file valid json format
            try:
                config = json.load(f, object_pairs_hook=OrderedDict)
            except ValueError:
                print("Config file is not of json type")
                sys.exit(1)

        for key in config:
            value = config[key]
            print("{} ({})".format(key, value))

        try:
            self.hare_birth = config["Hare_birth"]
            self.hare_predation = config["Hare_predation"]
            self.hare_diffusion = config["Hare_diffusion"]
            self.puma_birth = config["Puma_birth"]
            self.puma_mortality = config["Puma_mortality"]
            self.puma_diffusion = config["Puma_diffusion"]
            self.time_step = config["Time_step"]
            self.steps = config["Steps"]
            self.output_interval = config["Output_interval"]

        except KeyError, e:
            print("Wrong key name in a config file:\n %s" % str(e))
            print('Try \'pumha --help\' for help')
            sys.exit(1)

   def create_config(self, config_file):
        """Create a default configuration file with some standard values

        This method is primarily used as a default when no file
        is parsed to a simulation, but is also called when a config
        file is passed with an error, so users will have a working 
        file which they can edit with their own settings.

        :param config_file: Name of file containing coniguration
        :type config_file: String
        """
        default = {
            'Hare_birth': 0.08,
            'Hare_predation': 0.04,
            'Hare_diffusion': 0.2,
            'Puma_birth': 0.02,
            'Puma_mortality': 0.06,
            'Puma_diffusion': 0.2,
            'Time_step': 0.4,
            'Steps': 100,
            'Output_interval': 8
        }

        try:
            with open(config_file, 'w') as outfile:
                json.dump(default, outfile, sort_keys=True, indent=4*' ')
                print("New config file created:\n%s\n" % config_file)
        except:
            print("Something went wrong...")
            raise

    def valid_config(self, config_file):
        """Checks that the configuration file is a JSON file in
        the correct format by comparing it to an expected schema.

        :param config_file: Name of file containing coniguration
        :type config_file: String
        """
        schema = {
            "type" : "object",
            "properties" : {
                "Hare_birth" : {"type" : "number"},
                "Hare_predation" : {"type" : "number"},
                "Hare_diffusion" : {"type" : "number"},
                "Puma_birth" : {"type" : "number"},
                "Puma_mortality" : {"type" : "number"},
                "Puma_diffusion" : {"type" : "number"},
                "Time_step" : {"type" : "number"},
                "Steps" : {"type" : "number"},
                "Output_interval" : {"type" : "number"},
            },
        }

        with open(config_file, 'r') as f:
            config = json.load(f, object_pairs_hook=OrderedDict)
        try:
            validate(config, schema)
        except jsonschema.exceptions.ValidationError as ve:
            print('Invalid configuration file format.:\n%s' % str(ve))
            print('Try \'pumha --help\' for help')
            sys.exit(1)


class Population(object):
    """ Base class for creating specific population classes

    Class stores instance attributes and provides methods which can be used by
    for derived subclasses. It is not intended to be used on its own, but
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
        """Assign a random density between min_ro and max_ro to every land square

        Returns a grid with a random density assigned
        between minimum and maximum densities for every land square.
        :param landscape_inp: Instance of a Landscape object
        :type landscape_inp: Landscape
        :return: a 2D array of random densities
        :rtype: numpy.ndarray of float64 type
        """
        min_ro = self.min_ro
        max_ro = self.max_ro
        grid = landscape_inp.landscape.astype(np.float)
        # assigning a random density to every land square
        grid[grid == 1] = np.random.uniform(min_ro, max_ro,
                                            grid[grid == 1].shape)
        return grid

    def load_config(self, birth, death, diffusion, dt):
        """Set instance attributes using provided parameters

        :param birth: birth rate of a given population
        :type birth: float
        :param death: death rate of a given population
        :type death: float
        :param diffusion: diffusion rate of a given population
        :type diffusion: float
        :param dt: timestep in arbitrary units
        :type dt: float
        """
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        self.dt = dt

    def find_density_arr(self, pop_class, pop_list):
        """Return required population density array from a list of populations

        Returns density array of a first found element matching pop_class from
        a list of provided populations. If no element is found, it returns
        matrix of zeros.
        :param pop_class: required population object
        :type pop_class: extended Population class
        :param pop_list: list of all populations
        :type pop_list: list
        :return: required population density array (array of zeros if not found)
        :rtype: numpy.ndarray of float64 type
        """
        rows, cols = self.density.shape
        return next((p.density for p in pop_list if
                     isinstance(p, pop_class)), np.zeros((rows, cols),
                                                         dtype=float))


class PumaPopulation(Population):
    """Puma population class with its specific update method

    This class represents puma population living in some landscape, therefore it
    requires Landscape object as a parameter. Remaining parameters are set to
    defaults and can be changed later by either using provided method load_config
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
        where
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
        :type P: numpy.ndarray of a float64 type
        :param H: density array of hares
        :type H: numpy.ndarray of a float64 type
        :return: updated density i, j square
        :rtype: float
        """
        b = self.birth
        m = self.death
        l = self.diffusion
        dt = self.dt
        N = self._N
        p_ij = P[i][j] + dt * (b * H[i][j] * P[i][j] - m * P[i][j]
                               + l * ((P[i - 1][j] + P[i + 1][j] + P[i][j - 1]
                                       + P[i][j + 1]) - N[i][j] * P[i][j]))
        return p_ij if p_ij > 0 else 0.


class HarePopulation(Population):
    """Hare population class with its specific update method

    This class represents hare population living in some landscape, therefore it
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
        where
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
        h_ij = H[i][j] + dt * (r * H[i][j] - a * H[i][j] * P[i][j]
                               + k * ((H[i - 1][j] + H[i + 1][j] + H[i][j - 1]
                                       + H[i][j + 1]) - N[i][j] * H[i][j]))
        return h_ij if h_ij > 0 else 0.
