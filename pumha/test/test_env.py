from unittest import TestCase
import numpy as np

from pumha.env import Landscape

land_arr = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0],
                     [0, 0, 1, 1, 0],
                     [0, 1, 1, 1, 0],
                     [0, 0, 0, 0, 0]
                     ])

dry_squares = np.array([[0, 1, 0, 0, 0],
                        [1, 0, 2, 1, 0],
                        [0, 3, 2, 2, 1],
                        [1, 1, 3, 2, 1],
                        [0, 1, 1, 1, 0]
                        ])

land_indices = [(1,1),
                (2,2),
                (2,3),
                (3,1),
                (3,2),
                (3,3)]

env = Landscape('pumha/test/data/test_land.dat')


class TestLandscape(TestCase):

    def test_load_landscape(self):
        self.assertTrue(np.array_equal(land_arr, env.landscape))

    def test_find_dry_squares(self):
        self.assertTrue(np.array_equal(dry_squares, env.dry_squares))

    def test_find_land_squares_indices(self):
        self.assertTrue(np.array_equal(land_indices, env.land_indices))