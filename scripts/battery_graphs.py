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
        socs = [1]
        for i, p in enumerate(powers):
            prev_soc = socs[i]
            socs.append(prev_soc + batt.compute_delta_soc(soc_init=prev_soc, power=p, duration=1))

        plt.plot(socs, label=batt.name)

    plt.legend()
    plt.show()