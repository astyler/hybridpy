__author__ = 'astyler'
import math

class IdealBattery(object):
    # forget voltage and consider battery as a bucket of wH
    def __init__(self, max_energy_wh=10000.0, voltage=90, name='ideal'):
        self.max_energy_wh = max_energy_wh
        self.voltage = voltage 
        self.name = name

    def compute_voltage(self, soc_init):
        return self.voltage

    # Not used in SOC calculation, convenience for current normalization
    def compute_current(self, soc_init, power_out_W):
        voltage = self.compute_voltage(soc_init)
        return power_out_W / voltage

    # Power in Watts, Duration in seconds, SOC in [0, 1]
    def compute_delta_soc_and_current(self, soc_init, power_out_W, duration_s):
        current = self.compute_current(soc_init, power_out_W)
        return (- power_out_W * duration_s / 3600.0) / self.max_energy_wh, current

class QuadraticBattery(object):
    def __init__(self, u_min=3.25, u_max=3.9, amphours=5, cells=60, resistance=2.1/1000, name='quadratic'):
        self.u_max = cells*u_max
        self.u_min = cells*u_min
        self.q_max_h = amphours
        self.resistance = cells*resistance
        self.name = name

    def compute_voltage(self, soc):
        return self.u_min+(self.u_max-self.u_min)*soc

    def compute_current(self, soc_init, power_out_W):
        voltage = self.compute_voltage(soc_init)
        try:
            current_out_A = (voltage - math.sqrt(voltage*voltage - 4 * power_out_W * self.resistance)) / (2 * self.resistance)
        except ValueError:
            current_out_A = power_out_W / voltage

        return current_out_A

    def compute_delta_soc_and_current(self, soc_init, power_out_W, duration_s):
        current_out_A = self.compute_current( soc_init, power_out_W)
        delta_soc = (-current_out_A * duration_s / 3600) / self.q_max_h

        return delta_soc, current_out_A
