from unittest import TestCase
from pumha.sim import Configuration, Landscape, PumaPopulation, HarePopulation


import numpy as np


LANDSCAPE = np.array([[0, 0, 0, 0],
                      [0, 1, 1, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1 ,0],
                      [0, 0, 0 ,0]
                     ])

N = np.array([[0, 1 ,1 ,0],
              [1, 2 ,1 ,1],
              [1, 1, 3, 0],
              [0, 2, 0, 0],
              [0, 0, 1, 0]
             ])

P = np.array([[0, 0, 0, 0],
              [0, 1.1, 1.9, 0],
              [0, 0.1, 0, 0],
              [0, 0, 2.6 ,0],
              [0, 0, 0 ,0]
             ])

H = np.array([[0, 0, 0, 0],
              [0, 3.1, 2.4, 0],
              [0, 3.1, 0, 0],
              [0, 0, 0.6 ,0],
              [0, 0, 0 ,0]
             ])

config = Configuration('pumha/data/config.dat')
env = Landscape('pumha/data/islands2.dat')
puma = PumaPopulation(env)
hare = HarePopulation(env)
pop_list = [hare, puma]

class TestPopulation(TestCase):
    def test_find_density_arr(self):
        arr = puma.find_density_arr(PumaPopulation, pop_list)
        self.assertTrue(isinstance(arr, np.ndarray))
        self.assertTrue(np.array_equal(arr, puma.density))
        # repeat with reversed list
        pop_list.reverse()
        arr = puma.find_density_arr(PumaPopulation, pop_list)
        self.assertTrue(isinstance(arr, np.ndarray))
        self.assertTrue(np.array_equal(arr, puma.density))

    def test_population_attributes(self):
        for pop in pop_list:
            self.assertIs(type(pop.min_ro), float)
            self.assertIs(type(pop.max_ro), float)
            self.assertIs(type(pop.birth), float)
            self.assertIs(type(pop.death), float)
            self.assertIs(type(pop.diffusion), float)
            self.assertIs(type(pop.dt), float)
            self.assertIs(type(pop.density), np.ndarray)
            self.assertIs(type(pop._N), np.ndarray)
            self.assertIs(type(pop._landscape), np.ndarray)
            self.assertTrue(pop.min_ro < pop.max_ro)
            self.assertTrue(pop.min_ro >= 0 and pop.max_ro >= 0)
            self.assertTrue(pop.birth >= 0 and pop.death >= 0)
            self.assertTrue(pop.diffusion >= 0)
            self.assertTrue(pop.dt >= 0)
            self.assertTrue(pop._N.shape == pop._landscape.shape)
            self.assertTrue(pop._N.shape == pop.density.shape)

    def test_load_config(self):
        birth = 0.2
        death = 0.3
        diffusion = 0.4
        dt = 0.5
        hare.load_config(birth, death, diffusion, dt)
        self.test_population_attributes()
        self.assertTrue(hare.birth == birth)
        self.assertTrue(hare.death == death)
        self.assertTrue(hare.diffusion == diffusion)
        self.assertTrue(hare.dt == dt)

    def test_puma_population_update_density_ij(self):
        b = .02
        m = .06
        l = .02
        dt = .4
        puma2 = PumaPopulation(env)
        puma2._landscape = LANDSCAPE
        puma2._N = N
        # test 1,2: 2nd row, 3rd column
        P_new_ij = puma2.update_density_ij(1, 2, P, H)
        P_test = 1.9+0.4*(0.02*1.9*2.4-0.06*1.9+0.02*((1.1)-1*1.9))
        self.assertAlmostEqual(P_new_ij, P_test)
        # test 1,1 : 2nd row, 2nd column
        P_new_ij = puma2.update_density_ij(1, 1, P, H)
        P_test = 1.1+0.4*(0.02*1.1*3.1-0.06*1.1+0.02*((1.9+0.1)-2*1.1))
        self.assertAlmostEqual(P_new_ij, P_test)

