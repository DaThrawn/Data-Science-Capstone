# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Hard-coded dropdown options for SpaceX launch sites
site_options = [
    {'label': 'All Sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
]

# ---------- Layout ----------
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown for Launch Site selection (default = ALL)
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Range slider for payload selection
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter chart showing payload vs. success (TASK 4 output)
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ---------- Callbacks ----------

# TASK 2: Pie chart callback
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        successes = (
            spacex_df[spacex_df['class'] == 1]
            .groupby('Launch Site')
            .size()
            .reset_index(name='success_count')
        )
        fig = px.pie(
            successes,
            values='success_count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = (
            site_df.groupby('class')
            .size()
            .reset_index(name='count')
            .replace({'class': {1: 'Success', 0: 'Failure'}})
            .rename(columns={'class': 'Outcome'})
        )
        fig = px.pie(
            outcome_counts,
            values='count',
            names='Outcome',
            title=f'Success vs. Failure for {entered_site}'
        )
        return fig


# TASK 4: Scatter chart callback (depends on dropdown + slider)
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Payload vs. Outcome for {selected_site}'
    else:
        title = 'Payload vs. Outcome for All Sites'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Booster Version'],
        title=title
    )
    return fig


# ---------- Run App ----------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=True)


