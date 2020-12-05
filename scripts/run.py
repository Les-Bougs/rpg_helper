'''main file'''

# Dash library to create simple webpage
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import uuid
import datetime
from flask import request

from app import app
import index
import gamemaster
from global_data import g_players_list, g_sessions, g_verbose


def server_layout():
    '''return a layout when a user try to connect the server '''
    sess_id = str(uuid.uuid4())  # create an ID
    sess_ip = request.environ.get("HTTP_X_REAL_IP",
                                  request.remote_addr)  # Get IP of the client

    # Check if the ip already tried to connect less than 2sec ago
    # or is remembered
    exist = False
    dt = datetime.datetime.now() - datetime.timedelta(seconds=2)
    for sess in g_sessions:
        if g_sessions[sess]["IP_add"] == sess_ip and (
            g_sessions[sess]["time_stamp"] > dt or
                g_sessions[sess]["rem"] is True
        ):
            sess_id = sess  # Give previous id
            exist = True  # Set exist to show a previous user was found
            g_sessions[sess_id]["update"] = True
            break

    if exist is False:  # If not an already existing user try to connect
        if g_verbose:
            print("[" + sess_id[:8] + "] New session")
        # Set its session information
        g_sessions[sess_id] = {
            "error": "",  # No error
            "update": True,  # Layout has to be updated
            "name": "NONE",  # Set the name of the user to none
            "IP_add": sess_ip,  # Set if IP address
            "time_stamp": datetime.datetime.now(),  # Set the timestamp
            "context": "index",  # Set its context to the index page
            "p_num": -1,  # No player numero yet
            "rem": False,  # Should not be remembered
        }

    return html.Div(  # Returns the layout of the index page
        [
            html.Div(index.index_layout, id="content"),
            html.Div(sess_id, id="sess_id", style={"display": "none"}),
            dcc.Location(id="url", refresh=False),
            # Object to reload the page frequently
            # by calling the function update_content
            dcc.Interval(
                id="update-timer",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
                disabled=False,
            ),
        ]
    )


# When the user try to connect it automatically get the layout
# returned by the function server_layout above
app.layout = server_layout


@app.callback(
    Output("content", "children"),
    [Input("sess_id", "children"), Input("update-timer", "n_intervals")],
)
def update_content(sess_id, interval):
    ''' This function is periodically called by the user's page
        to reload its content. To do so the function check the session context
        and return matching layout. '''

    layout = None
    # Test if the page need to be updated
    if g_sessions[sess_id]["update"] is True:
        g_sessions[sess_id]["update"] = False
        context = g_sessions[sess_id]["context"]  # Get the context of the ses
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
        if context == "index":  # Connection context
            if g_sessions[sess_id]["error"] == "":
                index.alert_connection.style = {"display": "none"}
            else:
                index.alert_connection.style = None
            index.alert_connection_text.children = g_sessions[sess_id]["error"]
            layout = index.index_layout
        elif context == "player":  # Player context
            p_num = g_sessions[sess_id]["p_num"]
            if p_num != -1:
                layout = g_players_list[p_num].layout
        elif context == "gm":  # if Game Master
            layout = gamemaster.page_layout
        return layout
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
