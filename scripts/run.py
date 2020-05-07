import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

import flask
import json
import pandas as pd

import player
import gamemaster


from app import app
from index import index_layout, alert_connection, alert_connection_text

import time



page_content =  html.Div(index_layout,id='content' )

page_layout = html.Div([
    page_content,
    html.Div(id='h-div-data', style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(
        id='update-timer',
        interval=1*1000, # in milliseconds
        n_intervals=0,
        disabled=True
        ),
    dcc.Store(id='local', storage_type='session'),
])


def serve_layout():
    return page_layout


app.layout =  serve_layout


    
#callbacks
@app.callback(Output('local', 'data'),
              [Input({'type': 'd-button', 'name': ALL}, 'n_clicks')],
              [State({'type': 'd-input', 'name': ALL}, 'value')])
def update_output(button_n, input_v ):
    ctx = dash.callback_context

    ## If no trigering event raise no update
    if not ctx.triggered or ctx.triggered[0]['value']==None:
        raise PreventUpdate

    ## Get the triggenring input
    trigering_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])

    ## If it's a button
    if trigering_id["type"] == "d-button":
        context, name = trigering_id["name"].split('-')

        ## if the context is the connection page
        if context == "connection":

            ## get the different data of the connection form
            data={}
            pseudo = ctx.states['{"name":"pseudo","type":"d-input"}.value']
            password = ctx.states['{"name":"password","type":"d-input"}.value']
            GM = "GM" in ctx.states['{"name":"connection-option","type":"d-input"}.value']
            print(pseudo + ":" + password)
            ## if it's a connection attempt
            if name == "connect":

                ## Search for player in the json data and compare password
                for p in game_data:
                    print(p["pseudo"] + ":" + p["password"])
                    if(p["pseudo"] == pseudo and p["password"]== password):
                        data = p
                        break
                print(data)
                ## If no player found display a warning message on the index page
                if data == {}:
                    print("1")
                    alert_connection_text.children = "Wrong Pseudo or Password"
                    alert_connection.style = None
                
                else:
                    ## Test if the client is connecting with the right statue
                    is_gm = (p["gm"]=="yes")
                    
                    if GM != is_gm:
                        print("bla")
                        alert_connection_text.children = "Wrong statue GM/player"
                        alert_connection.style = None
                        data = {}

                    ## If everything is good
                    else:
                        alert_connection.style = {'display': 'none'}

                        ## If game master
                        if is_gm:
                            gamemaster.page_layout.children = gamemaster.page(data["pseudo"])

                        ## If player
                        else:
                            data["session_num"] = len(player.pages)
                            player.pages.append(player.page(data["pseudo"]))
                            gamemaster.div_players.append(gamemaster.player_line(data["pseudo"]))

            ## If it's a new player attempt
            if name == "new-player":
                pass #todo process to create a new player add it to the players.json file + lauch the player page

            ## return the player /GM profil if one was found/created
            return json.dumps(data)

        ## Stuff during the game context
        if context == "game":
            if name == "bt1":
                player.div_text[-1].children = "hey"
    else:
        raise PreventUpdate
        


    
@app.callback(Output('content', 'children'),
               [Input('local', 'data')])
def update_metrics(data):
    ## if no data previously store send the client on the index page
    if(data==None or data == "{}" ):
        return index_layout

    ## if previously connected 
    jdata = json.loads(data)

    ## if player
    if(jdata["gm"] == "no" and len(player.pages)>0):
        return player.pages[jdata["session_num"]]
    ## if Game Master
    elif(jdata["gm"] == "yes"):
        return gamemaster.page_layout

    
game_file = open("../game_template/players.json")
game_data = json.load(game_file)


def save_game(g):
    pass

def update_game(p, g):
    ## add/update player data in game data
    pass

def get_player_data(g, pseudo):
    #return the player data
    pass

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')

