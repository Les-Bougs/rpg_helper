import json


game_file = open("../game_template/players.json")
game_data = json.load(game_file)

players_list = []

session_data = {}
