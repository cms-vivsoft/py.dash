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
import plotly
import plotly.graph_objects as go
# import data_pipeline
# import sql_queries
# from vault.prototype_map_config import config
from cms_dash.DataQueryHelper2 import DataQueryHelper
from cms_dash.S3DataManager import S3DataManager
from app import app
from pandasql import sqldf

DATA_DIRECTORY = "data/"

dropdown_style = {'color': 'black'}

# data_helper = DataQueryHelper(
#     file_name=os.path.join('data', 'data_exploration_lite.csv'))

s3_mgr = S3DataManager()
#df_inpatient = s3_mgr.load_data('df_inpatient.csv')
df_inpatient = s3_mgr.load_data('df_inpatient.pkl')


def readmit_pctg():
    tmpdf = df_inpatient.loc[(df_inpatient.DESYNPUF_ID != 'xxxxxxxxxx'), ['ReadmissionDays', 'DESYNPUF_ID']]
    tmpdf['ReadmissionDays'] = tmpdf['ReadmissionDays'].dt.days
    temp1 = sqldf("""Select (count(distinct case when ReadmissionDays <=30 then DESYNPUF_ID end)) Num,
                  count(distinct DESYNPUF_ID) Denom
                  from tmpdf 
            where ReadmissionDays <> 'null' """)

    x = (temp1['Num'][0]/temp1['Denom'][0]) * 100
    x = round(x, 2)
    x = str(x)
    return x


def admit_cat_counts():

    tmpdf = df_inpatient.loc[(df_inpatient.ReadmissionDays.dt.days <= 30), ['AdmitCategory', 'DESYNPUF_ID', 'CLM_PMT_AMT', 'ReadmissionDays']]
    tmpdf['ReadmissionDays'] = tmpdf['ReadmissionDays'].dt.days
    h1 = sqldf("""
               SELECT AdmitCategory, COUNT(distinct DESYNPUF_ID) InpatientCount, AVG(CLM_PMT_AMT) ClaimsAmount
               FROM tmpdf WHERE ReadmissionDays <> 'null' AND ReadmissionDays <= 30
               GROUP BY AdmitCategory
               """)

    fig = px.bar(h1,
                 y="AdmitCategory",
                 x="InpatientCount",
                 orientation='h')

    fig.layout.update(
        margin=dict(l=2, r=2, b=2, t=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig

def admit_cat_avgs():
    # TODO - ask Ujval if this should be for all pts or just readmits
    tmpdf = df_inpatient.loc[(df_inpatient.ReadmissionDays.dt.days <= 30), ['AdmitCategory', 'DESYNPUF_ID', 'CLM_PMT_AMT', 'ReadmissionDays']]
    tmpdf['ReadmissionDays'] = tmpdf['ReadmissionDays'].dt.days
    h1 = sqldf("""
               SELECT AdmitCategory, COUNT(distinct DESYNPUF_ID) InpatientCount, AVG(CLM_PMT_AMT) ClaimsAmount
               FROM tmpdf WHERE ReadmissionDays <> 'null' AND ReadmissionDays <= 30
               GROUP BY AdmitCategory
               """)

    fig = px.bar(h1,
                 y="AdmitCategory",
                 x="ClaimsAmount",
                 orientation='h')

    fig.layout.update(
        margin=dict(l=2, r=2, b=2, t=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig

def graph_top_vessels():
    vessel_data = df_inpatient.groupby(['mmsi', 'coverage'])[
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






@app.callback(
    Output('admit_cat_counts', 'figure'),
    Output('admit_cat_avgs', 'figure'),
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
                            dbc.CardHeader('% of Patients with a secondary claim within 30 days of previous claims date'),
                            dbc.CardBody([
                                html.P([readmit_pctg() + "%"])
                            ])
                        ]),
                    ], width=12
                    )
                ]), 

                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                        dbc.CardHeader('Inpatient Count'),
                        dcc.Graph(
                            figure=admit_cat_counts(),
                            style={'height': '250px'},
                            id='admit_cat_counts'
                        )
                        ])
                    )
                ]),


            ]
            ), md=3
        ),

        dbc.Col(
            dbc.Card([
                # first-row:
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Average Claims Amount of readmission patients within 30 day sof previous claims date'),
                            dbc.CardBody([
                                html.P([
                                    "${:,.0f}".format(df_inpatient.loc[(df_inpatient.ReadmissionDays.dt.days <= 30), ['CLM_PMT_AMT']].mean()[0])
                                ])
                            ])
                        ])
                    ], width=12
                    )
                ]), 


                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                        dbc.CardHeader('Average Claim Amount'),
                        dcc.Graph(
                            figure=admit_cat_avgs(),
                            style={'height': '250px'},
                            id='admit_cat_avgs'
                        )
                        ])
                    )
                ])

            ]
            ), md=3
        ),


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
