from unittest import TestCase
import numpy as np
from pumha.env import Landscape
from pumha.pop import (PumaPopulation,
                       HarePopulation,
                       Configuration)


land_arr = np.array([[0, 0, 0, 0],
                     [0, 1, 1, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 0]])

dry_squares = np.array([[0, 1, 1, 0],
                        [1, 2, 1, 1],
                        [1, 1, 3, 0],
                        [0, 2, 0, 0],
                        [0, 0, 1, 0]])

P_density = np.array([[0, 0, 0, 0],
                      [0, 1.1, 1.9, 0],
                      [0, 0.1, 0, 0],
                      [0, 0, 2.6, 0],
                      [0, 0, 0, 0]])

H_density = np.array([[0, 0, 0, 0],
                      [0, 3.1, 2.4, 0],
                      [0, 3.1, 0, 0],
                      [0, 0, 0.6, 0],
                      [0, 0, 0, 0]])

# create new landscape
env = Landscape('pumha/test/data/test_land.dat')
# add arrays so we know what to expect
env.landscape = np.copy(land_arr)
env.dry_squares = np.copy(dry_squares)
env.land_indices = [(1, 1), (1, 2), (2, 1), (3, 2)]
# create puma and hare populations
# and add density arrays for testing
puma = PumaPopulation(env)
puma.density = np.copy(P_density)
hare = HarePopulation(env)
hare.density = np.copy(H_density)
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

    # check is halo of zeros in the hare density array not updated
    def test_hare_update_density_boundary(self):
        pop_list_new = np.copy(pop_list)
        hare.update_density(pop_list, pop_list_new)
        self.assertTrue(zero_surrounded(hare.density))
        # reset to original so no issues for other tests
        hare.density = np.copy(H_density)

    # check is halo of zeros in the puma density array not updated
    def test_puma_update_density_boundary(self):
        pop_list_new = np.copy(pop_list)
        puma.update_density(pop_list, pop_list_new)
        self.assertTrue(zero_surrounded(puma.density))
        # reset to original so no issues for other tests
        puma.density = np.copy(P_density)

    def test_puma_population_update_density_ij(self):
        b = .02
        m = .06
        l = .2
        dt = .4
        # test 1,2: 2nd row, 3rd column
        P = puma.density
        H = hare.density
        P_new_ij = puma.update_density_ij(1, 2, P, H)
        P_test = 1.9+dt*(b*1.9*2.4-m*1.9+l*((1.1)-1*1.9))
        self.assertAlmostEqual(P_new_ij, P_test)
        # test 1,1 : 2nd row, 2nd column
        P_new_ij = puma.update_density_ij(1, 1, P, H)
        P_test = 1.1+dt*(b*1.1*3.1-m*1.1+l*((1.9+0.1)-2*1.1))
        self.assertAlmostEqual(P_new_ij, P_test)

    def test_hare_population_update_density_ij(self):
        r = .08
        a = .04
        k = .2
        dt = .4
        # test 1,2: 2nd row, 3rd column
        P = puma.density
        H = hare.density
        H_new_ij = hare.update_density_ij(1, 2, P, H)
        H_test = 2.4 + dt * (r * 2.4 - a * 2.4 * 1.9 + k *((3.1) - 1 * 2.4))
        self.assertAlmostEqual(H_new_ij, H_test)
        # test 1,1 : 2nd row, 2nd column
        H_new_ij = hare.update_density_ij(1, 1, P, H)
        H_test = 3.1 + dt * (r * 3.1 - a * 3.1 * 1.1 + k * ((2.4 + 3.1) -
                                                            2 * 3.1))
        self.assertAlmostEqual(H_new_ij, H_test)

    def test_random_density(self):
        for pop in pop_list:
            # check that grids are numpy arrays
            self.assertTrue(isinstance(pop.random_density(env), np.ndarray))
            # check that the output array is the same shape as the landscape
            self.assertTrue(
                pop.random_density(env).shape == env.landscape.shape)
            # check that no nonzero density was assigned to the water squares
            self.assertAlmostEqual(env.landscape[env.landscape == 0].all(),
                                   pop.random_density(env)[
                                       pop.random_density(env) == 0].all())
            # check that all the random densities are between min_ro and max_ro
            self.assertTrue(pop.min_ro <= pop.random_density(env)[
                pop.random_density(env) != 0].all() <= pop.max_ro)


# return True if all matrix perimeter (boundary) elements are zeros
def zero_surrounded(array):
    return not (array[0, :].any() or array[-1, :].any() or array[:, 0].any()
                or array[:, -1].any())

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

config = Configuration('pumha/test/data/config.dat')


class Test_Configuration(TestCase):
    def test_load_from_file(self):
        #Test a properly formatted config loads properly
        self.assertEqual(config.hare_birth, default["Hare_birth"])
        self.assertEqual(config.hare_predation, default["Hare_predation"])
        self.assertEqual(config.hare_diffusion, default["Hare_diffusion"])
        self.assertEqual(config.puma_birth, default["Puma_birth"])
        self.assertEqual(config.puma_mortality, default["Puma_mortality"])
        self.assertEqual(config.puma_diffusion, default["Puma_diffusion"])
        self.assertEqual(config.time_step, default["Time_step"])
        self.assertEqual(config.steps, default["Steps"])
        self.assertEqual(config.output_interval, default["Output_interval"])

        #Test empty config input
        with self.assertRaises(SystemExit) as cm:
            Configuration('pumha/test/data/config_empty.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test broken key name
        with self.assertRaises(SystemExit) as cm:
            Configuration('pumha/test/data/config_keytest.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test missing key name
        with self.assertRaises(SystemExit) as cm:
            Configuration('pumha/test/data/config_missingkey.dat')
        self.assertEqual(cm.exception.code, 1)
