from telegram import Update
from telegram.ext import ContextTypes
from utils.json_store import load_json, save_json
from utils.constants import (
    STREAK_FILE, USER_FILE, WORKOUT_FILE, PROGRESS_FILE, GOAL_FILE,
    REMINDER_FILE, WAITING_COUNT_FILE, SLEEP_FILE, SLEEP_SENT_FILE,
    WORKOUT_SENT_FILE, SLEEP_REMINDER_FILE
)
from datetime import datetime, timedelta

# Set goal command
async def set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /setgoal <number of days>")
        return
    days = int(context.args[0])
    goals = load_json(GOAL_FILE)
    goals[user_id] = days
    save_json(GOAL_FILE, goals)
    await update.message.reply_text(f"✅ Goal set to {days} days!")


async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    today = datetime.now().strftime('%Y-%m-%d')

    # Load files
    streaks = load_json(STREAK_FILE)
    goals = load_json(GOAL_FILE)
    progress = load_json(PROGRESS_FILE)
    sleep_data = load_json(SLEEP_FILE)
    workouts = load_json(WORKOUT_FILE)

    # Get goal and streak info
    goal = int(goals.get(user_id, 21))
    streak_info = streaks.get(user_id, {"streak": 0, "last_update": "N/A"})
    days = streak_info["streak"]
    last = streak_info["last_update"]

    # Workout progress
    user_workouts = workouts.get(user_id, [])
    workout_today = progress.get(user_id, {}).get(today, {})

    # 🧠 Check if all workouts completed today, and streak not updated
    if set(user_workouts) == set(workout_today.keys()) and last != today:
        days += 1
        last = today
        streaks[user_id] = {"streak": days, "last_update": today}
        save_json(STREAK_FILE, streaks)

    # Build workout message
    workout_msg = "✅ Workouts Today:\n"
    if workout_today:
        for w, count in workout_today.items():
            workout_msg += f"- {w}: {count}\n"
    else:
        workout_msg += "Not logged yet.\n"

    # Sleep info today
    sleep_today = sleep_data.get(user_id, {}).get(today)
    sleep_msg = f"😴 Sleep Today: {sleep_today} hrs\n" if sleep_today else "😴 Sleep Today: Not logged\n"

    # Visual progress bar
    progress_bar = "✅" * days + "❌" * (goal - days)

    # Final message
    msg = f"🧮 *Your Progress*\n\n"
    msg += f"🔥 Streak: *{days} days*\n"
    msg += f"📅 Last Update: {last}\n"
    msg += f"🎯 Goal: {goal} days\n"
    msg += f"📊 Progress: {progress_bar}\n\n"
    msg += workout_msg + "\n"
    msg += sleep_msg

    await update.message.reply_text(msg, parse_mode='Markdown')