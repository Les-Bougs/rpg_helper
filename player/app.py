import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_auth

from dash.dependencies import Input, Output, State, MATCH, ALL

from dash.exceptions import PreventUpdate
import json
import numpy as np

## DEF FUNCTIONS
def create_ressource_bar(ress_dict):
    list_ress = []
    for ress, value in ress_dict.items():
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
                    dbc.Button(
                        f"-", id={'type':'d-button-dec', 'index':f"{skill}"},
                        className="d-button"
                    ),
                    dbc.Button(
                        f"+", id={'type':'d-button-inc', 'index':f"{skill}"},
                        className="d-button"
                    ),
                    dbc.Col(html.Div(id={'type':'d-roll-out', 'index':f"{skill}"})),
                    dbc.Button(
                        f"{skill} roll", id={'type':'d-button-roll', 'index':f"{skill}"},
                        className="d-button"
                    ),
                ],
                align="center"
            )
        ]
    )

# INSTANCE VARIABLES
game_file = open("../game_template/players.json")
game_data = json.load(game_file)
for p in game_data:
    if p['pseudo'] == 'Nini':
        skillset = p['skills']
        ressource = p['ressource']

skilldash = create_skill_dash(skillset)
ressource_bar = create_ressource_bar(ressource)
dict_input = {key:i for i,key in enumerate(skillset)}

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

## LAYOUT CREATION
app.layout = html.Div([navbar, body])

## DEF CALLBACKS

# WRITE BAR VALUE
@app.callback(
    Output({'type': 'd-bar', 'index': MATCH}, 'children'),
    [Input({'type': 'd-bar', 'index': MATCH}, 'value')]
)
def update_bar_display(input_value):
    return input_value


# INCREASE/DECREASE BAR
@app.callback(
    Output({'type': 'd-bar', 'index': MATCH}, 'value'),
    [Input({'type': 'd-button-inc', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'd-button-dec', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'd-bar', 'index': MATCH}, 'value')],
)
def update_bar_value(n_inc, n_dec, value):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['value']==None:
        raise PreventUpdate

    button_type = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['type']
    if button_type == 'd-button-inc' and value <100:
        return min(value + 10, 100)
    elif button_type == 'd-button-dec' and value >0:
        return max(value - 10, 0)
    return value


## ROLL
@app.callback(
    Output({'type': 'd-roll-out', 'index': ALL}, 'children'),
    [Input({'type': 'd-button-roll', 'index': ALL}, 'n_clicks')],
    [State({'type': 'd-bar', 'index': ALL}, 'value')],
)
def roll_skill(n_inc, value):
    ctx = dash.callback_context
    inputs = ctx.inputs
<<<<<<< HEAD
=======
    
>>>>>>> 9999781ede3026df03e6a038cbc648730653c487
    if not ctx.triggered or ctx.triggered[0]['value']==None:
        raise PreventUpdate

    trigger = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    trigger_id = dict_input[trigger]
    value = value[trigger_id]

    bonus = np.random.randint(0, 20) - 10
    target = value + bonus
    dice = np.random.randint(0, 100)
    if target >= dice:
        result = 'SUCCESS ✅'
    else:
        result = 'FAIL ❌'
    result_out = f'{result} (dice : {dice}, skill : {target} ({value}+{bonus}))'
    out = ['']*(len(inputs.keys()))
    out[trigger_id] = result_out
    return out


if __name__ == "__main__":
    app.run_server()
