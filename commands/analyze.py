from telegram import Update
from telegram.ext import ContextTypes
from utils.constants import PROGRESS_FILE, SLEEP_FILE, GOAL_FILE
from utils.json_store import load_json
from utils.gemini import ask_gemini
from datetime import datetime, timedelta
from utils.constants import STREAK_FILE, WORKOUT_FILE


def get_last_n_days(n):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n)]

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    progress = load_json(PROGRESS_FILE)
    sleep = load_json(SLEEP_FILE)
    goals = load_json(GOAL_FILE)
    streaks = load_json(STREAK_FILE)
    workouts = load_json(WORKOUT_FILE)

    selected_workouts = workouts.get(user_id, [])
    streak_info = streaks.get(user_id, {"streak": 0, "last_update": "N/A"})


    last_7 = get_last_n_days(7)
    summary = []

    for day in reversed(last_7):
        workouts = progress.get(user_id, {}).get(day, {})
        sleep_hours = sleep.get(user_id, {}).get(day, "N/A")
        summary.append(f"{day} - 🏋️ {list(workouts.keys()) or 'None'}, 😴 {sleep_hours} hrs")

    goal = goals.get(user_id, 21)

    prompt = (
    f"You're a smart, friendly habit coach AI.\n\n"
    f"The user is doing a {goal}-day discipline challenge.\n"
    f"Current streak: {streak_info['streak']} days\n"
    f"Last update: {streak_info['last_update']}\n"
    f"User's selected workouts: {selected_workouts or 'None'}\n\n"
    f"Here’s their past 7 days:\n"
    f"{chr(10).join(summary)}\n\n"
    "👉 Analyze and give advice:\n"
    "• Mention any good or missing habits\n"
    "• Suggest small improvements (e.g., more sleep, missed workouts)\n"
    "• Motivate them to stay on track\n"
    "✦ Keep it short — 6-7 friendly sentences"
)


    reply = ask_gemini(prompt)
    await update.message.reply_text(f"📊 *AI Habit Review:*\n{reply}", parse_mode="Markdown")
