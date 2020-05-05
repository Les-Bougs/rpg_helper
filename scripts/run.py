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


from app import app
from index import index_layout, alert_connection



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
        )
])


def serve_layout():
    return page_layout


app.layout =  serve_layout


    
#callbacks
@app.callback(Output('h-div-data', 'children'),
              [Input({'type': 'd-button', 'name': ALL}, 'n_clicks')],
              [State({'type': 'd-input', 'name': ALL}, 'value')])
def update_output(button_n, input_v ):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    print(ctx.states)
    trigering_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    print(trigering_id)
    if trigering_id["type"] == "d-button":
        context, name = trigering_id["name"].split('-')
        if context == "connection":
            if name == "connect":
                player_file = open("../game_template/players.json")
                player_data = json.load(player_file)
                data={}
                pseudo = ctx.states['{"name":"pseudo","type":"d-input"}.value']
                password = ctx.states['{"name":"password","type":"d-input"}.value']
                print(pseudo+":"+password)
                for p in player_data:
                    if(p["pseudo"] == pseudo and p["password"]== password):
                        data = p
                if data == {}:
                    alert_connection.style = None
                else:
                    alert_connection.style = {'display': 'none'}
                    page_content.children = player.page(data["pseudo"])
                return json.dumps(data)
            if name == "new-player":
                #todo process to create a new player add it to the players.json file + lauch the player page
                return json.dumps(data)
        if context == "game":
            if name == "bt1":
                player.div_text[-1].children = "hey"
        #in-game button
        


    
@app.callback(Output('content', 'children'),
               [Input('h-div-data', 'children')])
def update_metrics(n):
     return page_content.children
    

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
