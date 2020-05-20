import json
import numpy as np
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

from global_data import (
    g_data,
    g_players_list,
    g_sessions,
    g_gm_list,
    g_verbose,
    g_attributes,
)
from app import app


div_players = []
players_dropdown = []


def disconnect_player(player):
    del div_players[player.num]
    del players_dropdown[player.num]
    g_players_list.remove(player)
    g_sessions[player.sess_id]["context"]="index"
    g_sessions[player.sess_id]["update"]=True
    g_sessions[player.sess_id]["p_num"]=-1
    for i in range(len(g_players_list)):
        p = g_players_list[i]
        p.num = i
        g_sessions[p.sess_id]["p_num"]=i
        p.p_data["session_num"] = i
        g_sessions[p.sess_id]["update"]=True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True

def player_line(player):
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    [html.H1(player.name, className="display-3"),],
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col([dbc.Row([player.btn_div]),], width={"size": 4}),
                dbc.Col([dbc.Row([player.result_div]),], width={"size": 4}),
            ]
        )
    )


def rolling_line():
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    dcc.Checklist(options=players_dropdown,
                        id= "gm-roll-checklist-players"),
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": a, "value": a} for a in g_attributes],
                        id= "gm-roll-dropbox-attribute"
                    ),
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            {"label": p, "value": p} for p in ["easy", "medium", "hard"]
                        ],
                        id="gm-roll-dropbox-difficulty"
                    ),
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col(
                    dbc.Button(
                        "Roll Dice",
                        id="gm-roll-button",
                        className="mr-1",
                    ),
                    width={"size": 3, "offset": 1},
                ),
            ]
        )
    )


def page(name):
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
                    dbc.DropdownMenuItem("Quit"),
                ],
            ),
        ],
        brand="RPG Helper",
        brand_href="#",
        sticky="top",
    )

    body = html.Div(
        [
            html.Div(id="gm_tmp", style={"display": "none"}),
            html.Div(id="gm_tmp2", style={"display": "none"}),
            html.Div(id="gm_tmp3", style={"display": "none"}),
            dbc.Jumbotron(dbc.Row(html.Div(name + " The Game Master"))),
            html.Div(div_players),
            dbc.Button(
                "Save Game", id={"type": "save-button", "name": "gm"}, className="mr-1",
            ),
            rolling_line(),
        ]
    )
    return html.Div([navbar, body])


page_layout = html.Div(page("none"))


def add_player_to_GM(p):
    players_dropdown.append({"label": p.name, "value": p.name})
    div_players.append(player_line(p))


# callbacks
@app.callback(
    Output("gm_tmp2", "children"),
    [
        Input({"type": "save-button", "name": ALL}, "n_clicks"),
        Input("sess_id", "children"),
    ],
)
def save_callback(button_n, sess_id):
    ctx = dash.callback_context
    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate
    if g_verbose:
        print("[" + sess_id[:8] + "-" + g_sessions[sess_id]["name"] + "] Save game")
    with open("../game_template/players.json", "w") as fp:
        json.dump(g_data, fp)
    return ""


# callbacks
@app.callback(
    Output("gm_tmp", "children"),
    [
        Input({"type": "difficulty-button", "player": ALL, "name": ALL}, "n_clicks"),
        Input("sess_id", "children"),
    ],
)
def p_btn_callback(button_n, sess_id):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    ## Stuff during the game context
    bt = trigering_id["name"]
    p_num = g_sessions[trigering_id["player"]]["p_num"]
    bonus = 0
    if bt == "easy":
        bonus = 10
    elif bt == "medium":
        bonus = 0
    else:
        bonus = -10
    g_players_list[p_num].bonus = bonus
    g_players_list[p_num].is_rolling = False
    g_players_list[p_num].btn_div.style = {"display": "none"}

    if g_verbose:
        print("[" + sess_id[:8] + "-" + g_sessions[sess_id]["name"] + "] GM rolled p["+str(p_num)+"]")

    raise PreventUpdate


# callbacks
@app.callback(
    Output("gm_tmp3", "children"),
    [
        Input("gm-roll-button", "n_clicks"),
    ],
    [
        State("gm-roll-checklist-players", "value"),
        State("gm-roll-dropbox-attribute", "value"),
        State("gm-roll-dropbox-difficulty", "value"),
        State("sess_id", "children"),
    ],
)
def gm_roll_callback(button_n, players, attribute, difficulty, sess_id):
    ctx = dash.callback_context
    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None or players==None or attribute==None or difficulty==None:
        raise PreventUpdate

    diff_val = {"easy":10, "medium":0, "hard":-10}
    bonus = diff_val[difficulty]
    for p in g_players_list:
        if p.name in players:
            value = p.p_data["attribute"][attribute]
            target = value + bonus
            dice = np.random.randint(0, 100)
            if target >= dice:
                result = "SUCCESS ✅"
            else:
                result = "FAIL ❌"
            result_out = f"{result} (dice : {dice}, skill : {target} ({value}+{bonus}))"
            for a in p.roll_outs:
                p.roll_outs[a].children = result_out if a == attribute else ""
            g_sessions[p.sess_id]["update"] = True
            p.result_div.children = "Result: " +result_out
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    raise PreventUpdate
