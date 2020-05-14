import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_auth

from dash.dependencies import Input, Output, State, MATCH, ALL

from dash.exceptions import PreventUpdate

from app import app

import json
import numpy as np
import time


class Player:
    
    def __init__(self, name, data):
        self.name = name
        self.p_data = data
        self.num = data["session_num"]

        self.roll_outs = []
        self.create_layout()
        
        
        self.btn_easy = dbc.Button("easy",id={"type":"d-button", "name":"gm-"+str(self.num)+"_easy"},className="mr-1")
        self.btn_medium = dbc.Button("medium",id={"type":"d-button", "name":"gm-"+str(self.num)+"_medium"},className="mr-1")
        self.btn_hard = dbc.Button("hard",id={"type":"d-button", "name":"gm-"+str(self.num)+"_hard"},className="mr-1")

        self.btn_div = html.Div([
            self.btn_easy,
            self.btn_medium,
            self.btn_hard], style={'display': 'none'})

        self.result = -1

    def create_layout(self):
        p = self.p_data
        
        skilldash = self.create_skill_dash()
        ressource_bar = self.create_ressource_bar()
        ## NAVBAR
        navbar = dbc.NavbarSimple(
            children=[
                dbc.Col(
                    ressource_bar
                ),
                
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

        
        body = dbc.Container(
            [
                skilldash
            ],
            className="skilldash_class",
        )

        self.layout =  html.Div([navbar, body])

    def create_skill_dash(self):
        self.skill_dash = []
        for skill, value in self.p_data["skills"].items():
            self.skill_dash.append(self.skill_bar(skill, value))
        return html.Div(self.skill_dash)
        
    def create_ressource_bar(self):
        list_ress = []
        for ress, value in self.p_data["ressource"].items():
            list_ress.append(
                html.Div(
                    [
                        dbc.Row(
                            html.Div(f'{ress} : {value}',
                                     id={'type':f'ress-{ress}', 'index':f'ress-{ress}'})
                        ),
                    ]
                )
            )
        return list_ress


    def skill_bar(self, skill, value):
        out = html.Div("hey",id={'type':'d-roll-out', 'index':f"{skill}"})
        self.roll_outs.append(out)
        return html.Div(
            [
                dbc.Row(dbc.Col(html.Div(skill))),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(dbc.Progress(f"{value}", value=value,
                                                  striped=False, style={"height": "30px"},
                                                  id={'type':'d-bar', 'index':f"{skill}"})
                            )
                        ),
                        dbc.Button(
                            f"-", id={'type':'d-button-dec', 'index':f"{skill}"},
                            className="d-button"
                        ),
                        dbc.Button(
                            f"+", id={'type':'d-button-inc', 'index':f"{skill}"},
                            className="d-button"
                        ),
                        dbc.Col(out),
                        dbc.Button(
                            f"{skill} roll", id={'type':'d-button-roll', 'index':f"{skill}"},
                            className="d-button"
                        ),
                    ],
                    align="center"
                )
            ]
        )


players_list = []

# TODO: Find better way to get dict_input
game_file = open("../game_template/players.json")
game_data = json.load(game_file)

skillset = game_data["Nini"]["skills"]
ressource = game_data["Nini"]["ressource"]

dict_input = {key: i for i, key in enumerate(skillset)}
# /TODO

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
    Output({"type": "d-roll-out", "index": ALL}, "children"),
    [Input({"type": "d-button-roll", "index": ALL}, "n_clicks")],
    [State({"type": "d-bar", "index": ALL}, "value"), State("local", "data")],
)
def roll_skill(n_inc, value, data):
    ctx = dash.callback_context
    inputs = ctx.inputs

    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    print(ctx.triggered)

    trigger = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["index"]
    trigger_id = dict_input[trigger]
    value = value[trigger_id]

    name = json.loads(data)["name"]
    jdata = game_data[name]

    p_num = game_data[name]["session_num"]
    p = players_list[p_num]
    players_list[p_num].btn_div.style = None

    while p.result == -1:
        print("hey")
        time.sleep(1)
    bonus = p.result
    p.result = -1

    print(jdata["skills"][trigger])
    print(trigger)

    target = value + bonus
    dice = np.random.randint(0, 100)
    if target >= dice:
        result = "SUCCESS ✅"
    else:
        result = "FAIL ❌"
    result_out = f"{result} (dice : {dice}, skill : {target} ({value}+{bonus}))"
    out = [""] * (len(inputs.keys()))
    out[trigger_id] = result_out

    for i in range(len(p.roll_outs)):
        p.roll_outs[i].children = out[i]

    return out