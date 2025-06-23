from telegram import Update
from telegram.ext import ContextTypes
from utils.json_store import load_json, save_json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.constants import (
    STREAK_FILE, USER_FILE, WORKOUT_FILE, PROGRESS_FILE, GOAL_FILE,
    REMINDER_FILE, WAITING_COUNT_FILE, SLEEP_FILE, SLEEP_SENT_FILE,
    WORKOUT_SENT_FILE, SLEEP_REMINDER_FILE
)
from datetime import datetime, timedelta



async def send_sleep_reminders(app):
    reminders = load_json("sleep_reminders.json")
    sent_status = load_json(SLEEP_SENT_FILE)

    now = datetime.utcnow() + timedelta(hours=5,
                                        minutes=30)  # Convert UTC to IST
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    for user_id, set_time in reminders.items():
        if current_time == set_time:
            if sent_status.get(user_id) == today:
                continue  # Already sent today

            try:
                await app.bot.send_message(
                    chat_id=user_id, text="🌙 It's time to sleep! Good night 😴")
                sent_status[user_id] = today  # Mark as sent
                save_json(SLEEP_SENT_FILE, sent_status)
            except Exception as e:
                print(f"Error sending sleep reminder to {user_id}: {e}")


async def send_workout_reminders(app):
    reminders = load_json(REMINDER_FILE)
    sent_status = load_json(WORKOUT_SENT_FILE)

    now = datetime.utcnow() + timedelta(hours=5,
                                        minutes=30)  # Convert UTC to IST
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    for user_id, set_time in reminders.items():
        if current_time == set_time:
            if sent_status.get(user_id) == today:
                continue  # Already sent today

            try:
                await app.bot.send_message(
                    chat_id=user_id,
                    text=
                    "🏋️ It's time for your daily workout! Tap /today to log today's workout."
                )
                sent_status[user_id] = today
                save_json(WORKOUT_SENT_FILE, sent_status)
            except Exception as e:
                print(f"Error sending workout reminder to {user_id}: {e}")


async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text(
            "❗ Usage: /setreminder HH:MM (24hr format)")
        return
    time = context.args[0]
    reminders = load_json(REMINDER_FILE)
    reminders[user_id] = time
    save_json(REMINDER_FILE, reminders)
    await update.message.reply_text(f"⏰ Reminder set for {time} daily!")

async def start_scheduler(app):
    scheduler = AsyncIOScheduler()

    # Direct coroutine jobs — no lambda, no create_task
    async def sleep_job():
        await send_sleep_reminders(app)

    async def workout_job():
        await send_workout_reminders(app)

    scheduler.add_job(sleep_job, trigger='interval', minutes=0.1)
    scheduler.add_job(workout_job, trigger='interval', minutes=0.1)

    scheduler.start()