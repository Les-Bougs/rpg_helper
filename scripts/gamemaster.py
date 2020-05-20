import json

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
)
from app import app


def player_line(player):
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    [html.H1(player.name, className="display-3"),],
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col([dbc.Row([player.btn_div]),], width={"size": 4}),
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
                    dbc.DropdownMenuItem("Entry 3"),
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
            dbc.Jumbotron(dbc.Row(html.Div(name + " The Game Master"))),
            html.Div(div_players),
            dbc.Button(
                "Save Game", id={"type": "save-button", "name": "gm"}, className="mr-1",
            ),
        ]
    )
    return html.Div([navbar, body])


div_players = []
page_layout = html.Div(page("none"))


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
def index_callback(button_n, sess_id):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    ## Stuff during the game context
    bt = trigering_id["name"]
    p_num = int(trigering_id["player"])
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
        print("[" + sess_id[:8] + "-" + g_sessions[sess_id]["name"] + "] GM rolled")
    # tell the GM session to update their layout
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True

    raise PreventUpdate
