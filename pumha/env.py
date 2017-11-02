"""Environment module
The module contains one class::

    Landscape

The module creates a Landscape object which holds all the landscape-related
information, such as the actual landscape grid array, information about
the number of neighbouring dry squares to each square and indices of land
squares.
"""


from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)
import sys
import numpy as np
from scipy.ndimage import convolve


class Landscape(object):
    """ Class for instantiating a simulation landscape

    Class checks that a valid landscape file exists, then loads it into a
    numpy array. The array will be padded with zeros around the
    given landscape. The number of land squares (represented by 1) around
    every square is then calculated for each array element and this
    information is saved into a new numpy array, so this can be used in future
    calculations.
    Finally, a list of indices is provided for land elements. When updating
    the population densities, this list of indices is used to avoid having to
    loop over water squares.

    :ivar filename: name of file holding the landscape array
    :type filename: string
    """
    def __init__(self, filename):
        # Check if the landscape exists.
        try:
            open(filename)
        except IOError:
            print('No such landscape file.')
            sys.exit(1)

        self.landscape = self.load_landscape(filename)
        self.dry_squares = self.find_dry_squares()
        self.land_indices = self.find_land_squares_indices()

    def load_landscape(self, filename):
        """Load the landscape as a numpy array from a file

        Loads an array of 1-s for land and 0-s for water in to a numpy
        array from the parsed filename. The array should start on the
        second line of the file (the first line contains the size, so it is
        skipped in the loading). The method pads the array with a border of
        0-s, so that the land is always surrounded by water.
        Before loading the landscape, the mehtod checks that the file can be
        loaded as a numpy array and then ensures that all entries are either 1
        or 0. If either of these checks fails, the simulation will terminate.

        :param filename: name of file containing land array
        :type filename: string
        :return: padded landscape array
        :rtype: integer array
        """
        print('Loading landscape')

        # ensure the file has isn't empty.
        with open(filename) as f:
            linecount = sum(1 for line in open(filename))
            if linecount < 2:
                print("No landscape found")
                sys.exit(1)

        try:
            new_map = np.pad(np.loadtxt(filename, skiprows=1),
                             ((1, 1), (1, 1)),
                             mode='constant',
                             constant_values=0)
        except ValueError:
            print("Value error in landscape file.")
            print("Please ensure the landscape contains only 0 and 1 entries.")
            sys.exit(1)

        new_map = np.pad(np.loadtxt(filename, skiprows=1),
                         ((1, 1), (1, 1)),
                         mode='constant',
                         constant_values=0)

        if np.array_equal(new_map, new_map.astype(bool)) is False:
            print("Value error in landscape file.")
            print("Please ensure the landscape contains only 0 and 1 entries.")
            sys.exit(1)

        return new_map

    def find_dry_squares(self):
        """Counts the number of dry squares around each array element

        Assigns to every element of an array a value equal to the sum of it's
        neighbours multiplied by the kernel (see example). Since land squares
        have value 1 and water squares have value 0,  multiplying cardinal
        neighbours by one and summing gives the total land in the cardinal
        directions.

        Example::

            Land:   0 1 0    Kernel:    0 1 0
                    0 1 1               1 0 1
                    0 0 0               0 1 0

        For entry (1,1), the kernel will multiply elements
        (0,1), (1,0), (1,2), (2,1) by 1 (from the kernel)
        and everything else by 0.
        In the land this corresponds to \
        (1*1), (0*1), (1*1), (0*1) = 1 + 0 + 1 + 0 = 2 \
        We calculate this value just once and store it to reduce computation.

        :return: array of summed neighbours
        :rtype: integer array
        """
        print('calculating number of dry squares')
        kernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        return convolve(self.landscape, kernel, mode='constant')

    def find_land_squares_indices(self):
        """Return tuples of all non-zero elements of landscape

        Find the non-zero elements of the landscape array and then
        transpose them in to an array of tuples.  This allows for just
        iterating over the land elements in later calculations,
        significantly reducing the computation.

        :param filename: name of file containing land array
        :type filename: string
        :return: list of indices for zon-zero (land) landscape array elements
        :rtype: [int, int] list
        """
        return np.transpose(np.nonzero(self.landscape))
