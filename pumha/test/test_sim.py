from unittest import TestCase
import os
from pumha.env import Landscape
from pumha.pop import (PumaPopulation,
                       HarePopulation)
from pumha.sim import Simulation
from pumha.sim import create_output_dir

env = Landscape('pumha/test/data/test_land.dat')
hare = HarePopulation(env)
puma = PumaPopulation(env)


class TestSimulation(TestCase):
    def test_create_output_dir(self):
        newdir = create_output_dir()
        self.assertTrue(os.path.exists(newdir))
        os.rmdir(newdir)

    def test_add_population(self):
        sim = Simulation()
        self.assertTrue(len(sim.populations) == 0)
        sim.add_population(hare)
        self.assertTrue(len(sim.populations) == 1)
        sim.add_population(puma)
        self.assertTrue(len(sim.populations) == 2)

    def test_remove_population(self):
        sim = Simulation(hare, puma)
        self.assertTrue(len(sim.populations) == 2)
        sim.remove_population(hare)
        self.assertTrue(len(sim.populations) == 1)
        sim.remove_population(puma)
        self.assertTrue(len(sim.populations) == 0)
        # try to remove one too many populations...
        text = sim.remove_population(puma)
        if "No such a population in" in text:
            test = True
        self.assertTrue(test)
