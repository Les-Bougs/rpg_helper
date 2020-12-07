import json
import numpy as np

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
    g_cards,
    g_cards_name,
    g_objects,
    g_objects_array
)
from app import app


div_players = []
players_dropdown = []


def disconnect_player(player):
    del div_players[player.num]
    del players_dropdown[player.num]
    g_players_list.remove(player)
    g_sessions[player.sess_id]["context"] = "index"
    g_sessions[player.sess_id]["update"] = True
    g_sessions[player.sess_id]["p_num"] = -1
    for i in range(len(g_players_list)):
        p = g_players_list[i]
        p.num = i
        g_sessions[p.sess_id]["p_num"] = i
        p.p_data["session_num"] = i
        g_sessions[p.sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True


def player_line(player):
    return dbc.Card(
        dbc.CardBody([html.Div(id={"type": "xp-div",
                                   "player": str(player.num)},
                               style={"display": "none"}),
                      html.Div(id={"type": "ress-div",
                                   "player": str(player.num)},
                               style={"display": "none"}),
                      html.Div(id={"type": "inventory-div",
                                   "player": str(player.num)},
                               style={"display": "none"}),
                      html.H1(player.name),
                      player.btn_div,
                      player.result_div,
                      html.Div(ressource_input(player)),
                      dbc.Button("Set ressources",
                                 id={"type": "ress-button", "player": str(player.num)},
                                 block=True),
                      html.Div(player.attribute_badges),
                      dbc.Button("Give XP",
                                 id={"type": "xp-button", "player": str(player.num)},
                                 block=True),
                      dcc.Dropdown(
                          options=g_objects_array,
                          multi=True,
                          id={"type": "inventory-dropdown", "player": str(player.num)}
                      )
                      ]), style={"width": "16rem"})


def ressource_input(player):
    return [dbc.Row([dbc.Col(html.P(ress), width={"size": 4, "offset": 0}),
                     dbc.Col(dbc.Input(type="number",
                                       value=value,
                                       min=0,
                                       step=1,
                                       id={"type": "ress-input",
                                           "player": str(player.num),
                                           "ressource": ress}))]) for ress, value in player.p_data["ressource"].items()]


def rolling_line():
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Checklist(options=players_dropdown,
                                  id="gm-roll-checklist-players", inline=True),
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col(
                    dcc.Dropdown(options=[{"label": a, "value": a} for a in g_attributes],
                                 id="gm-roll-dropbox-attribute"),
                    width={"size": 3},
                ),
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            {"label": p, "value": p} for p in ["easy", "mkay", "hard", "nope"]
                        ],
                        id="gm-roll-dropbox-difficulty"
                    ),
                    width={"size": 3},
                ),
                dbc.Col(
                    dbc.Button(
                        "Roll Dice",
                        id="gm-roll-button",
                        className="mr-1",
                    ),
                    width={"size": 1, "offset": 1},
                ),
            ]
        )
    )


def move_to_card_line():
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(dbc.Checklist(options=players_dropdown,
                                      id="gm-move-to-card-checklist-players", inline=True),
                        width={"size": 3, "offset": 1}),
                dbc.Col(
                    dcc.Dropdown(options=[{"label": a, "value": a} for a in g_cards_name]+[{"label": "Clear", "value": "Clear"}],
                                 id="gm-move-to-card-dropbox-card"),
                    width={"size": 3},
                ),
                dbc.Col(
                    dbc.Button(
                        "Move",
                        id="gm-move-to-card-button",
                        className="mr-1",
                    ),
                    width={"size": 1, "offset": 1},
                ),
            ]
        )
    )


def cards_line():
    return dbc.Row(g_cards)


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
            dbc.Button(
                "Save Game", id={"type": "save-button", "name": "gm"}, className="mr-1",
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
            html.Div(id="gm_tmp4", style={"display": "none"}),
            dbc.Row(div_players),
            rolling_line(),
            move_to_card_line(),
            cards_line()
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

    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate

    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    # Stuff during the game context
    bt = trigering_id["name"]
    p_num = g_sessions[trigering_id["player"]]["p_num"]
    roll_dice(g_players_list[p_num], g_players_list[p_num].testing_attribute, bt)

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
    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None or players is None or attribute is None or difficulty is None:
        raise PreventUpdate

    for p in g_players_list:
        if p.name in players:
            roll_dice(p, attribute, difficulty)
    raise PreventUpdate


def roll_dice(p, attr, diff):
    x = p.p_data["attribute"][attr]
    if diff == "easy":
        a, b = 0.3, 65
    elif diff == "mkay":
        a, b = 0.6, 20
    elif diff == "hard":
        a, b = 0.4, 10
    elif diff == "nope":
        a, b = 0.25, 5
    target = a*x + b
    dice = np.random.randint(0, 100)
    if target >= dice:
        result = "SUCCESS ✅"
    else:
        result = "FAIL ❌"
    result_out = f"{result}({dice}:{target})"
    for a in p.roll_outs:
        p.roll_outs[a].children = result_out if a == attr else ""

    p.result_div.children = attr + " test: " + result_out
    g_sessions[p.sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True


# callbacks
@app.callback(
    Output("gm_tmp4", "children"),
    [Input("gm-move-to-card-button", "n_clicks")],
    [
        State("gm-move-to-card-checklist-players", "value"),
        State("gm-move-to-card-dropbox-card", "value"),
        State("sess_id", "children")
    ]
)
def gm_move_to_card_callback(button_n, players, card, sess_id):
    ctx = dash.callback_context
    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None or players is None or card is None:
        raise PreventUpdate

    index = 0
    if(card == "Clear"):
        index = -1
    else:
        for c in g_cards_name:
            if c == card:
                break
            index = index+1

    for p in g_players_list:
        if p.name in players:
            if index == -1:
                p.cards.clear()
            else:
                p.cards.append(g_cards[index])
    for card in g_cards:
        card.children[1].children[2].children = ""

    for p in g_players_list:
        for card in p.cards:
            card.children[1].children[2].children += p.name + " (" + p.raceName + "|" + p.className + ")     "
    for p in g_players_list:
        g_sessions[p.sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    raise PreventUpdate


# callbacks
@app.callback(
    Output({"type": "xp-div", "player": MATCH}, "children"),
    [Input({"type": "xp-button", "player": MATCH}, "n_clicks")]
)
def give_xp_callback(button_n):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = trigger_obj["player"]
    p = g_players_list[int(p_num)]
    p.xp_to_use += 5
    for a in p.skill_bar_obj:
        p.skill_bar_obj[a]["button_inc"].disabled = False
    g_sessions[p.sess_id]["update"] = True


# callbacks
@app.callback(
    Output({"type": "ress-div", "player": MATCH}, "children"),
    [Input({"type": "ress-button", "player": MATCH}, "n_clicks")],
    [
        State({"type": "ress-input", "player": MATCH, "ressource": ALL}, "value")
    ]
)
def set_ressources_callback(button_n, value):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = trigger_obj["player"]
    p = g_players_list[int(p_num)]

    index = 0
    for ress in p.p_data["ressource"]:
        p.p_data["ressource"][ress] = value[index]
        index += 1

    p.ressource_div.children = ""
    for ress, value in p.p_data["ressource"].items():
        p.ressource_div.children += "| " + f"{ress} : {value} "
    p.ressource_div.children += "|"

    g_sessions[p.sess_id]["update"] = True


# callbacks
@app.callback(
    Output({"type": "inventory-div", "player": MATCH}, "children"),
    [Input({"type": "inventory-dropdown", "player": MATCH}, "value")]
)
def inventory_callback(value):
    print("hey")
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = trigger_obj["player"]
    p = g_players_list[int(p_num)]
    p.inventory.children.clear()
    for obj in value:
        p.inventory.children.append(dbc.Badge(obj, color="primary", className="mr-1"))
    g_sessions[p.sess_id]["update"] = True
