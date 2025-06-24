from datetime import datetime
from zoneinfo import ZoneInfo

print("Asia/Kolkata:", datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
print("System time :", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
