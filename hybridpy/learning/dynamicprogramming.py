__author__ = 'astyler'

import numpy as np
from scipy.interpolate import interp1d
from hybridpy.models import vehicles, batteries


def compute(trip, controls, soc_states=50, gamma=1.0,
            cost_function=lambda fuel_rate, power, duration: fuel_rate * duration, vehicle=vehicles.Car(),
            battery=batteries.QuadraticBattery()):
    """ Computes the value function and q function for a given trip and optimization parameters
    :param trip: Trip dataframe containing speed, acceleration, elevation, and gradient features
    :param controls: discrete list of allowed controls for the engine power output
    :param soc_states: scalar number of state of charge states (resolution)
    :param gamma: discount factor in bellman equation
    :param cost_function: cost function for input arguments: fuel_rate, power, duration
    :param vehicle: vehicle model to generate power outputs from speed, acceleration, gradient
    :param battery: battery model to compute SOC change for given power loads
    :return: value_function, q_function, power list, duration list
    """
    
    socs = np.linspace(0, 1, num=soc_states)
    time_states = len(trip)

    q_function = np.zeros(shape=(time_states, soc_states, len(controls)))
    value_function = np.zeros(shape=(time_states, soc_states))

    powers = []
    durations = []

    for t in xrange(0, time_states - 1):
        state = trip.iloc[t]
        duration = trip.ElapsedSeconds.iloc[t + 1] - state.ElapsedSeconds
        power = vehicle.get_power(speed_init=state.SpeedFilt, acceleration=state.Acceleration, elevation=state.ElevationFilt,
                                  gradient=state.GradientRaw, duration=duration)
        powers.append(power)
        durations.append(duration)

    # value function terminal state value is 0 for all charges.  consider adding in price of electricity to fill battery

    # backprop djikstras to compute value function
    for t in xrange(time_states - 2, -1, -1):
        next_value_slice = interp1d(socs, value_function[t + 1])
        power_demand = powers[t]
        duration = durations[t]

        def cost_to_go(soc):
            if soc < 0:
                return np.nan # can't pull energy when battery empty, return inf ctg
            elif soc > 1:
                return value_function[t + 1][-1] # can't charge above max, return value at max
            else:
                return next_value_slice(soc) # return cost to go of next slice

        for (i, soc) in enumerate(socs):
            # control is power supplied from the ICE, battery makes up the difference
            costs_to_go = [cost_to_go(soc + battery.compute_delta_soc_and_current(soc, power_demand - control, duration)[0]) for
                           control in controls]
            q_function[t][i] = [
                cost_function(vehicle.compute_fuel_rate(control, soc), power_demand - control, duration) + (gamma * ctg) for
                ctg, control in zip(costs_to_go, controls)]

        value_function[t] = [np.nanmin(q) for q in q_function[t]]

    return value_function, q_function, powers, durations