import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html

from dash.dependencies import Input, Output, State

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
    brand="Demo",
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
                        striped=False, style={"height": "30px"}))
                    ),
                    dbc.Col(html.Div(id=f'{skill}-score')),
                    dbc.Button(f"{skill} +", id=f"inc-{skill}",className="d-button"),
                    dbc.Button(f"{skill} -", id=f"dec-{skill}",className="d-button")
                ],
                align="center"
            )            
        ]
    )


skillset = {'Strength':30, 'Agility':40, 'Health': 76}
skilldash = create_skill_dash(skillset)


body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(dbc.Progress(value=50, striped=True, id='prog'))),
                dbc.Button(f"+", id=f"inc-prog",className="d-button"),
                dbc.Button(f"-", id=f"dec-prog",className="d-button"),
            ]
        ),        
        dbc.Row(html.Div(id=f'disp-div')),
        skilldash
    ],
    className="mt-4",
)



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, body])

# WRITE BAR VALUE
@app.callback(
    Output(component_id='prog', component_property='children'),
    [Input(component_id='prog', component_property='value')]
)
def update_output_div(input_value):
    return input_value


n_inc_prev, n_dec_prev = None, None
# INCREASE/DECREASE BAR
@app.callback(
    Output("prog", "value"),
    [Input("inc-prog", "n_clicks"),Input("dec-prog", "n_clicks")],
    [State("prog", "value")],
)
def inc_bar(n_inc, n_dec, value):
    global n_inc_prev, n_dec_prev
    if not n_inc and not n_dec:
        return value
    if n_inc != n_inc_prev and value <100:
        n_inc_prev = n_inc      
        return value + 10
    elif n_dec != n_dec_prev and value >0:
        n_dec_prev = n_dec     
        return value - 10
    return value

if __name__ == "__main__":
    app.run_server()
