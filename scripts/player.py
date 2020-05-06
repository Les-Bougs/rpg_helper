import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.dependencies import Input, Output


div_text = []

pages = []

def page(name):
    div_text.append(html.P( "kejfzek.",className="lead"))
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
            dbc.Jumbotron(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H1(name, className="display-3"),
                                    div_text[-1],
                                ],width={"size": 3, "offset":1}),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Button("bt1",id={"type":"d-button", "name":"game-bt1"},className="mr-1"),
                                            dbc.Button("bt2",className="mr-1")
                                        ]
                                    ),
                                ],width={"size": 4})
                        ]),
                ])
        ])
    return html.Div([navbar, body])


