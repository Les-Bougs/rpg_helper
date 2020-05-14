import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

import flask
import json

import player
import gamemaster


from app import app
from index import index_layout, alert_connection, alert_connection_text

import time

import numpy as np

# from django_plotly_dash.consumers import send_to_pipe_channel


page_content = html.Div(index_layout, id="content")

inter = dcc.Interval(
    id="update-timer",
    interval=1 * 1000,  # in milliseconds
    n_intervals=0,
    disabled=False,
)

page_layout = html.Div(
    [
        page_content,
        html.Div(id="h-div-data", style={"display": "none"}),
        dcc.Location(id="url", refresh=False),
        inter,
        dcc.Store(id="local", storage_type="session"),
    ]
)


def serve_layout():
    return page_layout


app.layout = serve_layout


# callbacks
@app.callback(
    Output("local", "data"),
    [Input({"type": "d-button", "name": ALL}, "n_clicks")],
    [State({"type": "d-input", "name": ALL}, "value")],
)
def update_output(button_n, input_v):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]["value"] == None:
        raise PreventUpdate

    print(ctx.triggered)
    ## Get the triggenring input
    trigering_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])

    ## If it's a button
    if trigering_id["type"] == "d-button":
        context, name = trigering_id["name"].split("-")

        ## if the context is the connection page
        if context == "connection":

            ## get the different data of the connection form
            data = ""
            pseudo = ctx.states['{"name":"pseudo","type":"d-input"}.value']
            password = ctx.states['{"name":"password","type":"d-input"}.value']
            GM = (
                "GM"
                in ctx.states['{"name":"connection-option","type":"d-input"}.value']
            )

            if pseudo == None or password == None:
                alert_connection_text.children = "Please enter a pseudo and a password"
                alert_connection.style = None
                data = None

            ## if it's a connection attempt
            elif name == "connect":

                print(pseudo + ":" + password)
                ## Search for player in the json data and compare password
                if (pseudo in game_data) and game_data[pseudo]["password"] == password:
                    data = {"name": pseudo}
                    p = game_data[pseudo]
                ## If no player found display a warning message on the index page
                if data == None:
                    print("1")
                    alert_connection_text.children = "Wrong Pseudo or Password"
                    alert_connection.style = None

                else:
                    ## Test if the client is connecting with the right statue
                    is_gm = p["gm"] == "yes"

                    if GM != is_gm:
                        print("bla")
                        alert_connection_text.children = "Wrong statue GM/player"
                        alert_connection.style = None
                        data = {}

                    ## If everything is good
                    else:
                        alert_connection.style = {"display": "none"}

                        ## If game master
                        if is_gm:
                            gamemaster.page_layout.children = gamemaster.page(pseudo)

                        ## If player
                        else:
                            p = player.Player(pseudo, game_data[pseudo])
                            
                            game_data[data["name"]]["session_num"] = len(players_list)
                            players_list.append(p)
                            gamemaster.div_players.append(gamemaster.player_line(p))

            ## If it's a new player attempt
            elif name == "new-player":
                pass  # todo process to create a new player add it to the players.json file + lauch the player page

            ## return the player /GM profil if one was found/created
            return json.dumps(data)

        ## Stuff during the game context
        if context == "gm":
            p_num = int(name.split("_")[0])
            bt = name.split("_")[1]
            bonus = 0
            if bt == "easy":
                bonus = 10
            elif bt == "medium":
                bonus = 0
            else:
                bonus = -10

            players_list[p_num].result = bonus
            players_list[p_num].btn_div.style = {"display": "none"}

            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(
    Output("content", "children"),
    [Input("local", "data"), Input("update-timer", "n_intervals")],
)
def update_metrics(data, interval):

    ## if no data previously store send the client on the index page
    ctx = dash.callback_context

    if not ctx.triggered or data == None or data == "{}":
        raise PreventUpdate

    name = json.loads(data)["name"]
    ## if player
    if game_data[name]["gm"] == "no" and len(players_list) > 0:
        p_num = game_data[name]["session_num"]
        p = players_list[p_num]
        return p.layout
    ## if Game Master
    elif game_data[name]["gm"] == "yes":
        return gamemaster.page_layout


game_file = open("../game_template/players.json")
game_data = json.load(game_file)
players_list = player.players_list


def save_game(g):
    pass


def update_game(p, g):
    ## add/update player data in game data
    pass


def get_player_data(g, pseudo):
    # return the player data
    pass


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
