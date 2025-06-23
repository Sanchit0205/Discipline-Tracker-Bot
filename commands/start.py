from telegram import Update
from telegram.ext import ContextTypes
from utils.json_store import load_json, save_json
from utils.constants import (
    STREAK_FILE, USER_FILE, WORKOUT_FILE, PROGRESS_FILE, GOAL_FILE,
    REMINDER_FILE, WAITING_COUNT_FILE, SLEEP_FILE, SLEEP_SENT_FILE,
    WORKOUT_SENT_FILE, SLEEP_REMINDER_FILE
)
from datetime import datetime, timedelta


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    users = load_json(USER_FILE)
    if user.id not in users:
        users.append(user.id)
        save_json(USER_FILE, users)

    await update.message.reply_text(
        f"👋 Hello *{user.first_name}*, welcome to *Discipline Tracker*! 🌟\n\n"
        "This bot helps you build habits and stay consistent.\n\n"
        "💪 *Workout Setup*\n"
        "• [/setworkout] — Tell me which exercises you'll do daily (e.g. pushups, squats)\n"
        "• [/today] — Start today's workout and track each one\n"
        "• [/todaysprogress]— Check which exercises you’ve finished\n\n"
        "🎯 *Goals & Progress*\n"
        "• [/setgoal] — Set how many days you want to stay consistent (e.g. 21)\n"
        "• [/status] — View your current streak and progress\n"
        "• [/mysettings] — Check your current workout, goal, and reminder times\n\n"
        "⏰ *Daily Reminders*\n"
        "• [/setreminder] — Set a time to get a daily workout reminder\n"
        "• [/setsleeptime] — Set a sleep reminder time\n\n"
        "😴 *Sleep Tracking*\n"
        "• [/sleeplog] — Log how many hours you slept today\n"
        "• [/sleepstatus] — See your average sleep over the past week\n\n"
        "📌 *Tip:* Use this bot every day for a few minutes. Tap the commands above or type them to stay on track 💯",
        parse_mode='Markdown',
        disable_web_page_preview=True)
    


# Show current settings
async def my_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    workouts = load_json(WORKOUT_FILE)
    goals = load_json(GOAL_FILE)
    reminders = load_json(REMINDER_FILE)  # workout time
    sleep_times = load_json(SLEEP_REMINDER_FILE)  # sleep time

    workout_list = workouts.get(user_id, [])
    goal = goals.get(user_id, "21")
    reminder = reminders.get(user_id, "06:00")
    sleep_time = sleep_times.get(user_id, "Not set")

    msg = f"📝 *Your Settings:*\n\n"

    # Workout list
    if workout_list:
        msg += f"🏋️ Workout List:\n- " + "\n- ".join(workout_list) + "\n\n"
    else:
        msg += "🏋️ Workout List: Not set\n\n"

    # Goal
    msg += f"🎯 Goal: {goal} days\n"

    # Workout reminder
    msg += f"⏰ Workout Reminder: {reminder}\n"

    # Sleep reminder
    msg += f"🌙 Sleep Reminder: {sleep_time}"

    await update.message.reply_text(msg, parse_mode='Markdown')