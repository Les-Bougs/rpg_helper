'''main file'''

# Dash library to create simple webpage
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import uuid
import datetime
from flask import request

from app import app
import index
import gamemaster
from global_data import g_players_list, g_sessions, g_verbose, g_socket_param, g_socket, g_cards_name, g_card_channels


def server_layout():
    '''return a layout when a user try to connect the server '''
    sess_id = str(uuid.uuid4())  # create an ID
    sess_ip = request.environ.get("HTTP_X_REAL_IP",
                                  request.remote_addr)  # Get IP of the client

    # # Check if the ip already tried to connect less than 2sec ago
    # # or is remembered
    exist = False
    # dt = datetime.datetime.now() - datetime.timedelta(seconds=2)
    # for sess in g_sessions:
    #     if g_sessions[sess]["IP_add"] == sess_ip and (
    #         g_sessions[sess]["time_stamp"] > dt or
    #             g_sessions[sess]["rem"] is True
    #     ):
    #         sess_id = sess  # Give previous id
    #         exist = True  # Set exist to show a previous user was found
    #         g_sessions[sess_id]["update"] = True
    #         break

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

    if g_socket_param["connected"] is not True:
        g_socket_param["connected"] = True
        g_socket.connect((g_socket_param["host"], g_socket_param["port"]))
        g_socket.sendall(bytearray(('N:').ljust(50, 'x'), 'latin-1'))
        index_c = 0
        for c in g_cards_name:
            if g_cards_name[c]['type'] == "place":
                g_cards_name[c]['channel'] = index_c
                g_socket.sendall(bytearray(('C:'+str(index_c)+':').ljust(50, 'x'), 'latin-1'))
                g_card_channels.append(dbc.Card([html.Div(id={"type": "channel-div",
                                                              "channel_num": str(index_c)
                                                              }, style={"display": "none"}),
                                                 dbc.CardHeader(c),
                                                 dbc.CardBody(html.P("")),
                                                 dbc.Button("join", id={"type": "channel-button",
                                                                        "channel_num": str(index_c)},
                                                            className="d-button")]))
                index_c += 1
                print("sent" + str(index_c))

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
