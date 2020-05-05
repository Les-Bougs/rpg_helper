import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_auth

from dash.dependencies import Input, Output, State, MATCH

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
    brand="Les Bougs - le RPG",
    brand_href="#",
    sticky="top",
)


def create_skill_dash(skillset):
    skill_dash = []
    for skill, value in skillset.items():
        skill_dash.append(skill_bar(skill, value))
    return html.Div(skill_dash)


def skill_bar(skill, value):
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
                    dbc.Col(html.Div(id=f'{skill}-score')),
                    dbc.Button(
                        f"{skill} +", id={'type':'d-button-inc', 'index':f"{skill}"},
                        className="d-button"
                    ),
                    dbc.Button(
                        f"{skill} -", id={'type':'d-button-dec', 'index':f"{skill}"},
                        className="d-button"
                    ),
                ],
                align="center"
            )            
        ]
    )


skillset = {'Strength':30, 'Agility':40, 'Health': 76}
skilldash = create_skill_dash(skillset)


body = dbc.Container(
    [
        skilldash
    ],
    className="skilldash_class",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# # PASSWORD SECURE
# VALID_USERNAME_PASSWORD_PAIRS = []
# with open('password_pairs.txt') as f:
#     content = f.readlines()
#     for pair in content:
#         pair = pair.replace('\n','').split(', ')
#         VALID_USERNAME_PASSWORD_PAIRS.append(pair)

# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

app.layout = html.Div([navbar, body])

# WRITE BAR VALUE
@app.callback(
    Output({'type': 'd-bar', 'index': MATCH}, 'children'),
    [Input({'type': 'd-bar', 'index': MATCH}, 'value')]
)
def update_bar_display(input_value):
    return input_value

# INCREASE/DECREASE BAR
n_inc_prev, n_dec_prev = None, None
@app.callback(
    Output({'type': 'd-bar', 'index': MATCH}, 'value'),
    [Input({'type': 'd-button-inc', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'd-button-dec', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'd-bar', 'index': MATCH}, 'value')],
)
def update_bar_value(n_inc, n_dec, value):
    global n_inc_prev, n_dec_prev
    if not n_inc and not n_dec:
        return value
    if n_inc != n_inc_prev and value <100:
        n_inc_prev = n_inc      
        return min(value + 10, 100)
    elif n_dec != n_dec_prev and value >0:
        n_dec_prev = n_dec     
        return max(value - 10, 0)
    return value

if __name__ == "__main__":
    app.run_server()
