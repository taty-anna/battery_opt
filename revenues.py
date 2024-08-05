"""
This script is responsible for calculating revenues using the baseline strategy below.

Baseline strategy: every day buy 100 MWh of energy at the **hour** with the lowest price
and sell 100 MWh of energy at the hour with the highest price.

Specs for simulation:
* power = 100 MW
* capacity = 100 MWh
* round-trip efficiency = 85%
* the average daily cycles (full charge and discharge) in each year are less or equal to 1.

This strategy involves limiting the battery to one full discharge cycle per day,
but ensuring that the battery charges fully before it discharges.

"""
import pandas as pd

def calculate_basic_strategy_revenues(df, capacity, power, round_trip_eff):
    """
    Calculate daily and annual revenues based on the baseline strategy.

    :return: Two DataFrames, one with detailed daily revenues and one with summarized annual revenues.
    """

    df['time'] = pd.to_datetime(df['time'])
    # Resample to hourly - necessary since we are trading at the hour
    hourly_prices = df.set_index('time').resample('H').mean()

    # Function to calculate daily revenue
    # One daily cycle: the battery is charged when the energy is bought (min price) \
    # and discharged when the energy is sold (max price).
    def calculate_daily_revenue(day):
        min_price_time = day['prices'].idxmin()
        max_price_time = day['prices'].idxmax()
        min_price = day.loc[min_price_time, 'prices']
        max_price = day.loc[max_price_time, 'prices']
        price_diff = max_price - min_price
        # No revenue if discharging occurs before charging
        revenue = price_diff * capacity * round_trip_eff if min_price_time < max_price_time else 0
        return {'Max Price': max_price, 'Min Price': min_price, 'Price Difference': price_diff, 'Revenue': revenue}

    # Calculate daily revenues/group by day
    daily_revenues = hourly_prices.groupby(hourly_prices.index.date).apply(calculate_daily_revenue)

    # Prepare daily DataFrame
    daily_revenues = pd.DataFrame(daily_revenues.tolist(), index=pd.to_datetime(daily_revenues.index))
    daily_revenues['Date'] = daily_revenues.index

    # Calculate annual revenues
    # Group by year and sum to get annual revenue
    annual_revenues = daily_revenues.groupby(daily_revenues['Date'].dt.year)['Revenue'].sum()

    # Prepare annual DataFrame
    annual_revenues_df = annual_revenues.to_frame(name='Annual Revenue (£)')
    annual_revenues_df['Year'] = annual_revenues_df.index   # set year to index

    # Normalize annual revenue to $/kW/hr
    annual_revenues_df['Annual Revenue per kW (£/kW/yr)'] = annual_revenues_df['Annual Revenue (£)'] / (power * 1000)
    annual_revenues_df.reset_index(drop=True, inplace=True)  # reset index back

    # Save the result DataFrames to CSV
    daily_revenues.to_csv('daily_revenues.csv', index=False)
    annual_revenues_df.to_csv('annual_revenues.csv', index=False)

    return daily_revenues, annual_revenues_df



