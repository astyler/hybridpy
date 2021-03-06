__author__ = 'astyler'
import math
from hybridpy.models.batteries import IdealBattery


class Vehicle(object):
    def get_power(self, speed_init, accleration, elevation, gradient, duration):
        return 0


class Car(Vehicle):
    def __init__(self, mass=1200, cross_area=1.988, drag_coefficient=0.31, rolling_resistance=0.015):
        self.mass = mass
        self.cross_area = cross_area
        self.drag_coefficient = drag_coefficient
        self.rolling_resistance = rolling_resistance

    def get_power(self, speed_init, acceleration, elevation, gradient, duration, outside_temperature=23):
        a_gravity = 9.81
        offset = 240
        ineff = 0.95
        regen_efficiency = 0.84
        pressure = 101325 * math.pow((1 - ((0.0065 * elevation) / 288.15)), ((a_gravity * 0.0289) / (8.314 * 0.0065)))
        rho = (pressure * 0.0289) / (8.314 * outside_temperature)
        air_resistance_coefficient = 0.5 * rho * self.cross_area * self.drag_coefficient

        # check behavior near 0
        theta = math.atan(gradient)
        f_sin = self.mass * a_gravity * math.sin(theta)
        f_cos = self.mass * a_gravity * math.cos(theta)

        # Rolling resistance dependent on the normal force
        rolling_resistance = self.rolling_resistance * f_cos

        air_resistance = air_resistance_coefficient * speed_init * speed_init
        f_net = self.mass * acceleration

        # Define fR to be sum of other forces
        f_resistance = air_resistance + rolling_resistance + f_sin
        f_motor = f_net + f_resistance

        if f_motor > 0:
            power = f_motor * speed_init / ineff
        else:
            power = f_motor * speed_init * ineff * regen_efficiency

        return power + offset

    # TODO: add in a real power -> fuel mapping
    def compute_fuel_rate(self, power_out_W, soc_init=0):
        return power_out_W/10000.0

class ElectricCar(Car):
    def __init__(self, battery=IdealBattery(), **kwargs):
        super(ElectricCar, self).__init__(**kwargs)
        self.battery = battery

    def compute_fuel_rate(self, power_out_W, soc_init):
        duration_s = 1.0
        delta_soc, current = self.battery.compute_delta_soc_and_current(soc_init, power_out_W, duration_s)
        return current


