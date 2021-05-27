from shutil import copyfile
from datetime import date, datetime
import pandas as pd
import numpy as np

import dash
import dash_auth
import dash_table
import sys
import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import data_pipeline
# from prototype_map_config import config
# from DataQueryHelper import DataQueryHelper
from pages import home, executivesmmary
from app import app

app.title = "CMS DASH BPA"

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/", id='home', className='nav-link', external_link=True)),        
        dbc.NavItem(dbc.NavLink("Executive Summary", href="/executive-summary", id='executive-summary', className='nav-link', external_link=True)),
        #dbc.NavItem(dbc.NavLink("Data Discovery Journey", href="/data-quality", id='data-quality', external_link=True, className='nav-link')),
        #dbc.NavItem(dbc.NavLink("Live Application", href="/live-map", id='live-map', external_link=True, className='nav-link'))
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Tab 1"), dbc.DropdownMenuItem("Tab 2")],
            label="Deep Dive",
            nav=True,
        )
    ],
    id="navbar",
    brand="CMS DASH BPA",
    color="dark",
    fluid=True,
    dark=True
)
   
body = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    ], id='body')

app.layout = html.Div([navbar, body]) 

@app.callback(dash.dependencies.Output('page-content', 'children'), 
                [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home.layout
    elif pathname == '/executive-summary':
        return executivesmmary.layout
    # elif pathname == '/data-quality':
    #     return dataquality.layout
    # elif pathname == '/live-map':
    #     return maps.layout
    else:
        return dcc.Markdown('## Page not found')


server = app.server

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=5050, debug=True)
