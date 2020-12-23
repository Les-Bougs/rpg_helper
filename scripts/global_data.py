import json
import dash_bootstrap_components as dbc
import dash_html_components as html
import socket


from app import app

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
g_cards = [dbc.Card([dbc.CardImg(src=app.get_asset_url(g_config["cards"][card_name]["src"]), top=True),
                     dbc.CardBody(
                         [
                             html.H4(card_name, className="card-title"),
                             html.P(g_config["cards"][card_name]["description"], className="card-text"),
                             html.P("", className="card-text"),
                             dbc.Button("go",
                                        id={"type": "card-button",
                                            "card_name": card_name},
                                        className="d-button"),
                             html.Div(id={"type": "card-div_tmp",
                                          "card_name": card_name},
                                      style={"display": "none"})
                         ])],
                    style={"width": "18rem"}) for card_name in g_config["cards"]]
g_objects = g_config["objects"]
g_objects_array = [{"label": name, "value": name} for name in g_objects]

g_dict_player_channel = {}

g_diff = {'easy': {'a': 0.30, 'b': 65},
          'mkay': {'a': 0.60, 'b': 20},
          'hard': {'a': 0.40, 'b': 10},
          'nope': {'a': 0.25, 'b': 5}}


g_guild = []

g_socket_param = {"host": '127.0.0.1',  # The server's hostname or IP address
                  "port": 65000,
                  "connected": False}        # The port used by the server

g_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


g_card_channels = []


def discord_connect():
    try:
        g_socket.connect((g_socket_param["host"], g_socket_param["port"]))
        g_socket.sendall(bytearray(('N:').ljust(50, 'x'), 'latin-1'))
    except Exception:
        print("[Discord BOT] Communication error")


def discord_setup_p(p_num, p_name):
    try:
        g_socket.sendall(bytearray(('S:'+p_num+':'+p_name+':').ljust(50, 'x'), 'latin-1'))
    except Exception:
        pass


def discord_move_p(p_num, c_num):
    try:
        g_socket.sendall(bytearray(('M:'+p_num+':'+c_num+':').ljust(50, 'x'), 'latin-1'))
    except Exception:
        pass


def discord_create_c(c_num):
    try:
        g_socket.sendall(bytearray(('C:'+c_num+':').ljust(50, 'x'), 'latin-1'))
    except Exception:
        pass


def discord_bonus_p(p_num, attr, val):
    try:
        g_socket.sendall(bytearray(('B:'+p_num+':'+attr+':'+val+':').ljust(50, 'x'), 'latin-1'))
    except Exception:
        pass
