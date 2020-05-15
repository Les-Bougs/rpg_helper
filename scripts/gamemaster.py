import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

from global_data import game_data, players_list, session_data
from app import app
import json


def player_line(player):
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(player.name, className="display-3"),
                    ],width={"size": 3, "offset":1}),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                player.btn_div
                            ]
                        ),
                    ],width={"size": 4})
            ]))

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
            dbc.Jumbotron(dbc.Row(html.Div(name + " The Game Master" ))),
            html.Div(div_players)
        ])
    return html.Div([navbar, body])



div_players = []
page_layout = html.Div(page("none"))


# callbacks
@app.callback(
    Output("gm_tmp", "children"),
    [Input({"type": "p-button", "name": ALL}, "n_clicks"),
     Input("sess_id", "children")],
)
def index_callback(button_n, sess_id):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    print("ouille")
    ## Stuff during the game context
    context, name = trigering_id["name"].split("-")
    p_num = int(name.split("_")[0])
    print(p_num)
    bt = name.split("_")[1]
    bonus = 0
    if bt == "easy":
        bonus = 10
    elif bt == "medium":
        bonus = 0
    else:
        bonus = -10
    
    players_list[p_num].result = bonus
    players_list[p_num].btn_div.style = {"display": "none"}
    
    raise PreventUpdate
