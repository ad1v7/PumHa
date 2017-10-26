import numpy as np
from scipy.ndimage import convolve
import sys


class Landscape(object):
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

    #Load landscape from file, in to an array padded with a border of water.
    def load_landscape(self, filename):
        print('Loading landscape')
        return np.pad(np.loadtxt(filename, skiprows=1), ((1, 1), (1, 1)),
                      mode='constant', constant_values=0)


    #This gives every element of an array a value equal to the value of it's
    #neighbours multiplied by the kernel.  Since land is 1 and water is 0,
    #multiplying + neighbours by one gives the sum of the land neighbours
    #minus the diagals.  This means we can calculate this value just once.
    def find_dry_squares(self):
        print('calculating number of dry squares')
        kernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        return convolve(self.landscape, kernel, mode='constant')

    #Return tuples of all non-zero elements of landscape (ie, the land)
    def find_land_squares_indices(self):
        return np.transpose(np.nonzero(self.landscape))


