from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from utils.json_store import load_json
from utils.constants import (
    PROGRESS_FILE, SLEEP_FILE, GOAL_FILE, STREAK_FILE, WORKOUT_FILE
)
from utils.gemini import ask_gemini
from utils.escape import escape_markdown
from utils.constants import COACH_HISTORY_FILE
from utils.json_store import save_json
from datetime import datetime
from prompts.coach_prompt import build_simple_coach_prompt

def get_last_n_days(n):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n)]


async def coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = " ".join(context.args)
    user_id = str(update.message.from_user.id)

    if not user_input:
        await update.message.reply_text(
            "🧠 Use like:\n`/coach I'm feeling lazy today`",
            parse_mode="Markdown"
        )
        return

    # Load all user data
    progress = load_json(PROGRESS_FILE)
    sleep = load_json(SLEEP_FILE)
    goals = load_json(GOAL_FILE)
    streaks = load_json(STREAK_FILE)
    workouts = load_json(WORKOUT_FILE)

    goal = goals.get(user_id, 21)
    selected_workouts = workouts.get(user_id, [])
    streak_info = streaks.get(user_id, {"streak": 0, "last_update": "N/A"})
    last_7_days = get_last_n_days(7)

    # Build 7-day summary
    summary_lines = []
    for day in reversed(last_7_days):
        workout_done = progress.get(user_id, {}).get(day, {})
        sleep_hours = sleep.get(user_id, {}).get(day, "N/A")
        summary_lines.append(f"{day} - 🏋️ {list(workout_done.keys()) or 'None'}, 😴 {sleep_hours} hrs")

        # Load recent coach chats for context
    coach_data = load_json(COACH_HISTORY_FILE)
    chat_history = coach_data.get(user_id, [])
    recent_chats = chat_history[-3:] if chat_history else []

    # Build Gemini prompt
    prompt = build_simple_coach_prompt(
    user_input=user_input,
    streak_info=streak_info,
    goal=goal,
    selected_workouts=selected_workouts,
    summary_lines=summary_lines,
    recent_chats=recent_chats
)



    reply = ask_gemini(prompt)
    safe_reply = escape_markdown(reply)

    await update.message.reply_text(
        f"*🗣️Coach:*\n{safe_reply}",
        parse_mode="MarkdownV2"
    )

        # Save coach chat data
    coach_data = load_json(COACH_HISTORY_FILE)

    if user_id not in coach_data:
        coach_data[user_id] = []

    coach_data[user_id].append({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "message": user_input,
        "reply": reply,
        "streak": streak_info['streak'],
        "workouts": selected_workouts,
    })

    save_json(COACH_HISTORY_FILE, coach_data)