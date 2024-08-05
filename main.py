"""
This is the main file where the analysis comes together.

"""
# Insert functions from other .py files
from data_preprocessing import preprocess_data
from revenues import calculate_basic_strategy_revenues
from optimised_model import optimize_battery
from visualisation import plot_revenues, plot_daily_revenues, plot_cycle_comparison


def run_optimization(prices_data, cycles):
    result_df = optimize_battery(prices_data, 100, 50, 50, 0.92, 0.92, 0, 100, cycles)
    result_df.to_csv(f'optimized_results_cycles_{cycles}.csv', index=False)
    annual_revenues = result_df.groupby(result_df['Datetime'].dt.year)['Revenue (£)'].sum().reset_index(name='Annual Revenue (£)')
    annual_revenues['Year'] = annual_revenues['Datetime']
    return result_df, annual_revenues


if __name__ == "__main__":
    file_name = 'input_data.csv'
    prices_data = preprocess_data(file_name)

    # Calculate revenues for the baseline strategy
    daily_revenue_df, annual_revenue_df = calculate_basic_strategy_revenues(prices_data, capacity=100, power=100,
                                                                            round_trip_eff=0.85)

    # Run the optimization for cycle 1
    result_df_cycle1, annual_opt_revenues_cycle1 = run_optimization(prices_data, cycles=1)

    # Run the optimization for cycle 2
    result_df_cycle2, annual_opt_revenues_cycle2 = run_optimization(prices_data, cycles=2)

    # Plot revenues
    plot_revenues(annual_revenue_df, annual_opt_revenues_cycle1)
    plot_daily_revenues(daily_revenue_df, result_df_cycle1)
    plot_cycle_comparison(annual_opt_revenues_cycle1, annual_opt_revenues_cycle2)
