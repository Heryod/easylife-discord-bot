import json
import os

TICKETS_FILE = "data/tickets.json"


def save_ticket(ticket_data):
    if not os.path.exists(TICKETS_FILE):
        os.makedirs(os.path.dirname(TICKETS_FILE), exist_ok=True)
        with open(TICKETS_FILE, "w") as f:
            json.dump([], f)

    with open(TICKETS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append(ticket_data)

    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def delete_ticket(ticket_id: int):
    if not os.path.exists(TICKETS_FILE):
        return

    with open(TICKETS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return

    data = [t for t in data if t.get("ticket_id") != ticket_id]

    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_ticket(ticket_id: int):
    if not os.path.exists(TICKETS_FILE):
        return None
    with open(TICKETS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None
    for t in data:
        if t.get("ticket_id") == ticket_id:
            return t
    return None


def get_user_ticket_count(user_id: int) -> int:
    if not os.path.exists(TICKETS_FILE):
        return 0
    with open(TICKETS_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return 0
    return sum(1 for t in data if t.get("creator_id") == user_id)
