# visualization.py

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# Formatter function for y-axis to avoid scientific notation
def millions(x, pos):
    'The two args are the value and tick position'
    return '%1.1fM' % (x * 1e-6)

def plot_revenues(basic_strategy_annual, optimized_strategy_annual):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(basic_strategy_annual['Year'], basic_strategy_annual['Annual Revenue (£)'], label='Basic Strategy',
            marker='o')
    ax.plot(optimized_strategy_annual['Year'], optimized_strategy_annual['Annual Revenue (£)'],
            label='Optimized Strategy', marker='o')

    ax.set_xlabel('Year')
    ax.set_ylabel('Annual Revenue (£)')
    ax.set_title('Annual Revenues: Basic Strategy vs Optimized Strategy')
    ax.legend()
    ax.grid(True)

    # Apply formatter to y-axis to avoid scientific notation
    formatter = FuncFormatter(millions)
    ax.yaxis.set_major_formatter(formatter)

    plt.savefig('annual_revenues_comparison.png')
    plt.show()

def plot_daily_revenues(basic_strategy_daily, optimized_strategy_daily):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(optimized_strategy_daily['Datetime'], optimized_strategy_daily['Revenue (£)'], label='Optimized Strategy',
            linestyle='-', alpha=0.7)
    ax.plot(basic_strategy_daily['Date'], basic_strategy_daily['Revenue'], label='Basic Strategy', linestyle='-',
            alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Revenue (£)')
    ax.set_title('Daily Revenues: Basic Strategy vs Optimized Strategy')
    ax.legend()
    ax.grid(True)

    plt.savefig('daily_revenues_comparison.png')
    plt.show()
