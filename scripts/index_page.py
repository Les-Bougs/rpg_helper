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

title = html.H1("Login", id="test",className="display-3")

body = html.Div(
    [
        dbc.Jumbotron(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                title,
                                html.P( "Please enter your credentials.",className="lead"),
                            ],width={"size": 3, "offset":1}),
                        dbc.Col(
                            [
                                dbc.Alert("This is a danger alert. Scary!", color="danger"),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Pseudo: ",className="lead"),width={"size": 2}),
                                        dbc.Col(dcc.Input(id="pseudo",type="text",placeholder="Ex: \"Nini\"")),
                                    ]),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Password: ",className="lead"),width={"size": 2}),
                                        dbc.Col(dcc.Input(id="password",type="password",placeholder="Ex: 1234")),
                                    ]),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("Options: ",className="lead"),width={"size": 2}),
                                        dbc.Col( dcc.Checklist(
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
                                        dbc.Button("Connect",id="connect",href="/form",className="mr-1")
                                    ]
                                ),
                            ],width={"size": 4})
                    ]),
            ])
    ])

index_layout = html.Div([navbar, body])


url_bar_and_content_div = html.Div([
    html.Div(index_layout,id='content' ),
    html.Div(id='h-div-connect', style={'display': 'none'}),
    html.Div(id='h-div-new', style={'display': 'none'}),
    html.Div(id='h-div-data', style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
])




def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        index_layout
    ])


app.layout =  serve_layout

@app.callback(Output('content', 'children'),
              [Input('url', 'pathname'),
               Input('h-div-data', 'children')])
def display_page(pathname, div):
    print("hey")
    if pathname == '/form' and div !=  None and div != "{}":
        print(div)
        data = json.loads(div)
        return player.page(data["pseudo"])
    else:
        return index_layout


    
# Page 1 callbacks
@app.callback(Output('h-div-data', 'children'),
              [Input('connect', 'n_clicks')],
              [State('pseudo', 'value'),
               State('password', 'value')])
def update_output(n_clicks, pseudo, password):
    if(n_clicks==None):
        raise PreventUpdate
    else:
        player_file = open("../game_template/players.json")
        player_data = json.load(player_file)
        data={}
        for p in player_data:
            if(p["pseudo"] == pseudo and p["password"]== password):
                data = p
        return json.dumps(data)

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
