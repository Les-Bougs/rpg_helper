import json
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate


from global_data import (
    g_sessions,
    g_players_list,
    g_gm_list,
    g_races,
    g_classes,
    g_races_affinity,
    g_verbose,
    g_cards_name,
    g_objects,
    g_diff,
    g_cards,
    discord_move_p,
    discord_bonus_p,
    g_dict_player_channel,
    g_card_channels
)
import gamemaster
from app import app


class Player:
    def __init__(self, name, sess_id, data):
        self.sess_id = sess_id
        self.p_data = data
        self.name = name
        self.raceName = self.p_data["race"]
        self.className = self.p_data["class"]
        self.num = data["session_num"]
        self.img_src = data["img_src"]
        self.channel = -1
        self.cards = []
        index = []
        i = 0
        for c in g_cards_name:
            if c in data['cards']:
                index.append(i)
                if "channel" in g_cards_name[c].keys():
                    self.channel = g_cards_name[c]["channel"]
            i += 1
        for i in index:
            self.cards.append(g_cards[i])
        self.create_layout()
        self.create_gm_interface()
        self.xp_to_use = 0  # Keep the name of the items for the mg GUI
        self.inventory = dbc.Row([dbc.Badge("none", color="primary", className="mr-1")])
        self.attribute_badges = [dbc.Badge(attr + ": " + str(value), color="primary", className="mr-1") for attr, value in self.p_data["attribute"].items()]
        self.bonus = dict([(attr, 0) for attr in self.p_data["attribute"]])

    def create_gm_interface(self):
        self.is_rolling = False
        self.result = -1
        self.attribute_tested = html.H3("hoy")
        self.result_div = html.Div("Result: ")
        self.btn_div = html.Div([
            dbc.Row(dbc.Col(self.attribute_tested)),
            dbc.Row([
                dbc.Col(dbc.Button(
                    "easy",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "easy",
                    },
                    color="success",
                    size="sm",
                ), width={"size": 3, "offset": 0}),
                dbc.Col(dbc.Button(
                    "mkay",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "mkay",
                    },
                    color="warning",
                    size="sm",
                ), width={"size": 3, "offset": 0}),
                dbc.Col(dbc.Button(
                    "hard",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "hard",
                    },
                    color="danger",
                    size="sm",
                ), width={"size": 3, "offset": 0}),
                dbc.Col(dbc.Button(
                    "nope",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "nope",
                    },
                    color="dark",
                    size="sm",
                ), width={"size": 3, "offset": 0})
            ])],
            style={"display": "none"},
        )

    def create_layout(self):
        self.roll_outs = {}
        self.skill_bar_obj = {}
        # player Creation div
        self.creation_div = self.create_creation_div()
        ## NAVBAR
        navbar = self.create_navbar()
        self.main_div = html.Div(self.creation_div)
        body = dbc.Container([self.main_div], className="skilldash_class")
        self.layout = html.Div([navbar, body])

    def create_navbar(self):
        ressource_bar = self.create_ressource_bar()
        return dbc.NavbarSimple(
            children=[
                html.Div(id="player-div-tmp", style={"display": "none"},),
                html.Div(
                    id={"type": "rolling-div", "player": str(self.num), "name": "tmp"},
                    style={"display": "none"},
                ),
                dbc.Col(ressource_bar),
                dbc.NavItem(dbc.NavLink("Link", href="https://github.com/Les-Bougs/rpg_helper")),
                dbc.DropdownMenu(
                    nav=True,
                    in_navbar=True,
                    label="Menu",
                    children=[
                        dbc.DropdownMenuItem("Quit", id="quit-button")
                    ],
                ),
            ],
            brand="Les Bougs - le RPG",
            brand_href="#",
            sticky="top",
        )

    def create_skill_dash(self):
        self.skill_dash = []
        for skill, value in self.p_data["attribute"].items():
            self.skill_dash.append(self.skill_bar(skill, value))
        self.update_inventory(self.p_data["inventory"].copy())
        return dbc.Col([dbc.Row([dbc.Col([dbc.Row(html.H1(self.name)),
                                          dbc.Row(html.H3(self.raceName + " " + self.className)),
                                          dbc.Row(html.P(g_cards_name[self.name]["description"])),
                                          dbc.Row(html.H5("Story:")),
                                          dbc.Row(html.P(self.p_data["story"])),
                                          dbc.Row(html.H5("Objective:")),
                                          dbc.Row(html.P(self.p_data["objective"]))]),
                                 dbc.Col(dbc.Card(dbc.CardImg(src=app.get_asset_url(self.img_src), top=True),
                                                  style={"width": "14rem"})),
                                 dbc.Row(dbc.Button("Private room",
                                                    id={"type": "private-button",
                                                        "player": str(self.num)},
                                                    className="d-button")),
                                 html.Div(id={"type": "player-div-private-tmp",
                                              "player": str(self.num)}, style={"display": "none"})]),
                        html.Div(self.skill_dash),
                        dbc.Row(html.H3("Inventory")),
                        self.inventory,
                        dbc.Row(html.H3("Cards")),
                        dbc.Row(self.cards)])

    def create_creation_div(self):
        return html.Div(
            dbc.Row(
                [
                    html.Div(
                        id={
                            "type": "create_player-div",
                            "player": str(self.num),
                            "name": "tmp",
                        },
                        style={"display": "none"},
                    ),
                    dbc.Col(
                        [
                            html.H1("Races:"),
                            dcc.Dropdown(
                                options=[{"label": r, "value": r} for r in g_races],
                                id={
                                    "type": "create_player-dropbox",
                                    "player": str(self.num),
                                    "name": "race",
                                },
                            ),
                        ],
                        width={"size": 3},
                    ),
                    dbc.Col(
                        [
                            html.H1("Classes:"),
                            dcc.Dropdown(
                                options=[{"label": c, "value": c} for c in g_classes],
                                id={
                                    "type": "create_player-dropbox",
                                    "player": str(self.num),
                                    "name": "class",
                                },
                            ),
                        ],
                        width={"size": 3},
                    ),
                    dbc.Col(
                        [
                            html.H1("."),
                            dbc.Button(
                                "Create",
                                id={
                                    "type": "create_player-button",
                                    "player": str(self.num),
                                    "name": "button",
                                },
                            ),
                        ],
                        width={"size": 3},
                    ),
                ]
            )
        )

    def create_ressource_bar(self):
        self.ressource_div = html.Div("")
        for ress, value in self.p_data["ressource"].items():
            self.ressource_div.children += "| " + f"{ress} : {value} "
        self.ressource_div.children += "|"
        return self.ressource_div

    def skill_bar(self, skill, value):
        # Create those object as player attribute to be able to reach them later in callback functions
        self.roll_outs[skill] = html.Div("", id={"type": "rolling-div",
                                                 "player": str(self.num),
                                                 "name": f"{skill}"})
        self.skill_bar_obj[skill] = {}
        self.skill_bar_obj[skill]["progress_bar"] = dbc.Progress(f"{value}",
                                                                 value=value,
                                                                 striped=False,
                                                                 style={"height": "30px"},
                                                                 id={"type": "d-bar", "name": f"{skill}"})
        self.skill_bar_obj[skill]["button_dec"] = dbc.Button("-",
                                                             id={"type": "d-button-dec", "name": f"{skill}"},
                                                             className="d-button",
                                                             disabled=True)
        self.skill_bar_obj[skill]["button_inc"] = dbc.Button("+",
                                                             id={"type": "d-button-inc", "name": f"{skill}"},
                                                             className="d-button",
                                                             disabled=True)
        self.skill_bar_obj[skill]["button_roll"] = dbc.Button(f"{skill} roll",
                                                              id={
                                                                  "type": "rolling-button",
                                                                  "player": str(self.num),
                                                                  "name": f"{skill}",
                                                              },
                                                              className="d-button")
        self.skill_bar_obj[skill]["badge_roll_easy"] = dbc.Badge(str(0.3*value+65)+"%", color="success", className="mr-1")
        self.skill_bar_obj[skill]["badge_roll_hard"] = dbc.Badge(str(0.4*value+10)+"%", color="danger", className="mr-1")
        return html.Div(
            [
                dbc.Row(dbc.Col(html.Div(skill))),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                self.skill_bar_obj[skill]["progress_bar"]
                            )
                        ),
                        self.skill_bar_obj[skill]["button_dec"],
                        self.skill_bar_obj[skill]["button_inc"],
                        dbc.Col(self.roll_outs[skill]),
                        self.skill_bar_obj[skill]["button_roll"],
                        dbc.Col([dbc.Row(self.skill_bar_obj[skill]["badge_roll_easy"]),
                                 dbc.Row(self.skill_bar_obj[skill]["badge_roll_hard"])])
                    ],
                    align="center",
                ),
            ]
        )

    def update_attribute_bar(self):
        index = 0
        for attr, value in self.p_data["attribute"].items():
            b = self.bonus[attr]
            s = str(value) + (("+" + str(b)) if b != 0 else "")
            self.skill_bar_obj[attr]["progress_bar"].children = s
            self.skill_bar_obj[attr]["progress_bar"].value = value
            easy_c = g_diff['easy']['a']*(value+b)+g_diff['easy']['b']
            hard_c = g_diff['hard']['a']*(value+b)+g_diff['hard']['b']
            self.attribute_badges[index].children = attr + ": " + s + " -- " + str(int(easy_c))+" | "+str(int(hard_c))
            self.skill_bar_obj[attr]["badge_roll_easy"].children = str(easy_c)+"%"
            self.skill_bar_obj[attr]["badge_roll_hard"].children = str(hard_c)+"%"
            index += 1

    def update_inventory(self, value):
        self.inventory.children.clear()
        self.p_data["inventory"].clear()
        for obj in value:
            self.inventory.children.append(dbc.Card([dbc.CardHeader(obj + "(" + str(g_objects[obj]["price"]) + "po)"),
                                                     dbc.CardBody(html.P(g_objects[obj]["description"] +
                                                                         (" (" +
                                                                          (" / ".join("{}\t{}".format(b["attribute"], b["value"])
                                                                                      for b in g_objects[obj]["bonus"])) +
                                                                          ")" if len(g_objects[obj]["bonus"]) > 0 else ""), className="card-text"))],
                                                    color="light"))
            self.p_data["inventory"].append(obj)
            # add potential bonus
            discord_bonus_p(str(self.num), "c", "0")
            if len(g_objects[obj]["bonus"]) > 0:
                for bonus in g_objects[obj]["bonus"]:
                    self.bonus[bonus["attribute"]] += bonus["value"]
                    discord_bonus_p(str(self.num), bonus["attribute"], str(bonus["value"]))
            self.update_attribute_bar()
            g_sessions[self.sess_id]["update"] = True


# INCREASE/DECREASE BAR
@app.callback(
    Output({"type": "d-bar", "name": MATCH}, "value"),
    [Input({"type": "d-button-inc", "name": MATCH}, "n_clicks")],
    [State("sess_id", "children")],
)
def update_bar_value(n_inc, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    attr = trigger_obj["name"]
    p_num = g_sessions[sess_id]["p_num"]
    p = g_players_list[p_num]
    p.p_data["attribute"][attr] += 1

    p.update_attribute_bar()

    p.xp_to_use -= 1
    if p.xp_to_use <= 0:
        for a in p.skill_bar_obj:
            p.skill_bar_obj[a]["button_inc"].disabled = True
    g_sessions[sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    raise PreventUpdate


# ROLL
@app.callback(
    Output({"type": "rolling-div", "player": MATCH, "name": "tmp"}, "children"),
    [Input({"type": "rolling-button", "player": MATCH, "name": ALL}, "n_clicks")],
    [State("sess_id", "children")],
)
def roll_skill(n_inc, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate

    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    attr = trigger_obj["name"]
    p_num = g_sessions[sess_id]["p_num"]
    p = g_players_list[p_num]

    # makes the player difficutly test button visible in the GM layout
    p.testing_attribute = attr
    p.attribute_tested.children = attr + " test: "
    p.btn_div.style = None
    if g_verbose:
        print(
            "["
            + sess_id[:8]
            + "-"
            + g_sessions[sess_id]["name"]
            + "] Rolling ("
            + attr
            + ")"
        )

    # tell the GM session to update their layout
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    p.is_rolling = True
    p.roll_outs[attr].children = dbc.Spinner(color="primary")
    # Disable any other roll
    for s in p.skill_bar_obj:
        p.skill_bar_obj[s]["button_roll"].disabled = True
    g_sessions[sess_id]["update"] = True
    while p.is_rolling is True:
        time.sleep(1)

    # Renable any other roll
    for s in p.skill_bar_obj:
        p.skill_bar_obj[s]["button_roll"].disabled = False
    g_sessions[sess_id]["update"] = True
    return [""] * len(ctx.outputs_list)


@app.callback(
    Output({"type": "create_player-div", "player": MATCH, "name": "tmp"}, "children"),
    [Input({"type": "create_player-button", "player": MATCH, "name": ALL}, "n_clicks")],
    [
        State({"type": "create_player-dropbox", "player": MATCH, "name": ALL}, "value"),
        State("sess_id", "children"),
    ],
)
def creation_callback(n_buttons, v_states, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    # trigger = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = g_sessions[sess_id]["p_num"]
    p = g_players_list[p_num]
    for state in ctx.states_list[0]:
        p.p_data[state["id"]["name"]] = state["value"]
    for attribute in p.p_data["attribute"]:
        p.p_data["attribute"][attribute] = g_races_affinity[p.p_data["race"]][attribute][0]
    p.main_div.children = p.create_skill_dash()
    g_sessions[sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    return [""] * len(ctx.outputs_list)


@app.callback(
    Output("player-div-tmp", "children"),
    [Input("quit-button", "n_clicks")],
    [State("sess_id", "children")],
)
def quit_callback(n_buttons, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    gamemaster.disconnect_player(g_players_list[g_sessions[sess_id]["p_num"]])


@app.callback(
    Output({"type": "card-div_tmp", "card_name": MATCH}, "children"),
    [Input({"type": "card-button", "card_name": MATCH}, "n_clicks")],
    [State("sess_id", "children")],
)
def card_button_callback(n_buttons, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = g_sessions[sess_id]["p_num"]
    p = g_players_list[p_num]
    c_num = g_cards_name[trigger_obj["card_name"]]["channel"]
    print(p_num)
    print(c_num)
    g_card_channels[g_dict_player_channel[p.name]].style = {"display": "none"}
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    discord_move_p(str(p_num), str(c_num))


@app.callback(
    Output({"type": "player-div-private-tmp", "player": MATCH}, "children"),
    [Input({"type": "private-button", "player": MATCH}, "n_clicks")],
    [State("sess_id", "children")],
)
def private_button_callback(n_buttons, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        raise PreventUpdate
    p_num = g_sessions[sess_id]["p_num"]
    p = g_players_list[p_num]
    c_num = g_dict_player_channel[p.name]
    print(p_num)
    print(c_num)
    p.channel = c_num
    g_card_channels[p.channel].style = None
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    discord_move_p(str(p_num), str(c_num))
