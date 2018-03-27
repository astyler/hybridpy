__author__ = 'astyler'

from hybridpy.learning import dynamicprogramming
from hybridpy.dataset import triploader
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == '__main__':
    sns.set_style('whitegrid')
    trip = triploader.load('/Users/astyler/projects/ChargeCarData/thor/thor20100226_0.csv')
    controls = [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000]
    v, q, p, d = dynamicprogramming.compute(trip=trip, controls=controls)

    plt.figure()
    plt.imshow(v.T[::-1])#cmap='RdBu_r')

    plt.show()