from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app


home = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col(
                html.H2("Healthcare Quality Analysis")
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Br()
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Br()
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Center(html.H5("Executive Summary", className="landing-section"))
            ),
            dbc.Col(
                html.Center(html.H5("Tab 1", className="landing-section"))
            ),
            dbc.Col(
                html.Center(html.H5("Tab 2", className="landing-section"))
            )
        ])
    ], className="landing-text"),
    html.Img(src=app.get_asset_url("Offset_68282_7373.jpg"), className="landing-image")
])


layout = home