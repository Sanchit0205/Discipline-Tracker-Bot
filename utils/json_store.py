import json, os

DATA_PATH = "data"

def load_json(filename):
    filepath = os.path.join(DATA_PATH, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    return {}

def save_json(filename, data):
    # Ensure the data directory exists
    os.makedirs(DATA_PATH, exist_ok=True)
    filepath = os.path.join(DATA_PATH, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
