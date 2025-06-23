from telegram import Update
from telegram.ext import ContextTypes
from utils.json_store import load_json, save_json
from utils.constants import (
    STREAK_FILE, USER_FILE, WORKOUT_FILE, PROGRESS_FILE, GOAL_FILE,
    REMINDER_FILE, WAITING_COUNT_FILE, SLEEP_FILE, SLEEP_SENT_FILE,
    WORKOUT_SENT_FILE, SLEEP_REMINDER_FILE
)
from datetime import datetime, timedelta

async def set_sleep_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text(
            "❗ Usage: /setsleeptime HH:MM (24hr format)")
        return
    time = context.args[0]
    reminders = load_json("sleep_reminders.json")
    reminders[user_id] = time
    save_json("sleep_reminders.json", reminders)
    await update.message.reply_text(f"🌙 Sleep reminder set for {time} daily.")


async def log_sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text("❗ Usage: /sleeplog 7.5 (hours)")
        return
    try:
        hours = float(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❗ Please enter a valid number of hours.")
        return
    today = datetime.now().strftime('%Y-%m-%d')
    sleep_data = load_json(SLEEP_FILE)
    if user_id not in sleep_data:
        sleep_data[user_id] = {}
    sleep_data[user_id][today] = hours
    save_json(SLEEP_FILE, sleep_data)
    await update.message.reply_text(f"✅ Logged {hours} hours of sleep.")


async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    sleep_data = load_json(SLEEP_FILE)
    if user_id not in sleep_data:
        await update.message.reply_text(
            "❗ No sleep data found. Use /sleeplog to log.")
        return

    today = datetime.now()
    logs = []
    for i in range(7):
        day = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        if day in sleep_data[user_id]:
            logs.append(sleep_data[user_id][day])

    if not logs:
        await update.message.reply_text(
            "❗ No sleep entries in the past 7 days.")
        return

    avg = sum(logs) / len(logs)
    await update.message.reply_text(f"🛌 Avg sleep (last 7 days): {avg:.1f} hrs"
                                    )