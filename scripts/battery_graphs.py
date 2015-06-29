__author__ = 'astyler'

import matplotlib.pyplot as plt
import hybridpy.models.batteries as bmodels
import numpy as np
import seaborn as sns

if __name__ == '__main__':
    sns.set_style('whitegrid')
    batts = [bmodels.IdealBattery(), bmodels.QuadraticBattery()]

    powers = np.abs(np.random.randn(80)*15000)
    plt.figure()
    for batt in batts:
        batt.state_of_charge = 1
        socs = [batt.apply_power(p, 1) for p in powers]
        plt.plot(socs, label=batt.name)

    plt.legend()
    plt.show()