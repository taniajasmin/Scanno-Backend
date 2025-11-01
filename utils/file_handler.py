import json
import os
from threading import Lock

DATA_PATH = "config/admin_data.json"
lock = Lock()

def read_admin_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("admin_data.json not found.")
    with lock:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def write_admin_data(data: dict):
    with lock:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
