import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_auth

from dash.dependencies import Input, Output, State, MATCH, ALL

from dash.exceptions import PreventUpdate
import json


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
