from telegram import Update
from telegram.ext import ContextTypes
from utils.json_store import load_json, save_json
from utils.constants import (
    STREAK_FILE, USER_FILE, WORKOUT_FILE, PROGRESS_FILE, GOAL_FILE,
    REMINDER_FILE, WAITING_COUNT_FILE, SLEEP_FILE, SLEEP_SENT_FILE,
    WORKOUT_SENT_FILE, SLEEP_REMINDER_FILE
)
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.waiting_state import set_waiting_count, get_waiting_count, clear_waiting_count


async def set_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text(
            "❗ Usage: /setworkout Pushups, Squats, Plank")
        return
    workouts = load_json(WORKOUT_FILE)
    workouts[str(user.id)] = [w.strip() for w in text.split(",")]
    save_json(WORKOUT_FILE, workouts)
    await update.message.reply_text(f"✅ Workout list set:\n- " +
                                    "\n- ".join(workouts[str(user.id)]))
    

async def show_today_workouts(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    workouts = load_json(WORKOUT_FILE)
    progress = load_json(PROGRESS_FILE)
    workout_list = workouts.get(user_id, [])
    today = datetime.now().strftime('%Y-%m-%d')

    if not workout_list:
        await update.message.reply_text(
            "❗ You haven't set your workout list yet. Use /setworkout")
        return

    if str(user_id) not in progress:
        progress[str(user_id)] = {}
    if today not in progress[user_id]:
        progress[user_id][today] = {}
    save_json(PROGRESS_FILE, progress)

    remaining_tasks = [
        t for t in workout_list if t not in progress[user_id][today]
    ]
    if not remaining_tasks:
        await update.message.reply_text(
            "🎉 You’ve already completed all your workouts for today!")
        return

    keyboard = [[
        InlineKeyboardButton(f"✅ {t}", callback_data=f"{user_id}|{t}")
    ] for t in remaining_tasks]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("👊 Today's Workout:",
                                    reply_markup=reply_markup)


async def todays_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    workouts = load_json(WORKOUT_FILE)
    progress = load_json(PROGRESS_FILE)
    workout_list = workouts.get(user_id, [])
    today = datetime.now().strftime('%Y-%m-%d')

    if not workout_list:
        await update.message.reply_text(
            "❗ You haven't set your workout list yet. Use /setworkout")
        return

    if str(user_id) not in progress or today not in progress[user_id]:
        done = []
    else:
        done = progress[user_id][today]

    remaining = [t for t in workout_list if t not in done]

    msg = "📊 *Today's Progress:*\n\n"
    msg += "✅ Completed:\n" + ("\n".join(
        f"- {t}: {done[t]} reps" for t in done) if done else "None") + "\n\n"
    msg += "⏳ Remaining:\n" + ("\n".join(
        f"- {t}" for t in remaining) if remaining else "None")

    await update.message.reply_text(msg, parse_mode="Markdown")



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Respond safely and quickly
    try:
        await query.answer()
    except telegram.error.BadRequest as e:
        print("⚠️ Query too old or invalid:", e)
        return

    data = query.data.split("|")
    user_id, task = data[0], data[1]
    today = datetime.now().strftime('%Y-%m-%d')

    progress = load_json(PROGRESS_FILE)
    workouts = load_json(WORKOUT_FILE)
    goals = load_json(GOAL_FILE)
    streaks = load_json(STREAK_FILE)
    goal = int(goals.get(user_id, 21))

    if user_id not in progress:
        progress[user_id] = {}
    if today not in progress[user_id]:
        progress[user_id][today] = {}

    if task in progress[user_id][today]:
        await query.edit_message_text(text=f"✅ {task} already logged.")
        return

    set_waiting_count(user_id, task, today)
    await query.edit_message_text(text=f"✅ {task} done! How many did you do?")


async def handle_workout_count(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    waiting = get_waiting_count(user_id)
    if not waiting:
        return  # Not expecting input

    try:
        count = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❗ Please send a number only.")
        return

    task = waiting["task"]
    date = waiting["date"]

    progress = load_json(PROGRESS_FILE)
    if user_id not in progress:
        progress[user_id] = {}
    if date not in progress[user_id]:
        progress[user_id][date] = {}

    progress[user_id][date][task] = count
    save_json(PROGRESS_FILE, progress)
    clear_waiting_count(user_id)

    await update.message.reply_text(
        f"✅ Logged {count} for {task}. Keep going 💪")
    await show_today_workouts(update, context)


# Daily workout reminder with buttons
async def send_daily_reminder(app):
    users = load_json(USER_FILE)
    workouts = load_json(WORKOUT_FILE)
    progress = load_json(PROGRESS_FILE)
    today = datetime.now().strftime('%Y-%m-%d')

    for user_id in users:
        try:
            workout_list = workouts.get(str(user_id), [])
            if not workout_list:
                await app.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ No workout list set. Use /setworkout")
                continue

            keyboard = [[
                InlineKeyboardButton(f"✅ {task}",
                                     callback_data=f"{user_id}|{task}")
            ] for task in workout_list]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if str(user_id) not in progress:
                progress[str(user_id)] = {}
            progress[str(user_id)][today] = {}
            save_json(PROGRESS_FILE, progress)

            await app.bot.send_message(chat_id=user_id,
                                       text="👊 Today's Workout:",
                                       reply_markup=reply_markup)

        except Exception as e:
            print(f"Could not send reminder to {user_id}: {e}")
