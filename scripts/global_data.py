import json

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
