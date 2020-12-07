import json
import dash_bootstrap_components as dbc
import dash_html_components as html

g_verbose = True
data_file = open("../game_template/players.json")
g_data = json.load(data_file)

config_file = open("../game_template/config.json")
g_config = json.load(config_file)

g_players_list = []
g_gm_list = []

g_sessions = {}

g_attributes = g_config["attributes"]
g_ressources = g_config["ressources"]
g_classes = g_config["classes"]
g_races = g_config["races"]
g_races_affinity = g_config["races_affinity"]

g_cards_name = g_config["cards"]
g_cards = [dbc.Card([dbc.CardImg(src=g_config["cards"][card_name]["src"], top=True),
                     dbc.CardBody(
                         [
                            html.H4(card_name, className="card-title"),
                            html.P(g_config["cards"][card_name]["description"], className="card-text"),
                            html.P("", className="card-text")
                         ])],
                    style={"width": "28rem"}) for card_name in g_config["cards"]]
g_objects = g_config["objects"]
g_objects_array = [{"label": name, "value": name} for name in g_objects]
