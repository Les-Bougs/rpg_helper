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

def create_row():
    return html.Div(
        id="test",
        className="row row-skill",
        children=[
            html.Div(
                id="ed",
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children= html.Button(
                    id="id",
                    className="metric-row-button",
                    children="test",
                    title="Click to visualize live SPC chart",
                    n_clicks=0,
                ),
            ),
            html.Div(
                id="ed",
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children= daq.GraduatedBar(
                    id="bar",
                    color={
                        "ranges": {
                            "#f45060": [0, 30],
                            "#f4d44d ": [30, 70],
                            "#92e0d3": [70, 100],
                        }
                    },
                    showCurrentValue=False,
                    max=100,
                    value=55,
                ),
            ),
            html.Div(
                id="ed",
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children= dbc.Button("View details", color="secondary"),
            ),
        ]),

body = dbc.Container(
    [
        #dbc.Row(dbc.Col(html.Div("Skills"))),
        dbc.Row(
            [
                dbc.Button("Force", id="example-button",className="mr-2"),
                dbc.Popover(
                    [
                        dbc.PopoverHeader("Popover header"),
                        dbc.PopoverBody("And here's some amazing content. Cool!"),
                    ],
                    id="popover",
                    is_open=False,
                    target="example button",
                ),
                dbc.Col(dbc.Progress(value=75, striped=True)),
                dbc.Button("New",className="mr-1"),
            
            ],
        )
    ],
    className="mt-4",
)



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, body])



@app.callback(
    Output("popover", "is_open"),
    [Input("example-button", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == "__main__":
    app.run_server()
