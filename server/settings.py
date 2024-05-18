import os, json

PATH = os.path.dirname(__file__) + "/../../settings.json"
SETTINGS_PATH = PATH if os.path.exists(PATH) else os.path.dirname(__file__) + "/settings.json"
with open(SETTINGS_PATH, "r") as file:
    data = json.load(file)