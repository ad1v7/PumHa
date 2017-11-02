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
        #Test a properly formatted map loads properly
        self.assertTrue(np.array_equal(land_arr, env.landscape))

        #Test missing map
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('')
        self.assertEqual(cm.exception.code, 1)

        #Test broken map input
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_broken.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test string input map
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_datatype_s.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test non-binary (min)
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_bin_min.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test non-binary (max)
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_bin_max.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test mixed data type file
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_datatype_mix.dat')
        self.assertEqual(cm.exception.code, 1)

        #Test empty data type file
        with self.assertRaises(SystemExit) as cm:
            test_map = Landscape('pumha/test/data/test_land_empty.dat')
        self.assertEqual(cm.exception.code, 1)

    def test_find_dry_squares(self):
        self.assertTrue(np.array_equal(dry_squares, env.dry_squares))

    def test_find_land_squares_indices(self):
        self.assertTrue(np.array_equal(land_indices, env.land_indices))

