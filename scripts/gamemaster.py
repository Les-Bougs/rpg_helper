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
    g_objects_array,
    g_diff,
    g_card_channels,
    discord_move_p,
    discord_setup_p
)
from app import app


div_players = []
players_dropdown = []

gm_gui_values = {}
gm_gui_values["gm-move-to-card-checklist-players"] = []
gm_gui_values["gm-move-to-card-dropbox-card"] = []
gm_gui_values["gm-roll-checklist-players"] = []

gm_gui_obj = {}


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
                      html.P(player.p_data["objective"]),
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
                          value=player.p_data["inventory"],
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
    gm_gui_obj["gm-roll-dropbox-attribute"] = dcc.Dropdown(options=[{"label": a, "value": a} for a in g_attributes],
                                                           id="gm-roll-dropbox-attribute")
    gm_gui_obj["gm-roll-dropbox-difficulty"] = dcc.Dropdown(options=[{"label": p, "value": p}
                                                                     for p in ["easy", "mkay", "hard", "nope"]],
                                                            id="gm-roll-dropbox-difficulty")
    return dbc.Jumbotron(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Checklist(options=players_dropdown,
                                  id="gm-roll-checklist-players",
                                  inline=True,
                                  value=gm_gui_values["gm-roll-checklist-players"]),
                    width={"size": 3, "offset": 1},
                ),
                dbc.Col(gm_gui_obj["gm-roll-dropbox-attribute"], width={"size": 3}),
                dbc.Col(gm_gui_obj["gm-roll-dropbox-difficulty"], width={"size": 3}),
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
                                      id="gm-move-to-card-checklist-players", inline=True, value=gm_gui_values["gm-move-to-card-checklist-players"]),
                        width={"size": 3, "offset": 1}),
                dbc.Col(
                    dcc.Dropdown(options=[{"label": a, "value": a} for a in g_cards_name]+[{"label": "Clear", "value": "Clear"}],
                                 id="gm-move-to-card-dropbox-card",
                                 multi=True,
                                 value=gm_gui_values["gm-move-to-card-dropbox-card"]),
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
            html.Div(id="gm_tmp5", style={"display": "none"}),
            dbc.Row(div_players),
            dbc.Row(g_card_channels),
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
    discord_setup_p(str(p.num), p.name)
    if p.channel != -1:
        discord_move_p(str(p.num), str(p.channel))
        g_card_channels[p.channel].children[2].children.children += p.name + " (" + p.raceName + "|" + p.className + ")  "
        g_card_channels[p.channel].style = None


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
    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
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
    x = p.p_data["attribute"][attr] + p.bonus[attr]
    a = g_diff[diff]['a']
    b = g_diff[diff]['b']
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
    Output("gm_tmp5", "children"),
    [
        Input("gm-move-to-card-checklist-players", "value"),
        Input("gm-move-to-card-dropbox-card", "value"),
        Input("gm-roll-checklist-players", "value"),
        Input("gm-roll-dropbox-attribute", "value"),
        Input("gm-roll-dropbox-difficulty", "value"),
    ]
)
def gm_gui_callback(move_checklist, move_dropdown_card, roll_checklist, roll_dropdown_attr, roll_dropdown_diff):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate

    gm_gui_values["gm-move-to-card-checklist-players"].clear()
    for v in move_checklist:
        gm_gui_values["gm-move-to-card-checklist-players"].append(v)

    gm_gui_values["gm-move-to-card-dropbox-card"].clear()
    for v in move_dropdown_card:
        gm_gui_values["gm-move-to-card-dropbox-card"].append(v)

    gm_gui_values["gm-roll-checklist-players"].clear()
    for v in roll_checklist:
        gm_gui_values["gm-roll-checklist-players"].append(v)

    gm_gui_obj["gm-roll-dropbox-attribute"].value = roll_dropdown_attr

    gm_gui_obj["gm-roll-dropbox-difficulty"].value = roll_dropdown_diff

    print(roll_dropdown_diff)

    raise PreventUpdate


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
def gm_move_to_card_callback(button_n, players, cards, sess_id):
    ctx = dash.callback_context
    # If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] is None or players is None or cards is None:
        raise PreventUpdate

    index = []
    i = 0
    is_new_place = False
    if(cards[0] == "Clear"):
        index.append(-1)
    else:
        for c in g_cards_name:
            if c in cards:
                index.append(i)
                if g_cards_name[c]["type"] == "place":
                    is_new_place = True
            i += 1

    for p in g_players_list:
        if p.name in players:
            if index[0] == -1:
                p.cards.clear()
            else:
                if is_new_place:  # if new place remove everything
                    p.cards.clear()
                    p.p_data["cards"].clear()
                ind = 0
                for i in index:
                    if g_cards[i] not in p.cards and g_cards[i].children[1].children[0].children != p.name:
                        p.cards.append(g_cards[i])
                        p.p_data["cards"].append(cards[ind])
                        ind += 1

    for card in g_cards:
        card.children[1].children[2].children = ""

    for c in g_card_channels:
        c.children[2].children.children = ""
        c.style = {"display": "none"}

    for p in g_players_list:
        for card in p.cards:
            if g_cards_name[card.children[1].children[0].children]["type"] == "place":
                card.children[1].children[2].children += p.name + " (" + p.raceName + "|" + p.className + ")     "
                if p.channel != g_cards_name[card.children[1].children[0].children]["channel"]:
                    p.channel = g_cards_name[card.children[1].children[0].children]["channel"]
                    discord_move_p(str(p.num), str(p.channel))
                g_card_channels[p.channel].style = None
                g_card_channels[p.channel].children[2].children.children += p.name + " (" + p.raceName + "|" + p.className + ")  "
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
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = trigger_obj["player"]
    p = g_players_list[int(p_num)]

    # reset bonus before recomputing them
    for attr in p.bonus:
        p.bonus[attr] = 0

    p.update_inventory(value)
    g_sessions[p.sess_id]["update"] = True


@app.callback(
    Output({"type": "channel-div", "channel_num": MATCH}, "children"),
    [Input({"type": "channel-button", "channel_num": MATCH}, "n_clicks")]
)
def channel_card(n_inc):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate

    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    c_num = trigger_obj["channel_num"]
    print(c_num)
    discord_move_p("-1", c_num)
    raise PreventUpdate
