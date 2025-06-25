# notify_users.py

import asyncio
import json
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

# Paths
USERS_FILE = "data/users.json"
NOTIFIED_FILE = "data/notified_users.json"

# Load users (handle list or dict)
with open(USERS_FILE, "r") as f:
    raw_data = json.load(f)

# ✅ Support both formats
if isinstance(raw_data, list):
    user_ids = [str(uid) for uid in raw_data]
else:
    user_ids = list(raw_data.get("users", {}).keys())

# Load notified user history
if os.path.exists(NOTIFIED_FILE) and os.path.getsize(NOTIFIED_FILE) > 0:
    with open(NOTIFIED_FILE, "r") as f:
        notified_users = set(json.load(f))
else:
    notified_users = set()


# 📢 Your message
message = (
    "🧠 *New Update! AI Coach is now smarter.*\n\n"
    "No need to type '/coach' every time — just start chatting!\n"
    "Use [/coach] to begin and [/exitcoach] to stop anytime.\n\n"
    "Your coach now responds freely like a real trainer. 💬💪"
)



# 🔁 Async function to send to unnotified users only
async def broadcast():
    updated_notified = set(notified_users)
    for user_id in user_ids:
        if str(user_id) not in notified_users:
            try:
                await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
                print(f"✅ Sent to {user_id}")
                updated_notified.add(str(user_id))
            except Exception as e:
                print(f"❌ Failed to send to {user_id}: {e}")
    
    # Save updated notified list
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(list(updated_notified), f, indent=2)

# Run it
asyncio.run(broadcast())
