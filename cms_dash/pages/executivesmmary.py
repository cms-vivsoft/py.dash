import os
from shutil import copyfile
from datetime import date, datetime
import json
import pandas as pd
import numpy as np

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

# import data_pipeline
# import sql_queries
# from vault.prototype_map_config import config
from cms_dash.DataQueryHelper2 import DataQueryHelper
from cms_dash.S3DataManager import S3DataManager
from app import app

DATA_DIRECTORY = "data/"

dropdown_style = {'color': 'black'}

# data_helper = DataQueryHelper(
#     file_name=os.path.join('data', 'data_exploration_lite.csv'))

s3_mgr = S3DataManager()
df_all_raw = s3_mgr.load_data(
    'data_exploration_lite.csv', # key name in s3 path; the bucket name was defined in S3DataManager
    os.path.join(DATA_DIRECTORY, 'data_exploration_lite.csv') # local path
)
df_all = df_all_raw


def graph_vessel_type():
    plot_data = df_all.groupby(
        ['group'])['mmsi'].nunique().reset_index()
    fig = px.sunburst(
        plot_data,
        path=['group'],
        values='mmsi',
        color='group',
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.layout.update(
        margin=dict(l=2, r=2, b=2, t=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig


def graph_top_vessels():
    vessel_data = df_all.groupby(['mmsi', 'coverage'])[
        'timestamp'].count().reset_index()
    top_vessels = vessel_data[vessel_data['coverage'] == 1].sort_values(
        by='timestamp', ascending=False).head(15)
    top_vessels = top_vessels.sort_values(by='timestamp', ascending=True)
    # bot10_vessels = vessel_data[vessel_data['coverage'] == 1].sort_values(by='timestamp', ascending=True).head(10)
    # bot10_vessels = bot10_vessels.sort_values(by='timestamp', ascending=False)

    fig = px.bar(top_vessels, x='timestamp', y='mmsi', orientation='h',
                 labels={'mmsi': 'Beneficier ID', 'timestamp': 'Number of Claims'},
                 template='plotly_dark',
                 )
    fig.update_yaxes(type='category')
    fig.update_traces(marker_color='rgba(31, 119, 180, .3)')
    fig.layout.update(
        margin=dict(r=6, b=6, t=6, l=6),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def graph_satellite_type():
    plot_data = df_all.groupby(
        ['industry'])['sat_id'].nunique().reset_index()
    fig = px.sunburst(
        plot_data,
        path=['industry'],
        values='sat_id',
        color='industry',
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    fig.layout.update(
        margin=dict(r=2, b=2, t=2, l=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def graph_top_satellites():
    sat_data = df_all.groupby(['sat_id', 'coverage'])[
        'mmsi'].count().reset_index()
    top_sats = sat_data[sat_data['coverage'] == 1].sort_values(
        by='mmsi', ascending=False).head(15)
    top_sats = top_sats.sort_values(by='mmsi', ascending=True)
    # bot10_sats = sat_data[sat_data['coverage'] == 1].sort_values(by='mmsi', ascending=True).head(10)
    # bot10_sats = bot10_sats.sort_values(by='mmsi', ascending=False)

    fig = px.bar(top_sats, x='mmsi', y='sat_id', orientation='h',
                 labels={'mmsi': 'Number of Claim', 'sat_id': 'Facility ID'},
                 template='plotly_dark',
                 )
    fig.update_yaxes(type='category')
    fig.update_traces(marker_color='rgba(44, 160, 44, .3)')
    fig.layout.update(
        margin=dict(r=6, b=6, t=6, l=6),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def map_vessels_and_sats():
    plot_data = df_all[
        (df_all['coverage'] == 1) | (
            df_all['coverage'] == 0)
    ].reset_index(drop=True).copy()

    temp = plot_data[['sat_id', 'timestamp',
                      'sat_lat', 'sat_lon', 'coverage']].copy()
    temp.columns = ['mmsi', 'timestamp', 'lat', 'lon', 'coverage']
    temp['type'] = [
        'Type 1' if x == 1 else 'Type 2' for x in temp.coverage]
    temp = temp.drop_duplicates(keep='first').reset_index(drop=True)

    plot_data = plot_data[['mmsi', 'timestamp', 'lat', 'lon', 'coverage']]
    plot_data = plot_data.drop_duplicates(keep='first').reset_index(drop=True)
    plot_data['type'] = 'Type 0'

    plot_data = plot_data.groupby(
        ['mmsi', 'timestamp', 'type']).mean().reset_index()
    plot_data = plot_data.append(
        temp.groupby(['mmsi', 'timestamp', 'type']).mean().reset_index()).reset_index(drop=True)

    fig = px.scatter_mapbox(
        plot_data, lat='lat', lon='lon', color='type',
        category_orders={
            'type': ['Vessel', 'Type 1', 'Type 2']},
        color_discrete_map={
            'Type 0': 'rgba(31, 119, 180, 0.6)',
            'Type 1': 'rgba(44, 160, 44, 0.6)',
            'Type 2': 'rgba(148, 103, 189, 0.4)'
        },
        zoom=1.5, center={'lat': 26.35, 'lon': -169.2},
        mapbox_style='carto-darkmatter',
        template='plotly_dark'
    )
    fig.layout.update(
        margin=dict(l=2, r=2, t=2, b=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            yanchor='top',
            y=0.95,
            xanchor='right',
            x=0.99,
            traceorder='normal',
            font=dict(size=12, color='white'),
            bgcolor='rgba(255,255,255,.3)',
            bordercolor='rgba(255,255,255,.35)',
            borderwidth=1,
        )
    )
    for i, item in enumerate(fig.data):
        if 'Miss' in item['name']:
            fig.data[i]['visible'] = 'legendonly'

    return fig


def graph_hits_over_time(plot_data):
    fig = px.bar(
        plot_data, x='timestamp', y='mmsi',
        labels={'mmsi': 'Number of Claims', 'timestamp': 'Time'},
        template='plotly_dark',
    )
    fig.update_traces(marker_color='rgba(44, 160, 44, .3)')
    fig.layout.update(
        margin=dict(r=6, b=6, t=6, l=6),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


@app.callback(
    Output('vessel-type', 'figure'),
    Output('top-vessels', 'figure'),
    Output('top-satellites', 'figure'),
    Output('vessel-sat-map', 'figure'),
    Output('n-vessel-filter', 'children'),
    Output('n-satellite-filter', 'children'),
    Output('total-hits', 'figure'),
    Output('satellite-type', 'figure'),
    Input('satellite-type', 'clickData'),
    Input('vessel-type', 'clickData'),
    Input('time-slider', 'value'),
    Input('reset-satellite-type', 'n_clicks'),
    Input('reset-vessel-type', 'n_clicks'),
)
def filter_vessel_type(satClickData, vesClickData, sliderValue, resetSatClicks, resetVesClicks):
    # filter_data = data_helper.RAW_DATA.copy()
    filter_data = df_all_raw.copy()

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'satellite-type' in changed_id:
        S3DataManager.filteredSatData = True

    if 'reset-satellite-type' in changed_id:
        S3DataManager.filteredSatData = False

    if 'vessel-type' in changed_id:
        S3DataManager.filteredVesData = True

    if 'reset-vessel-type' in changed_id:
        S3DataManager.filteredVesData = False

    # if 'satellite-type' in changed_id and satClickData:
    if satClickData and S3DataManager.filteredSatData:
        click_path = satClickData['points'][0]['id']
        filter_data = filter_data[filter_data['industry']
                                  == click_path].reset_index(drop=True)

    # if 'vessel-type' in changed_id and vesClickData:
    if vesClickData and S3DataManager.filteredVesData:
        click_path = vesClickData['points'][0]['id']
        filter_data = filter_data[filter_data['group']
                                  == click_path].reset_index(drop=True)

    # get new hits figure
    hits_fig = graph_hits_over_time(filter_data[filter_data['coverage'] == 1].groupby([
                                    'timestamp']).count()['mmsi'].reset_index())

    # filter to current time point
    filter_time = sorted(filter_data['timestamp'].unique())[sliderValue]
    filter_data = filter_data[filter_data['timestamp']
                              == filter_time].reset_index(drop=True)

    # data_helper.DATA = filter_data
    df_all = filter_data

    return [
        graph_vessel_type(),
        graph_top_vessels(),
        graph_top_satellites(),
        map_vessels_and_sats(),
        'Claim Type Distribution ({0} Total)'.format(df_all['mmsi'].nunique()),
        'Facility Type Distribution ({0} Total)'.format(
            df_all['sat_id'].nunique()),
        hits_fig,
        graph_satellite_type(),
    ]




data_explore_body = html.Div([dbc.Row(
    [
        # side bar
        dbc.Col(
            dbc.Card([
                # first-row:
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Summary'),
                            dbc.CardBody([
                                html.P([
                                    """
                                    This dashboard hosts data from a 4-hour time window from 14:00 to 18:00 on January 15, 2015 for the purpose of data exploration.
                                    """])
                            ])
                        ])
                        
                    ], width=12
                    )
                ]), 

                # second-row:
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Configurations'),
                            dbc.CardBody([
                                html.H6("Location"),
                                dcc.Dropdown(
                                    options=[
                                        {'label': 'New York City', 'value': 'NYC'},
                                        {'label': 'Montréal', 'value': 'MTL'},
                                        {'label': 'San Francisco', 'value': 'SF'}
                                    ],
                                    multi=True,
                                    value="MTL"
                                ), 
                                html.P(""),
                                html.P(""),
                                html.P(""),                                
                                html.H6('''
                                Calculation Method
                                '''),
                                dcc.RadioItems(
                                    options=[
                                        {'label': ' Linear', 'value': 'NYC'},
                                        {'label': ' Log', 'value': 'MTL'}
                                    ],
                                    value='MTL',
                                    labelStyle={'display': 'block'}
                                )            

                            ])
                        ])                        
                    ], width=12
                    )
                ])                
            ]
            ), md=3
        ),

        # body
        dbc.Col(
            dbc.Card([
                # first-row:
                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader('Total Claims Over Time'),
                            dcc.Graph(
                                # style={'height': '350px'},
                                id='total-hits',
                            )
                        ]), width=6
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader('Claims Location'),
                            dcc.Graph(
                                id='vessel-sat-map',
                            ),
                            html.Div([html.H6('January 15, 2015')],style={'margin':'5px 0px 2px 10px'}),
                            html.Div([
                                dcc.Slider(
                                    min=0,
                                    max=(df_all['timestamp'].nunique() - 1),
                                    step=None,
                                    marks={
                                        i:x for i, x in enumerate(sorted(pd.to_datetime(df_all['timestamp'].unique()).strftime('%H:%M')))
                                    },
                                    value=0,
                                    included=False,
                                    id='time-slider',
                                ),
                            ],
                            style={'width':'95%', 'margin':'0px 2px 0px 10px'}
                            ),
                        ]),
                        width=6
                    )
                ]),
                # second-row:
                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader([
                                html.Nobr(['Facility Types Distribution ({0} Total)'.format(0)], id='n-satellite-filter'),
                                html.Nobr(
                                    html.Button(
                                        id='reset-satellite-type',
                                        n_clicks=0,
                                        children='Reset',
                                        disabled=False,
                                        style={'float': 'right'}
                                    ),
                                )
                            ]),
                            dcc.Graph(
                                figure=graph_satellite_type(),
                                style={'height': '250px'},
                                id='satellite-type'
                            )
                        ]),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader([
                                html.Nobr(['Claim Types Distribution ({0} Total)'.format(0)], id='n-vessel-filter'),
                                html.Nobr(
                                    html.Button(
                                        id='reset-vessel-type',
                                        n_clicks=0,
                                        children='Reset',
                                        disabled=False,
                                        style={'float': 'right'}
                                    ),
                                )
                            ]),
                            dcc.Graph(
                                style={'height': '250px'},
                                id='vessel-type'
                            )
                        ]),
                        width=6
                    )
                    
                ]),
                # third-row:
                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                        dbc.CardHeader('Top Facility'),
                        dcc.Graph(
                            figure=graph_top_satellites(),
                            style={'height': '250px'},
                            id='top-satellites'
                        )
                        ])
                    ),
                    dbc.Col(
                        dbc.Card([
                        dbc.CardHeader('Top Claims'),
                        dcc.Graph(
                            figure=graph_top_vessels(),
                            style={'height': '250px'},
                            id='top-vessels'
                        )
                    ])
                    )                    
                ])

            ]), md=9
        )


    ]
)

])

data_explore_header = dbc.Row([
    dbc.Col(
        html.H4("Claim Intelligence")
    )
])

data_explore_layout = dbc.Container(children=[
    data_explore_header,
    data_explore_body    
], fluid=True, id="data-explore")


layout = data_explore_layout
