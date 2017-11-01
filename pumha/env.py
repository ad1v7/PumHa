from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import numpy as np
from scipy.ndimage import convolve
import sys


class Landscape(object):
    """ Class for instantiating a simulation landscape

    Class checks that a valid landscape file exists, before then
    loading it in to a padded array, representing a guaranteed empty
    water-halo around the land).  The number of land (1) tiles around
    water (0) tiles is then calculated for each array element so this
    can be used in future calculations, instead of evaluated every time.
    Finally, a list of indices is provided for land elements.
    :ivar filename: name of file holding the landscape array
    :type filename: string
    """
    def __init__(self, filename):
        #Check if the landscape exists.
        try:
            my_file = open(filename)
        except IOError:
            print('No such landscape file.')
            sys.exit(1)

        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()
        self.land_indices = self.find_land_squares_indices()

    def load_landscape(self, filename):
        """Load the landscape as a numpy array, from a file.

        Loads an array of 1's for land and 0's for water in to a numpy
        array, from the parsed filename.  The array should start on the
        second line of the file; the first line contains the size but
        that is irrelevant in our implementation so the first line is
        skipped in the loading.  The array is padded with a border of
        0's, so that the land is always contained.

        Before loading it is checked that the file can be loaded as a
        numpy and then after, ensures that the entries are 1 or 0.
        In the even that either of these checks is failed, loading
        will be considered failed, and the simulation ended.

        :param filename: name of file containing land array
        :type filename: string
        :return: padded landscape array
        :rtype: integer array
        """
        print('Loading landscape')
        
        try:
            new_map = np.pad(np.loadtxt(filename, skiprows=1), ((1, 1), (1, 1)),
                      mode='constant', constant_values=0)
        except ValueError:
            print("Value error in landscape file.")
            print("Please ensure the landscape contains only 0 and 1 entries.")
            sys.exit(1)

        new_map = np.pad(np.loadtxt(filename, skiprows=1), ((1, 1), (1, 1)),
                      mode='constant', constant_values=0)

        if np.array_equal(new_map, new_map.astype(bool)) == False:
            print("Value error in landscape file.")
            print("Please ensure the landscape contains only 0 and 1 entries.")
            sys.exit(1)

        return new_map

    def find_dry_squares(self):
        """Counts the number of dry squares around each array element.

        This gives every element of an array a value equal to the sum of it's
        neighbours multiplied by the kernel.  Since land is 1 and water is 0,
        multiplying cardinal neighbours by one and summing gives the total land
        in the cardinal directions.

        Example:

        Land:   0 1 0    Kernel:    0 1 0
                0 1 1               1 0 1
                0 0 0               0 1 0

        for entry (1,1), the kernel will multiply elements

            (0,1), (1,0), (1,2), (2,1) by 1 (from the kernel)
            and everything else by 0.

            In the land this corresponds to

            (1*1), (0*1), (1*1), (0*1) = 1 + 0 + 1 + 0 = 2

        We calculate this value just once and store it to reduce
        computation.

        :return: array of summed neighbours
        :rtype: integer array
        """
        print('calculating number of dry squares')
        kernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        return convolve(self.landscape, kernel, mode='constant')

    def find_land_squares_indices(self):
        """Return tuples of all non-zero elements of landscape (ie, the land)

        Find the non-zero elements of the landscape array and then
        transpose them in to an array of tuples.  This allows for just
        iterating over the land elements in later calculations, which
        are the only one's which can have a non-zero value.

        :param filename: name of file containing land array
        :type filename: string
        :return: list of indices for zon-zero (land) landscape array elements
        :rtype: [int, int] list
        """
        return np.transpose(np.nonzero(self.landscape))


