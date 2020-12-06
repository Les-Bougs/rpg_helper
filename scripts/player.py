import json
import numpy as np
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate


from global_data import (
    g_data,
    g_sessions,
    g_players_list,
    g_gm_list,
    g_ressources,
    g_races,
    g_classes,
    g_attributes,
    g_races_affinity,
    g_verbose,
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
        self.cards = []
        self.create_layout()
        self.create_gm_interface()

    def create_gm_interface(self):
        self.is_rolling = False
        self.result = -1
        self.attribute_tested = html.H3("hoy")
        self.result_div = html.Div("Result: ")
        self.btn_div = html.Div(
            [
                self.attribute_tested,
                dbc.Button(
                    "easy",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "easy",
                    },
                    className="mr-1",
                ),
                dbc.Button(
                    "medium",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "medium",
                    },
                    className="mr-1",
                ),
                dbc.Button(
                    "hard",
                    id={
                        "type": "difficulty-button",
                        "player": self.sess_id,
                        "name": "hard",
                    },
                    className="mr-1",
                ),
            ],
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
                    id={"type": "rolling-div", "player": str(self.num), "name": "tmp",},
                    style={"display": "none"},
                ),
                dbc.Col(ressource_bar),
                dbc.NavItem(dbc.NavLink("Link", href="#")),
                dbc.DropdownMenu(
                    nav=True,
                    in_navbar=True,
                    label="Menu",
                    children=[
                        dbc.DropdownMenuItem("Entry 1"),
                        dbc.DropdownMenuItem("Entry 2"),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Quit", id="quit-button"),
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
        return dbc.Col([dbc.Row(html.H1(self.name)),
                        dbc.Row(html.H3(self.raceName + " " + self.className)),
                        html.Div(self.skill_dash),
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
                        dbc.Button(
                            f"{skill} roll",
                            id={
                                "type": "rolling-button",
                                "player": str(self.num),
                                "name": f"{skill}",
                            },
                            className="d-button",
                        ),
                    ],
                    align="center",
                ),
            ]
        )


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
    value = p.p_data["attribute"][attr]
    p.skill_bar_obj[attr]["progress_bar"].value = value
    p.skill_bar_obj[attr]["progress_bar"].children = str(value)
    p.skill_bar_obj[attr]["button_inc"].disabled = True
    g_sessions[sess_id]["update"] = True
    return value


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
    g_sessions[sess_id]["update"] = True
    while p.is_rolling is True:
        time.sleep(1)
    bonus = p.bonus
    value = p.p_data["attribute"][attr]
    target = value + bonus
    dice = np.random.randint(0, 100)
    if target >= dice:
        result = "SUCCESS ✅"
    else:
        result = "FAIL ❌"
    if g_verbose:
        print(
            "["
            + sess_id[:8]
            + "-"
            + g_sessions[sess_id]["name"]
            + "] Rolled ("
            + result
            + ")"
        )
    result_out = f"{result}\t\t(dice : {dice}, skill : {target} ({value}+{bonus}))"
    for a in p.roll_outs:
        p.roll_outs[a].children = result_out if a == attr else ""

    p.result_div.children = attr + " test: " + result_out
    g_sessions[sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
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
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate
    trigger = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
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
    [State("sess_id", "children"),],
)
def creation_callback(n_buttons, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate
    gamemaster.disconnect_player(g_players_list[g_sessions[sess_id]["p_num"]])
