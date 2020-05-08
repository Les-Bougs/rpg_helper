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

navbar = dbc.NavbarSimple(
    children=[
        dbc.Col(
            html.Div(
                [
                    # dbc.Row(
                    #     html.Div(dbc.Progress(f"health", value=30,
                    #     striped=False, style={"height": "10px", "width":"250px"},
                    #     id={'type':'d-bar', 'index':f"health-bar"})
                    #     ),
                    # ),
                    dbc.Row(html.Div('Health : 90', id={'type':'out-health', 'index':'health'})),
                    dbc.Row(html.Div('Gold : 30', id={'type':'out-gold', 'index':'gold'})),
                ]
            ),
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


skillset = {'Strength':80, 'Agility':20,  'Stamina': 80, 'Charisma': 60}
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


# # roll
# @app.callback(
#     Output({'type': 'd-roll-out', 'index': ALL}, 'children'),
#     [Input({'type': 'd-button-roll', 'index': ALL}, 'n_clicks')],
#     [State({'type': 'd-bar', 'index': ALL}, 'value')]
# )
# def erase_roll(n_clicks, value):
#     print('erase')
#     ctx = dash.callback_context
#     inputs = ctx.inputs
#     # states = ctx.states
#     inputs_list = [(list(inputs.keys())[j])[10:].split('"')[0] for j in range(len(inputs.keys()))]
#     dict_in = {key:i for i,key in enumerate(inputs_list)}
#     if not ctx.triggered or ctx.triggered[0]['value']==None:
#         raise PreventUpdate
#     trigger = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
#     trigger_id = dict_in[trigger]
#     value = value[trigger_id]
#     # print('inputs : ', inputs)
#     # print('states : ', states)
#     # print('trigger : ', trigger)
#     out = [f'a+{n_clicks}', f'b+{n_clicks}', f'c+{n_clicks}']
#     out[trigger_id] = value
#     return out


@app.callback(
    Output({'type': 'd-roll-out', 'index': ALL}, 'children'),
    [Input({'type': 'd-button-roll', 'index': ALL}, 'n_clicks')],
    [State({'type': 'd-bar', 'index': ALL}, 'value')],
)
def roll_skill(n_inc, value):
    ctx = dash.callback_context
    inputs = ctx.inputs
    # states = ctx.states
    inputs_list = [(list(inputs.keys())[j])[10:].split('"')[0] for j in range(len(inputs.keys()))]
    dict_in = {key:i for i,key in enumerate(inputs_list)}
    if not ctx.triggered or ctx.triggered[0]['value']==None:
        raise PreventUpdate

    trigger = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    trigger_id = dict_in[trigger]
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


# @app.callback(
#     Output({'type': 'd-roll-out', 'index': MATCH}, 'children'),
#     [Input({'type': 'd-button-roll', 'index': MATCH}, 'n_clicks')],
#     [State({'type': 'd-bar', 'index': MATCH}, 'value')],
# )
# def roll_skill(n_inc, value):
#     ctx = dash.callback_context
#     if not ctx.triggered or ctx.triggered[0]['value']==None:
#         raise PreventUpdate

#     bonus = np.random.randint(0, 20) - 10
#     target = value + bonus
#     dice = np.random.randint(0, 100)
#     if target >= dice:
#         result = 'SUCCESS ✅'
#     else:
#         result = 'FAIL ❌'

#     return f'{result} (dice : {dice}, skill : {target} ({value}+{bonus}))'

if __name__ == "__main__":
    app.run_server()
