import json
from datetime import datetime

DATA_FILE = "stats.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "starts": [],
            "buy_clicks": 0
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_start(user_id: int):
    data = load_data()

    if user_id not in data["starts"]:
        data["starts"].append(user_id)

    save_data(data)


def log_buy_click():
    data = load_data()
    data["buy_clicks"] += 1
    save_data(data)


def get_stats():
    data = load_data()

    return {
        "users": len(data["starts"]),
        "buy_clicks": data["buy_clicks"]
    }