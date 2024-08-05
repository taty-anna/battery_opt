"""
This is the main file where the analysis comes together.

"""
# Insert functions from other .py files
from data_preprocessing import preprocess_data
from revenues import calculate_basic_strategy_revenues
from optimised_model import optimize_battery
from vis_tool_dash import app
from visualisation import plot_revenues


if __name__ == "__main__":
    file_name = 'input_data.csv'  # Open original price data
    prices_data = preprocess_data(file_name)  # Clean the price data using pre-developed function

    # Calculate revenues for the baseline strategy
    daily_revenue_df, annual_revenue_df = calculate_basic_strategy_revenues(prices_data, capacity=100, power=100,
                                                                            round_trip_eff=0.85)

    # Run the optimization (counter-strategy proposed)
    cycles = 1  # Specify number of cycles - 1 OR 2

    # Run the model
    result_df = optimize_battery(prices_data, 100, 50, 50,
                                 0.92, 0.92, 0, 100, cycles)

    # Save results to CSV
    result_df.to_csv(f'optimized_results_cycles_{cycles}.csv', index=False)
    result_df.info()

    # Group by year based on the 'Datetime' column and sum the 'Revenue (£)' column
    annual_opt_revenues = result_df.groupby(result_df['Datetime'].dt.year)['Revenue (£)'].sum()

    # Save CSV file with annual revenues from the optimised model, /
    # file name will adjust accordingly to the cycles chosen
    annual_opt_revenues.to_csv(f'annual_opt_results_cycles_{cycles}.csv', index=False)

    # Plot revenues comparing baseline and optimised strategies
    plot_revenues(annual_revenue_df, annual_opt_revenues)

    # Run the Dash Plotly visualisation tool - Run in browser 'http://127.0.0.1:8050'
    app.run_server(host='127.0.0.1', port=8050, debug=True)
