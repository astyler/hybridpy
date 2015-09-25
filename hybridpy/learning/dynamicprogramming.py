__author__ = 'astyler'

import numpy as np
from scipy.interpolate import interp1d

from hybridpy.models import vehicles, batteries


def compute(trip, controls, soc_states=50, gamma=1.0,
            cost_function=lambda fuel_rate, power, duration: fuel_rate * duration, vehicle=vehicles.Car(),
            battery=batteries.QuadraticBattery()):
    
    socs = np.linspace(0, 1, num=soc_states)
    time_states = len(trip)

    q_function = np.zeros(shape=(time_states, soc_states, len(controls)))
    value_function = np.zeros(shape=(time_states, soc_states))

    powers = []
    durations = []

    for t in xrange(0, time_states - 1):
        state = trip.iloc[t]
        duration = trip.ElapsedSeconds.iloc[t + 1] - state.ElapsedSeconds
        power = vehicle.get_power(speed_init=state.Speed, acceleration=state.Acceleration, elevation=state.Elevation,
                                  gradient=state.Gradient, duration=duration)
        powers.append(power)
        durations.append(duration)

    # value function terminal state value is 0 for all charges.  consider adding in price of electricity to fill battery

    # backprop djikstras to compute value function
    for t in xrange(time_states - 2, -1, -1):
        next_value_slice = interp1d(socs, value_function[t + 1], bounds_error=False)
        power_demand = powers[t]
        duration = durations[t]

        def cost_to_go(soc):
            if soc < 0:
                return np.inf
            elif soc > 1:
                return value_function[t + 1][-1]
            else:
                return next_value_slice(soc)

        for (i, soc) in enumerate(socs):
            # control is power supplied from the ICE
            costs_to_go = [cost_to_go(soc + battery.compute_delta_soc(soc, power_demand - control, duration)) for
                           control in controls]
            q_function[t][i] = [
                cost_function(vehicle.compute_fuel_rate(control), power_demand - control, duration) + gamma * ctg for
                ctg, control in zip(costs_to_go, controls)]

        value_function[t] = [np.nanmin(q) for q in q_function[t]]

    return value_function, q_function, powers, durations