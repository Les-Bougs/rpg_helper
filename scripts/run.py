import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL

import flask
import json
import uuid
import datetime

import index
import player
import gamemaster

from global_data import game_data, players_list, session_data
from app import app


from flask import request   
  





def serve_layout():
    
    sess_id = str(uuid.uuid4())
    sess_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    exist = False
    print(session_data)
    for sess in session_data:
        if session_data[sess]["IP_add"] == sess_ip and session_data[sess]["time_stamp"] > datetime.datetime.now() - datetime.timedelta(seconds=2):
            print("same")
            sess_id = sess
            exist = True
            break


    if exist == False:
        print("new connexion:")
        session_data[sess_id] = {"error": False, "name":"", "IP_add":sess_ip , "time_stamp": datetime.datetime.now()}
        print(session_data[sess_id])

    print(session_data)
        
    return  html.Div(
        [
            html.Div(index.index_layout, id="content"),
            html.Div(sess_id, id="sess_id", style={"display": "none"}),
            dcc.Location(id="url", refresh=False),
            dcc.Interval(
                id="update-timer",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
                disabled=False,
            ),
        ]
    )


app.layout = serve_layout


@app.callback(
    Output("content", "children"),
    [Input("sess_id", "children"),
     Input("update-timer", "n_intervals")],
)
def update_content(sess_id, interval):

    ## if no data previously store send the client on the index page
    ctx = dash.callback_context
    

    if(session_data[sess_id]["error"]==True):
        session_data[sess_id]["error"]=False
        return index.index_layout

    
    if not ctx.triggered or session_data[sess_id]["name"]== "":
        raise PreventUpdate
    

    name = session_data[sess_id]["name"]
    ## if player
    if game_data[name]["gm"] == "no" and len(players_list) > 0:
        p_num = game_data[name]["session_num"]
        p = players_list[p_num]
        return p.layout
    ## if Game Master
    elif game_data[name]["gm"] == "yes":
        return gamemaster.page_layout







if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
