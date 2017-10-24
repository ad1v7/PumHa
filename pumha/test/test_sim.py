from unittest import TestCase
from pumha import sim
import numpy

class TestPopulation(TestCase):
    def test_find_density_arr(self):
        config = sim.Configuration('pumha/data/config.dat')
        env = sim.Landscape('pumha/data/islands2.dat')
        puma = sim.PumaPopulation(env)
        hare = sim.PumaPopulation(env)
        pop_list = [hare, puma]
        pop = puma.find_density_arr(sim.PumaPopulation, pop_list)
        self.assertTrue(isinstance(pop, numpy.ndarray))

