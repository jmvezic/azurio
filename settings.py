import json
from loaded_models import models

settings = {}

def LoadSettings():
    with open("settings.json") as json_data:
        d = json.load(json_data)
        settings = d
        models_list = []
        for x,y in models.items():
            models_list.append(x)
        settings["models"] = models_list
    return settings

def StoreSettings(settings_dict):
    with open('settings.json', 'w') as fp:
        json.dump(settings_dict, fp)