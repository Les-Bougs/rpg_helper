import json
import numpy as np
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_auth
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
from app import app


class Player:
    def __init__(self, name, sess_id, data):
        self.sess_id = sess_id
        self.p_data = data
        self.name = name
        self.num = data["session_num"]
        self.create_layout()
        self.create_gm_interface()

    def create_gm_interface(self):
        self.is_rolling = False
        self.result = -1
        self.attribute_tested = html.H1("hoy")
        self.result_div = html.Div("Result: ")
        self.btn_div = html.Div(
            [
                self.attribute_tested,
                dbc.Button(
                    "easy",
                    id={
                        "type": "difficulty-button",
                        "player": str(self.num),
                        "name": "easy",
                    },
                    className="mr-1",
                ),
                dbc.Button(
                    "medium",
                    id={
                        "type": "difficulty-button",
                        "player": str(self.num),
                        "name": "medium",
                    },
                    className="mr-1",
                ),
                dbc.Button(
                    "hard",
                    id={
                        "type": "difficulty-button",
                        "player": str(self.num),
                        "name": "hard",
                    },
                    className="mr-1",
                ),
            ],
            style={"display": "none"},
        )

    def create_layout(self):
        self.roll_outs = {}
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
                        dbc.DropdownMenuItem("Entry 3"),
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
        return html.Div(self.skill_dash)

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
            ),
        )

    def create_ressource_bar(self):
        list_ress = []
        for ress, value in self.p_data["ressource"].items():
            list_ress.append(
                html.Div(
                    [
                        dbc.Row(
                            html.Div(
                                f"{ress} : {value}",
                                id={"type": f"ress-{ress}", "index": f"ress-{ress}"},
                            )
                        ),
                    ]
                )
            )
        return list_ress

    def skill_bar(self, skill, value):
        out = html.Div(
            "", id={"type": "rolling-div", "player": str(self.num), "name": f"{skill}",}
        )
        self.roll_outs[skill] = out
        return html.Div(
            [
                dbc.Row(dbc.Col(html.Div(skill))),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                dbc.Progress(
                                    f"{value}",
                                    value=value,
                                    striped=False,
                                    style={"height": "30px"},
                                    id={"type": "d-bar", "index": f"{skill}"},
                                )
                            )
                        ),
                        dbc.Button(
                            f"-",
                            id={"type": "d-button-dec", "index": f"{skill}"},
                            className="d-button",
                        ),
                        dbc.Button(
                            f"+",
                            id={"type": "d-button-inc", "index": f"{skill}"},
                            className="d-button",
                        ),
                        dbc.Col(out),
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


# WRITE BAR VALUE
@app.callback(
    Output({"type": "d-bar", "index": MATCH}, "children"),
    [Input({"type": "d-bar", "index": MATCH}, "value")],
)
def update_bar_display(input_value):
    return input_value


# INCREASE/DECREASE BAR
@app.callback(
    Output({"type": "d-bar", "index": MATCH}, "value"),
    [
        Input({"type": "d-button-inc", "index": MATCH}, "n_clicks"),
        Input({"type": "d-button-dec", "index": MATCH}, "n_clicks"),
    ],
    [State({"type": "d-bar", "index": MATCH}, "value")],
)
def update_bar_value(n_inc, n_dec, value):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    button_type = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["type"]
    if button_type == "d-button-inc" and value < 100:
        return min(value + 10, 100)
    elif button_type == "d-button-dec" and value > 0:
        return max(value - 10, 0)
    return value


## ROLL
@app.callback(
    Output({"type": "rolling-div", "player": MATCH, "name": "tmp"}, "children"),
    [Input({"type": "rolling-button", "player": MATCH, "name": ALL}, "n_clicks")],
    [State("sess_id", "children")],
)
def roll_skill(n_inc, sess_id):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate
    trigger_obj = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    attr = trigger_obj["name"]
    p_num = int(trigger_obj["player"])
    p = g_players_list[p_num]

    p.attribute_tested.children = attr
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
    while p.is_rolling == True:
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
    result_out = f"{result} (dice : {dice}, skill : {target} ({value}+{bonus}))"
    for a in p.roll_outs:
        p.roll_outs[a].children = result_out if a == attr else ""
    p.result_div.children = "Result: " +result_out
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
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate
    trigger = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    p_num = int(trigger["player"])
    p = g_players_list[p_num]
    for state in ctx.states_list[0]:
        p.p_data[state["id"]["name"]] = state["value"]
    for attribute in p.p_data["attribute"]:
        p.p_data["attribute"][attribute] = g_races_affinity[p.p_data["race"]][
            attribute
        ][0]
    p.main_div.children = p.create_skill_dash()
    g_sessions[sess_id]["update"] = True
    for gm_id in g_gm_list:
        g_sessions[gm_id]["update"] = True
    return [""] * len(ctx.outputs_list)
