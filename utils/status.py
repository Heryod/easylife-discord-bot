from mcstatus import JavaServer
import os
import json
from config import Files


def get_status():
    """
    Reads the server status from the JSON file and returns a formatted string.
    """

    if not os.path.exists(Files.STATUS_FILE):
        return "Serwer offline"

    with open(Files.STATUS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return "Serwer offline"

    if data.get("status") != "players":
        return data.get("status", "Serwer offline")

    try:
        server = JavaServer.lookup("easylife2.pl", timeout=5)
        status = server.status()
        return f"{status.players.online}/{status.players.max} Graczy"
    except Exception:
        return "Serwer offline"
