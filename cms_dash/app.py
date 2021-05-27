import dash
import dash_auth
import sys
import os
import dash_bootstrap_components as dbc
from flask import Flask
from users import VALID_USERNAME_PASSWORD_PAIRS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

external_stylesheets=[dbc.themes.SLATE]


server = Flask(__name__) # define flask app.server

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    server=server,
)

# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )