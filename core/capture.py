import json, os
from datetime import datetime
from core.config import CAPTURE_FILE, LOG_DIR

def save(data_type, target, data, ip="unknown"):
    os.makedirs(LOG_DIR, exist_ok=True)
    try:
        with open(CAPTURE_FILE, "r") as f:
            all_data = json.load(f)
    except:
        all_data = []

    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": data_type,
        "target": target,
        "ip": ip,
        "data": data
    }
    all_data.append(entry)
    with open(CAPTURE_FILE, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    return entry

def load_all():
    try:
        with open(CAPTURE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def get_by_type(data_type):
    return [e for e in load_all() if e.get("type") == data_type]
