__author__ = 'astyler'
import math


class Battery(object):
    state_of_charge = 0
    name = 'skeleton'
    def apply_power(self, power, duration):
        return 0


class IdealBattery(Battery):
    # Forget voltage and consider battery as a bucket of KwH
    name = 'ideal'
    def __init__(self, max_energy=10000.0, init_energy=0):
        self.max_energy = max_energy
        self.state_of_charge = init_energy / max_energy

    # Power in Watts, Duration in seconds, SOC in [0, 1]
    def apply_power(self, power, duration):
        self.state_of_charge += -(power * duration / 3600.0) / self.max_energy
        return self.state_of_charge


class QuadraticBattery(Battery):
    name = 'quadratic'
    def __init__(self, u_min=3.25, u_max=3.9, amphours=50, cells=50, resistance=2.1/1000):
        self.u_max = cells*u_max
        self.u_min = cells*u_min
        self.q_max = amphours
        self.resistance = cells*resistance

    def get_voltage(self):
        return self.u_min+(self.u_max-self.u_min)*self.state_of_charge

    def apply_power(self, power, duration):
        voltage = self.get_voltage()
        # p = i * v; p = i * ( v - i*r); 0 = -r*i^2 + v*i - p
        current = - (voltage - math.sqrt(voltage*voltage - 4 * power * self.resistance) ) / (2 * self.resistance)

        self.state_of_charge += (current * duration / 3600) / self.q_max
        return self.state_of_charge



