import os, json

PATH = os.path.dirname(__file__) + "/../../assets/"
ASSETS_PATH = PATH if os.path.exists(PATH) else os.path.dirname(__file__) + "/assets/"
with open(ASSETS_PATH + "settings.json", "r") as file:
    data = json.load(file)