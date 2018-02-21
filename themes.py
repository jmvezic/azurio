import json

# themes_dict = {
#     "Dark": {
#         "BackgroundColor": "#2e3a50",
#         "ForegroundColor": "#ffffff",
#         "HighlightColor": "#ffb608",
#         "HighlightedTextColor": "#000000",
#         "BorderColor": "#888",
#         "AccentColor": "#ffb608",
#         "WarningColor": "#ffb608",
#     },
#     "Light": {
#         "BackgroundColor": "#f6f6f6",
#         "ForegroundColor": "#333333",
#         "HighlightColor": "#006ed7",
#         "HighlightedTextColor": "#f6f6f6",
#         "BorderColor": "#cccccc",
#         "AccentColor": "#006ed7",
#         "WarningColor": "#006ed7",
#     }
# }

themes_dict = {}

def LoadThemes():
    with open("themes.json") as json_data:
        themes_dict = json.load(json_data)
    return themes_dict

# with open("themes.json", "w") as fp:
#     json.dump(themes_dict, fp)