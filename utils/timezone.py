from datetime import datetime
from zoneinfo import ZoneInfo


def get_ist_timestamp():
    ist = ZoneInfo("Asia/Kolkata")
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
