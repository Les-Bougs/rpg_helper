import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import flask
import json

import player
import pandas as pd

import glob, os
from app import app


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="RPG Helper",
    brand_href="#",
    sticky="top",
)

alert_connection_text = html.Div("Wrong Pseudo or Passwoedrd")
alert_connection = dbc.Alert(alert_connection_text, color="danger",style={'display': 'none'})

body = html.Div(
    [
        dbc.Jumbotron(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1("Login", id="test",className="display-3"),
                                html.P( "Please enter your credentials.",className="lead"),
                            ],width={"size": 3, "offset":1}),
                        dbc.Col(
                            [
                                alert_connection,
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Pseudo: ",className="lead"),width={"size": 2}),
                                        dbc.Col(dcc.Input(id={"type":"d-input", "name":"pseudo"},type="text",placeholder="Ex: \"Nini\"")),
                                    ]),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Password: ",className="lead"),width={"size": 2}),
                                        dbc.Col(dcc.Input(id={"type":"d-input", "name":"password"},type="password",placeholder="Ex: 1234")),
                                    ]),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Options: ",className="lead"),width={"size": 2}),
                                        dbc.Col( dcc.Checklist(id={"type":"d-input", "name":"connection-option"},
                                            options=[
                                                {'label': ' Remember me', 'value': 'REM'},
                                                {'label': ' Game Master', 'value': 'GM'}
                                            ],
                                            value=[],
                                        ),width={"size": 4})
                                    ]),
                                dbc.Row(
                                    [
                                        dbc.Button("New Player",id="new_player",className="mr-1"),
                                        dbc.Button("Connect",id={"type":"d-button", "name":"connection-connect"},className="mr-1")
                                    ]
                                ),
                            ],width={"size": 4})
                    ]),
            ])
    ])

index_layout = html.Div([navbar, body])

