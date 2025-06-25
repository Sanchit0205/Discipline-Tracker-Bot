from utils.json_store import load_json, save_json

# 🔄 Task-based waiting (your existing logic)
def set_waiting_count(user_id, task, date):
    waiting = load_json("waiting_count.json")
    waiting[str(user_id)] = {"task": task, "date": date}
    save_json("waiting_count.json", waiting)

def get_waiting_count(user_id):
    waiting = load_json("waiting_count.json")
    return waiting.get(str(user_id))

def clear_waiting_count(user_id):
    waiting = load_json("waiting_count.json")
    if str(user_id) in waiting:
        del waiting[str(user_id)]
        save_json("waiting_count.json", waiting)

# 🧠 Coach mode state (NEW logic)
def set_coach_mode(user_id: str, value: bool):
    data = load_json("coach_mode.json")
    data[str(user_id)] = value
    save_json("coach_mode.json", data)

def is_in_coach_mode(user_id: str) -> bool:
    data = load_json("coach_mode.json")
    return data.get(str(user_id), False)
