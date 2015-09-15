__author__ = 'astyler'

# foobar


def compute_value_function(trip, init_soc, num_soc_states=1000, electricity_to_fuel_price_ratio=0.25,
                           sell_to_buy_ratio=0.8, gamma=1.0):
    """ Computes the value function for a trip
    :param trip: Trip dataframe with columns [TimeIndex (s), Gradient, Speed (m/s)]
    :param init_soc: Initial battery state of charge [0-1]
    :param num_soc_states: Resolution of SOC grid
    :param electricity_to_fuel_price_ratio: ratio of cost between electricity and fuel
    :param sell_to_buy_ratio: ratio of cost recovery at terminal state from selling excess SOC to grid
    :param gamma: single state decay rate for bellman equation
    :return: Value Function matrix [T x SOC], Q Matrix [T, SOC, Actions]
    """
    actions = carmodel.get_action_list()
    states = np.linspace(0, 1, num=num_soc_states)
    T = len(trip)

    q_function = np.empty(shape=(T, len(states), len(actions)))
    value_function = np.empty(shape=(T, len(states)))

    # Set terminal costs, reduce gain for selling electricity buy sell/buy ratio.
    value_function[T - 1] = [compute_terminal_cost(init_soc, soc, electricity_to_fuel_price_ratio, sell_to_buy_ratio)
                             for soc in states]

    # define default cost function
    cost_function = lambda l_fuel, l_time: l_fuel * l_time if l_fuel >= 0 else 1e6

    # backprop djikstras to compute value function
    for t in reversed(range(T - 1)):
        def nextvalue(x_query):
            fit = interp1d(states, value_function[t + 1], bounds_error=False)
            v_max_batt = value_function[t + 1][-1]
            return [1e6 if xq < 0 else v_max_batt if xq > 1 else yq for (xq, yq) in zip(x_query, fit(x_query))]

        time_period = trip.TimeIndex.iloc[t + 1] - trip.TimeIndex.iloc[t]

        powers, fuels = zip(*[__get_model_outputs(a, t, time_period, trip) for a in actions])

        for (idx, x) in enumerate(states):
            next_values = nextvalue([carmodel.new_soc(x, power, time_period) for power in powers])
            q_function[t][idx] = [cost_function(fuel, time_period) + gamma * nval for nval, fuel in
                                  zip(next_values, fuels)]

        value_function[t] = [min(qt_state) for qt_state in q_function[t]]

    # return J and Q
    return value_function, q_function