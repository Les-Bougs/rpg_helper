import glob, os
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

from global_data import g_data, g_players_list, g_sessions, g_gm_list
from app import app

import player
import gamemaster

# Def of the navigation bar on top of the page
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

# Object to display a alert when an error occured
alert_connection_text = html.Div("")
alert_connection = dbc.Alert(
    alert_connection_text,
    id="alert_connection_text",
    color="danger",
    style={"display": "none"},
)

body = html.Div(
    [
        dbc.Jumbotron(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id="index_tmp", style={"display": "none"}),
                                html.H1("Login", id="test", className="display-3"),
                                html.P(
                                    "Please enter your credentials.", className="lead"
                                ),
                            ],
                            width={"size": 3, "offset": 1},
                        ),
                        dbc.Col(
                            [
                                alert_connection,
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Label("Pseudo: ", className="lead"),
                                            width={"size": 2},
                                        ),
                                        dbc.Col(
                                            dcc.Input(
                                                id={
                                                    "type": "d-input",
                                                    "name": "pseudo",
                                                },
                                                type="text",
                                                placeholder='Ex: "Nini"',
                                                persistence="b",
                                                persistence_type="local",
                                            )
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Label("Password: ", className="lead"),
                                            width={"size": 2},
                                        ),
                                        dbc.Col(
                                            dcc.Input(
                                                id={
                                                    "type": "d-input",
                                                    "name": "password",
                                                },
                                                type="password",
                                                placeholder="Ex: 1234",
                                                persistence="a",
                                                persistence_type="local",
                                            )
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Label("Options: ", className="lead"),
                                            width={"size": 2},
                                        ),
                                        dbc.Col(
                                            dcc.Checklist(
                                                id={
                                                    "type": "d-input",
                                                    "name": "connection-option",
                                                },
                                                options=[
                                                    {
                                                        "label": " Remember me",
                                                        "value": "REM",
                                                    },
                                                ],
                                                value=[],
                                            ),
                                            width={"size": 4},
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Button(
                                            "New Player",
                                            id={
                                                "type": "d-button",
                                                "name": "connection-new",
                                            },
                                            className="mr-1",
                                        ),
                                        dbc.Button(
                                            "Connect",
                                            id={
                                                "type": "d-button",
                                                "name": "connection-connect",
                                            },
                                            className="mr-1",
                                        ),
                                    ]
                                ),
                            ],
                            width={"size": 4},
                        ),
                    ]
                ),
            ]
        )
    ]
)

index_layout = html.Div([navbar, body])


# callbacks
@app.callback(
    Output("index_tmp", "children"),
    [
        Input({"type": "d-button", "name": ALL}, "n_clicks"),
        Input("sess_id", "children"),
    ],
    [State({"type": "d-input", "name": ALL}, "value")],
)
def index_callback(button_n, sess_id, input_v):
    ''' each time a button in the index page is triggered this function is called '''
    ctx = dash.callback_context

    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate

    # Get the triggenring input
    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])

    # If it's a button
    if trigering_id["type"] == "d-button":
        context, name = trigering_id["name"].split("-")

        # if the context is the connection page
        if context == "connection":

            # get the different data of the connection form
            data = g_sessions[sess_id]
            pseudo = ctx.states['{"name":"pseudo","type":"d-input"}.value']
            password = ctx.states['{"name":"password","type":"d-input"}.value']
            data["rem"] = (
                "REM"
                in ctx.states['{"name":"connection-option","type":"d-input"}.value']
            )

            if pseudo is None or password is None:
                alert_connection.style = None
                data["error"] = "Please enter a pseudo and a password"

            # if it's a connection attempt
            elif name == "connect":

                # Search for player in the json data and compare password
                p = None
                if (pseudo in g_data) and g_data[pseudo]["password"] == password:
                    p = g_data[pseudo]
                # If no player found display a warning message on the index page
                if p is None:
                    alert_connection.style = None
                    data["error"] = "Wrong Pseudo or Password"

                else:
                    # If everything is good
                    is_gm = p["gm"] == "yes"
                    alert_connection.style = {"display": "none"}
                    data["name"] = pseudo

                    # If game master
                    if is_gm:
                        data["context"] = "gm"
                        gamemaster.page_layout.children = gamemaster.page(pseudo)
                        if (sess_id in g_gm_list) is False:
                            g_gm_list.append(sess_id)
                    else:  # If player
                        data["error"] = ""
                        data["context"] = "player"
                        alrdy_exist = False
                        for p in g_players_list:
                            if p.name == pseudo:
                                alrdy_exist = True
                        if alrdy_exist is False:
                            p_num = len(g_players_list)
                            data["p_num"] = p_num
                            g_data[pseudo]["session_num"] = p_num
                            p = player.Player(pseudo, sess_id, g_data[pseudo])
                            g_players_list.append(p)
                            gamemaster.add_player_to_GM(p)
                            p.main_div.children = p.create_skill_dash()
                        else:
                            data["p_num"] = g_data[pseudo]["session_num"]

                        # tell the GM session to update their layout
                        for gm_id in g_gm_list:
                            g_sessions[gm_id]["update"] = True

            # If it's a new player attempt
            elif name == "new":
                # If pseudo already used by other character
                if pseudo in g_data:
                    alert_connection.style = None
                    data["error"] = "Pseudo already used"
                else:
                    # If everything is good
                    p_num = len(g_players_list)
                    data["error"] = ""
                    data["context"] = "player"
                    data["p_num"] = p_num
                    data["name"] = pseudo
                    g_data[pseudo] = {
                        "password": password,
                        "gm": "no",
                        "session_num": p_num,
                        "race": "",
                        "class": "",
                        "ressource": {"hp": 100, "mp": 100, "gold": 200},
                        "attribute": {
                            "strength": 0,
                            "dexterity": 0,
                            "stamina": 0,
                            "charisma": 0,
                            "inteligence": 0,
                            "wisdom": 0,
                        },
                        "inventory": [],
                    }
                    p = player.Player(pseudo, sess_id, g_data[pseudo])
                    g_players_list.append(p)
                    gamemaster.div_players.append(gamemaster.player_line(p))
                    # tell the GM session to update their layout
                    for gm_id in g_gm_list:
                        g_sessions[gm_id]["update"] = True

            # return the player /GM profil if one was found/created
            data["update"] = True
            return ""
    else:
        raise PreventUpdate
