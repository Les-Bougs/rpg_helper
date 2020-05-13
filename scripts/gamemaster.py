import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.dependencies import Input, Output



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
            dbc.Jumbotron(dbc.Row(html.Div(name + " The Game Master" ))),
            html.Div(div_players)
        ])
    return html.Div([navbar, body])



div_players = []
page_layout = html.Div(page("none"))
