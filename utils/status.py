from mcstatus import JavaServer
import os
import json

STATUS_FILE = "data/status.json"


def get_status():
    """
    Reads the server status from the JSON file and returns a formatted string.
    """

    if not os.path.exists(STATUS_FILE):
        return "Serwer offline"

    with open(STATUS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return "Serwer offline"

    if data.get("status") != "players":
        return data.get("status", "Serwer offline")

    try:
        server = JavaServer.lookup("easylife2.pl")
        status = server.status()
        return f"{status.players.online}/{status.players.max} Graczy"
    except Exception:
        return "Serwer offline"
