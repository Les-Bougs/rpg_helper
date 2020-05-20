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
from global_data import g_players_list, g_sessions, g_verbose
from app import app


from flask import request


def serve_layout():
    sess_id = str(uuid.uuid4())  # create an ID
    sess_ip = request.environ.get(
        "HTTP_X_REAL_IP", request.remote_addr
    )  # Get IP of the client

    # Check if the ip already tried to connect less than 2sec ago or is remembered
    exist = False
    for sess in g_sessions:
        dt = datetime.datetime.now() - datetime.timedelta(seconds=2)
        if g_sessions[sess]["IP_add"] == sess_ip and (
            g_sessions[sess]["time_stamp"] > dt or g_sessions[sess]["rem"] == True
        ):
            sess_id = sess
            exist = True
            g_sessions[sess_id]["update"] = True
            break

    if exist == False:
        if g_verbose:
            print("[" + sess_id[:8] + "] New session")
        g_sessions[sess_id] = {
            "error": "",
            "update": True,
            "name": "NONE",
            "IP_add": sess_ip,
            "time_stamp": datetime.datetime.now(),
            "context": "index",
            "p_num": -1,
            "rem": False,
        }

    return html.Div(
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
    [Input("sess_id", "children"), Input("update-timer", "n_intervals")],
)
def update_content(sess_id, interval):

    ## if no data previously store send the client on the index page
    ctx = dash.callback_context

    layout = None
    if g_sessions[sess_id]["update"] == True:
        g_sessions[sess_id]["update"] = False
        context = g_sessions[sess_id]["context"]
        if g_verbose:
            print(
                "["
                + sess_id[:8]
                + "-"
                + g_sessions[sess_id]["name"]
                + "] Update Layout ("
                + context
                + "["
                + str(g_sessions[sess_id]["p_num"])
                + "])"
            )
        if context == "index":  ## Connection context
            if g_sessions[sess_id]["error"] == "":
                index.alert_connection.style = {"display": "none"}
            else:
                index.alert_connection.style = None
            index.alert_connection_text.children = g_sessions[sess_id]["error"]
            layout = index.index_layout
        elif context == "player":  ## Player context
            p_num = g_sessions[sess_id]["p_num"]
            if p_num != -1:
                layout = g_players_list[p_num].layout
        elif context == "gm":  ## if Game Master
            layout = gamemaster.page_layout
        return layout
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
