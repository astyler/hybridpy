__author__ = 'astyler'
import math

class IdealBattery(object):
    # forget voltage and consider battery as a bucket of KwH
    def __init__(self, max_energy=10000.0, name='ideal'):
        self.max_energy = max_energy
        self.name = name

    # Power in Watts, Duration in seconds, SOC in [0, 1]
    def compute_delta_soc(self, soc_init, power, duration):
        return (- power * duration / 3600.0) / self.max_energy

class QuadraticBattery(object):
    def __init__(self, u_min=3.25, u_max=3.9, amphours=50, cells=50, resistance=2.1/1000, name='quadratic'):
        self.u_max = cells*u_max
        self.u_min = cells*u_min
        self.q_max = amphours
        self.resistance = cells*resistance
        self.name = name

    def compute_voltage(self, soc):
        return self.u_min+(self.u_max-self.u_min)*soc

    def compute_delta_soc(self, soc_init, power, duration):
        voltage = self.compute_voltage(soc_init)
        try:
            current = - (voltage - math.sqrt(voltage*voltage - 4 * power * self.resistance)) / (2 * self.resistance)
        except ValueError:
            current = - power / voltage

        delta_soc = (current * duration / 3600) / self.q_max

        return delta_soc
