"""
This script uses Dash to create interactive visualizations that help in understanding the analysis results.

Two graphs are being generated: Line chart showing charge and discharge prices and bar chart showing revenues produced
by the second strategy. This tool adds flexibility to choose desired frequencies: day, month, year.

"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data for both cycles
data_cycle_1 = pd.read_csv("optimized_results_cycles_1.csv")
data_cycle_1['Datetime'] = pd.to_datetime(data_cycle_1['Datetime'])

data_cycle_2 = pd.read_csv("optimized_results_cycles_2.csv")
data_cycle_2['Datetime'] = pd.to_datetime(data_cycle_2['Datetime'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout with a darker theme and button-like dropdowns
app.layout = html.Div([
    html.H1("Battery Energy Storage Dashboard", style={'color': '#FFFFFF', 'backgroundColor': '#333333'}),

    # Container for dropdowns styled as buttons
    html.Div([
        # Dropdown for selecting data frequency for Graphs (Price and Revenues)
        dcc.Dropdown(
            id='frequency-dropdown',
            options=[
                {'label': 'Day', 'value': 'D'},
                {'label': 'Month', 'value': 'M'},
                {'label': 'Year', 'value': 'Y'}
            ],
            value='D',  # Default value set to Day
            multi=False,
            style={'color': '#000000', 'display': 'inline-block', 'width': '48%', 'margin-right': '1%'}
        ),

        # Dropdown for selecting the number of cycles
        dcc.Dropdown(
            id='cycle-dropdown',
            options=[
                {'label': '1 Cycle', 'value': 1},
                {'label': '2 Cycles', 'value': 2}
            ],
            value=1,  # Default value set to 1 cycle
            multi=False,
            style={'color': '#000000', 'display': 'inline-block', 'width': '48%'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '20px'}),

    # Line Chart for Prices
    dcc.Graph(id='price-chart'),

    # Bar Chart for Revenues
    dcc.Graph(id='revenue-chart')
], style={'backgroundColor': '#333333', 'color': '#FFFFFF', 'padding': '10px'})


# Callback to update the Price and Revenue charts based on the selected frequency and cycles
@app.callback(
    [Output('price-chart', 'figure'),
     Output('revenue-chart', 'figure')],
    [Input('frequency-dropdown', 'value'),
     Input('cycle-dropdown', 'value')]
)
def update_charts(selected_frequency, selected_cycle):
    if selected_cycle == 1:
        df = data_cycle_1
    else:
        df = data_cycle_2

    df_resampled = df.resample(selected_frequency, on='Datetime').sum().reset_index()

    # Create the line chart for prices
    price_chart = px.line(df_resampled, x='Datetime', y=['Charge Price (£/MWh)', 'Discharge Price (£/MWh)'],
                          title="Prices Over Time",
                          labels={'Datetime': 'Time', 'value': '£/MWh'},
                          height=400)
    price_chart.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    # Create the bar chart for revenues
    revenue_chart = px.bar(df_resampled, x='Datetime', y='Revenue (£)',
                           title="Revenue Over Time",
                           labels={'Datetime': 'Time', 'value': '£'},
                           height=400)
    revenue_chart.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    return price_chart, revenue_chart


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8050, debug=True)
