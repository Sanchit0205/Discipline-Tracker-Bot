from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from utils.json_store import load_json, save_json
from utils.constants import (
    PROGRESS_FILE, SLEEP_FILE, GOAL_FILE, STREAK_FILE, WORKOUT_FILE, COACH_HISTORY_FILE
)
from utils.gemini import ask_gemini
from utils.escape import escape_markdown
from prompts.coach_prompt import build_simple_coach_prompt
from utils.waiting_state import set_coach_mode, is_in_coach_mode

def get_last_n_days(n):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n)]

async def coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    if text.lower().startswith("/exitcoach"):
        set_coach_mode(user_id, False)
        await update.message.reply_text("👋Coach mode exited. See you next time!")
        return

    if text.lower().startswith("/coach"):
        set_coach_mode(user_id, True)
        message_text = text[6:].strip()

        await update.message.reply_text(
            "🧠Coach mode activated. Let’s go!\nType anything, I’m listening..."
        )

        if not message_text:
            return  # Wait for next message

        context.args = message_text.split()

    elif is_in_coach_mode(user_id):
        context.args = text.split()
    else:
        return

    # Load user data
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

    # Recent coach history
    coach_data = load_json(COACH_HISTORY_FILE)
    chat_history = coach_data.get(user_id, [])
    recent_chats = chat_history[-3:] if chat_history else []

    # Build prompt
    prompt = build_simple_coach_prompt(
        user_input=" ".join(context.args),
        streak_info=streak_info,
        goal=goal,
        selected_workouts=selected_workouts,
        summary_lines=summary_lines,
        recent_chats=recent_chats
    )

    # Ask Gemini
    reply = ask_gemini(prompt)
    safe_reply = escape_markdown(reply)

    await update.message.reply_text(
        f"*🗣️ Coach:*\n{safe_reply}",
        parse_mode="MarkdownV2"
    )

    # Save history
    coach_data[user_id] = coach_data.get(user_id, [])
    coach_data[user_id].append({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "message": " ".join(context.args),
        "reply": reply,
        "streak": streak_info['streak'],
        "workouts": selected_workouts,
    })

    save_json(COACH_HISTORY_FILE, coach_data)
