achievements = {
    "FirstModel": {
        "counter": 0,
        "foractive": 1,
        "activated": False,
    },
    "FirstTrash": {
            "counter": 0,
            "foractive": 1,
            "activated": False,
        }
}

def CheckAchievement(achiv, message, title, tray):
    if not achievements[achiv]["activated"]:
        achievements[achiv]["counter"] += 1
        if achievements[achiv]["counter"] is achievements[achiv]["foractive"]:
            tray.showMessage(title, message)
            achievements[achiv]["activated"] = True