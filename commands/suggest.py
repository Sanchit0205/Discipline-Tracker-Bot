from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from utils.json_store import load_json
from utils.constants import (
    PROGRESS_FILE, SLEEP_FILE, GOAL_FILE, STREAK_FILE, WORKOUT_FILE
)
from utils.gemini import ask_gemini
from utils.escape import escape_markdown



def get_last_n_days(n):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n)]


async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Load user data
    progress = load_json(PROGRESS_FILE)
    sleep = load_json(SLEEP_FILE)
    goals = load_json(GOAL_FILE)
    streaks = load_json(STREAK_FILE)
    workouts = load_json(WORKOUT_FILE)

    selected_workouts = workouts.get(user_id, [])
    streak_info = streaks.get(user_id, {"streak": 0, "last_update": "N/A"})
    goal = goals.get(user_id, 21)

    last_7 = get_last_n_days(7)
    summary_lines = []

    for day in reversed(last_7):
        w_done = progress.get(user_id, {}).get(day, {})
        sleep_hours = sleep.get(user_id, {}).get(day, "N/A")
        summary_lines.append(
            f"{day} - 🏋️ {list(w_done.keys()) or 'None'}, 😴 {sleep_hours} hrs"
        )

    prompt = (
    f"You're a friendly fitness and habit coach bot.\n\n"
    f"User's current streak: {streak_info['streak']} days\n"
    f"Goal: {goal} days\n"
    f"Last update: {streak_info['last_update']}\n"
    f"User's selected workouts: {selected_workouts or 'None'}\n\n"
    f"Here’s a summary of the last 7 days:\n"
    f"{chr(10).join(summary_lines)}\n\n"
    "Now suggest what the user should do *today* in a short, attractive way.\n\n"
    "✦ Keep it under 6 lines\n"
    "✦ Use emojis if helpful\n"
    "✦ Be clear, motivating, and casual — like a personal buddy giving a tip\n"
    "✦ Use bullet points if possible\n\n"
    "Example:\n"
    "• 🔁 Missed a day? Try a 10-min walk to restart momentum!\n"
    "• 💤 Avg sleep low — aim for 6.5+ hrs tonight.\n"
    "• 💪 Challenge: Try 15 pushups & 10 squats today!"
)


    reply = ask_gemini(prompt)
    safe_reply = escape_markdown(reply)


    await update.message.reply_text(
        f"🧭 *Next Step Suggestion:*\n{safe_reply}",
        parse_mode="MarkdownV2"
)

