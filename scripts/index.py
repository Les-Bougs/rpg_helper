import glob, os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

import json


from global_data import game_data, players_list, session_data
from app import app
import player
import gamemaster


print("init")
index_error = [False]

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


alert_connection_text = html.Div("")
alert_connection = dbc.Alert(alert_connection_text,id="alert_connection_text", color="danger",style={'display': 'none'})

body = html.Div(
    [
        dbc.Jumbotron(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                
                                html.Div(id="index_tmp", style={"display": "none"}),
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




# callbacks
@app.callback(
    Output("index_tmp", "children"),
    [Input({"type": "d-button", "name": ALL}, "n_clicks"),
     Input("sess_id", "children")],
    [State({"type": "d-input", "name": ALL}, "value")],
)
def index_callback(button_n, sess_id, input_v):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    print(ctx.triggered)
    ## Get the triggenring input
    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])

    ## If it's a button
    if trigering_id["type"] == "d-button":
        context, name = trigering_id["name"].split("-")

        ## if the context is the connection page
        if context == "connection":

            ## get the different data of the connection form
            data = session_data[sess_id]
            pseudo = ctx.states['{"name":"pseudo","type":"d-input"}.value']
            password = ctx.states['{"name":"password","type":"d-input"}.value']
            GM = (
                "GM"
                in ctx.states['{"name":"connection-option","type":"d-input"}.value']
            )

            if pseudo == None or password == None:
                alert_connection_text.children = "Please enter a pseudo and a password"
                alert_connection.style = None
                data["error"] = True

            ## if it's a connection attempt
            elif name == "connect":

                print(pseudo + ":" + password)
                ## Search for player in the json data and compare password
                if (pseudo in game_data) and game_data[pseudo]["password"] == password:
                    p = game_data[pseudo]
                ## If no player found display a warning message on the index page
                if data == None:
                    alert_connection_text.children = "Wrong Pseudo or Password"
                    alert_connection.style = None
                    data["error"] = True
                    

                else:
                    ## Test if the client is connecting with the right statue
                    is_gm = p["gm"] == "yes"

                    if GM != is_gm:
                        print("bla")
                        alert_connection_text.children = "Wrong statue GM/player"
                        alert_connection.style = None
                        data["error"] = True

                    ## If everything is good
                    else:
                        alert_connection.style = {"display": "none"}
                        data["name"] =  pseudo

                        ## If game master
                        if is_gm:
                            gamemaster.page_layout.children = gamemaster.page(pseudo)

                        ## If player
                        else:
                            alrdy_exist = False
                            for p in players_list:
                                if p.name == pseudo:
                                    alrdy_exist = True
                            if alrdy_exist == False:
                                p = player.Player(pseudo, game_data[pseudo])
                                game_data[data["name"]]["session_num"] = len(players_list)
                                players_list.append(p)
                                gamemaster.div_players.append(gamemaster.player_line(p))

            ## If it's a new player attempt
            elif name == "new-player":
                pass  # todo process to create a new player add it to the players.json file + lauch the player page

            ## return the player /GM profil if one was found/created
            return ""
    else:
        raise PreventUpdate

