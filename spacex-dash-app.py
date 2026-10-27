
# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].dropna().unique()
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches
    # If a specific launch site is selected, show Success vs Failed counts
    html.Div(
        dcc.Graph(id='success-pie-chart')
    ),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            i: str(i) for i in range(0, 10001, 1000)
        },
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation
    # between payload and launch success
    html.Div(
        dcc.Graph(id='success-payload-scatter-chart')
    )
])


# TASK 2:
# Add a callback function for site-dropdown as input,
# success-pie-chart as output

@app.callback(
    Output(
        component_id='success-pie-chart',
        component_property='figure'
    ),
    Input(
        component_id='site-dropdown',
        component_property='value'
    )
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        # Show successful launch counts for all launch sites
        filtered_df = spacex_df[
            spacex_df['class'] == 1
        ]

        fig = px.pie(
            filtered_df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )

    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        # Count successful and failed launches
        outcome_counts = (
            filtered_df['class']
            .map({0: 'Failure', 1: 'Success'})
            .value_counts()
            .reindex(['Success', 'Failure'], fill_value=0)
            .reset_index()
        )

        outcome_counts.columns = ['Outcome', 'Count']

        fig = px.pie(
            outcome_counts,
            names='Outcome',
            values='Count',
            title=f'Launch Outcomes for {entered_site}'
        )

    return fig


# TASK 4:
# Add a callback function for site-dropdown and payload-slider
# as inputs, success-payload-scatter-chart as output

@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(
            component_id='site-dropdown',
            component_property='value'
        ),
        Input(
            component_id='payload-slider',
            component_property='value'
        )
    ]
)
def get_scatter_chart(entered_site, payload_range):

    # Get the selected payload limits
    low, high = payload_range

    # Filter data by payload range
    filtered_df = spacex_df[
        spacex_df['Payload Mass (kg)'].between(low, high)
    ].copy()

    # Check whether all sites or a specific site is selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload Mass vs. Launch Outcome',
        labels={
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'class': 'Launch Outcome',
            'Booster Version Category': 'Booster Version'
        }
    )

    # Label the y-axis with launch outcomes
    fig.update_yaxes(
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['Failure (0)', 'Success (1)']
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8051)
