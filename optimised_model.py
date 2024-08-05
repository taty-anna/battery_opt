"""
This script proposes and simulates an alternative trading strategy, focusing on optimizing battery usage for
better efficiency and profitability.

This strategy considers similar specifications suggested in baseline strategy,
but it also takes into account state of charge because it helps understand the remaining capacity of a battery.
Constraints are clarified below.

"""

import pandas as pd
import numpy as np
import pulp

def optimize_battery(df, max_capacity, charge_power_limit, discharge_power_limit,
                     charge_efficiency, discharge_efficiency, min_soc, max_soc, cycles):

    # Convert 'datetime' column to datetime object and set as index
    df['datetime'] = pd.to_datetime(df['time'])
    df.set_index('datetime', inplace=True)

    # Create the LP problem
    model = pulp.LpProblem("Battery Optimization", pulp.LpMaximize)

    # Define decision variables
    charge_power = pulp.LpVariable.dicts("Charge", df.index, 0, charge_power_limit)
    discharge_power = pulp.LpVariable.dicts("Discharge", df.index, 0, discharge_power_limit)
    soc = pulp.LpVariable.dicts("SoC", df.index, min_soc * max_capacity, max_soc * max_capacity)

    # Objective Function - Maximize Profit (charge at lower prices, discharge at higher prices)
    model += pulp.lpSum([(df.loc[t, 'prices'] * discharge_power[t] / discharge_efficiency) -
                         (df.loc[t, 'prices'] * charge_power[t] * charge_efficiency)
                         for t in df.index])
    for t in df.index:
        model += soc[t] <= 100   # state of charge is set to less or equal to 100

    daily_charge_limit = daily_discharge_limit = 50 * cycles  # daily charge limit  = 100 MWh per day

    # 'all_days' is obtaining all unique days from the DataFrame 'df' index.
    # 'df.index.normalize()' normalizes the datetime index to midnight,
    # thereby stripping the time part and retaining only the date part.
    all_days = df.index.normalize().unique()

    # 'list_of_days' is splitting the DataFrame 'df' into smaller chunks.
    # The DataFrame is being divided into 2677 parts. This splitting is
    # for processing or analysis purposes, to handle data day-by-day.
    list_of_days = np.array_split(df, 2677)
    c = 0 # Initializing a counter 'c' to 0. This will be used to iterate through 'list_of_days'.
    for day in all_days:  # Iterating over each unique day in 'all_days'.

        # Extracting the index (which are timestamps) of each chunk in 'list_of_days'.
        daily_periods = list(list_of_days[c].index)

        # Constraint: ensures the sum of charge power over all periods in a day
        # (multiplied by 0.5, possibly to convert to hours) does not exceed the daily charge limit.
        model += pulp.lpSum([charge_power[t] * 0.5 for t in daily_periods]) <= daily_charge_limit
        # Constraint: ensures the sum of discharge power over all periods in a day
        # does not exceed the daily discharge limit.
        model += pulp.lpSum([discharge_power[t] * 0.5 for t in daily_periods]) <= daily_discharge_limit
        c += 1  # Incrementing the counter 'c' to move to the next chunk in the next iteration.

    # Constraints
    for i, t in enumerate(df.index):
        if i == 0:  # Initial state of charge
            # If it's the first timestamp, set the state of charge (soc) equal to half of the maximum capacity.
            model += soc[t] == max_capacity / 2
        else:  # Subsequent states of charge
            prev_t = df.index[i - 1]

            # Updates the state of charge (soc) for the current time 't'.
            # The new state of charge is equal to the previous state of charge plus
            # the charge added to the system minus the charge removed from the system
            model += soc[t] == soc[prev_t] + charge_power[prev_t] * charge_efficiency - (
                        discharge_power[prev_t] * discharge_efficiency)

    # Solve the model
    model.solve(pulp.PULP_CBC_CMD(msg=True))

    # Extract results
    output = {
        'Datetime': df.index,
        'Charging (MWh)': [charge_power[t].varValue for t in df.index],
        'Discharging (MWh)': [discharge_power[t].varValue for t in df.index],
        'State of Charge (MWh)': [soc[t].varValue for t in df.index],
        'Charge Price (£/MWh)': [df.loc[t, 'prices'] if charge_power[t].varValue > 0 else None for t in df.index],
        'Discharge Price (£/MWh)': [df.loc[t, 'prices'] if discharge_power[t].varValue > 0 else None for t in
                                    df.index],
        'Revenue (£)': [((df.loc[t, 'prices'] * discharge_power[t].varValue / discharge_efficiency) -
                         (df.loc[t, 'prices'] * charge_power[t].varValue * charge_efficiency)) for t in df.index]
    }

    dfopt = pd.DataFrame(output)
    return dfopt
