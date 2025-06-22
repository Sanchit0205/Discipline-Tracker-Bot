from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime
import os
import json
import asyncio
from keep_alive import keep_alive
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Files
STREAK_FILE = "streaks.json"
USER_FILE = "users.json"
WORKOUT_FILE = "workouts.json"
PROGRESS_FILE = "progress.json"
GOAL_FILE = "goals.json"
REMINDER_FILE = "reminders.json"


# Load & Save functions
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            else:
                return {}
    return {}


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    users = load_json(USER_FILE)
    if user.id not in users:
        users.append(user.id)
        save_json(USER_FILE, users)
    await update.message.reply_text(
        "🚀 Welcome to *Mission 21 Days Tracker*!\n\n✅ /setworkout Pushups, Squats\n✅ /setgoal 21\n✅ /setreminder 06:30\n📊 /status to check streak.",
        parse_mode='Markdown')


# Set workout command
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


# Set reminder command
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


# Show current settings
async def my_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    workouts = load_json(WORKOUT_FILE)
    goals = load_json(GOAL_FILE)
    reminders = load_json(REMINDER_FILE)

    workout_list = workouts.get(user_id, [])
    goal = goals.get(user_id, "21")
    reminder = reminders.get(user_id, "06:00")

    msg = f"📝 *Your Settings:*\n\n"
    msg += f"🏋️ Workout List:\n- " + "\n- ".join(
        workout_list
    ) + "\n\n" if workout_list else "🏋️ Workout List: Not set\n\n"
    msg += f"🎯 Goal: {goal} days\n"
    msg += f"⏰ Reminder: {reminder}"

    await update.message.reply_text(msg, parse_mode='Markdown')


# Status command
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    streaks = load_json(STREAK_FILE)
    goals = load_json(GOAL_FILE)
    goal = goals.get(user_id, 21)

    if user_id in streaks:
        days = streaks[user_id]["streak"]
        last = streaks[user_id]["last_update"]
        progress = "✅" * days + "❌" * (int(goal) - days)
        await update.message.reply_text(
            f"🧮 Your current streak: *{days} days*\n📅 Last update: {last}\n🎯 Goal: {goal} days\n📊 Progress: {progress}",
            parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❗ No update found — start logging your workout!")


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
            progress[str(user_id)][today] = []
            save_json(PROGRESS_FILE, progress)

            await app.bot.send_message(chat_id=user_id,
                                       text="👊 Today's Workout:",
                                       reply_markup=reply_markup)

        except Exception as e:
            print(f"Could not send reminder to {user_id}: {e}")


# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    user_id, task = data[0], data[1]
    today = datetime.now().strftime('%Y-%m-%d')
    progress = load_json(PROGRESS_FILE)
    workouts = load_json(WORKOUT_FILE)
    streaks = load_json(STREAK_FILE)
    goals = load_json(GOAL_FILE)
    goal = int(goals.get(user_id, 21))

    if task not in progress[user_id][today]:
        progress[user_id][today].append(task)
        save_json(PROGRESS_FILE, progress)

    remaining_tasks = [
        t for t in workouts.get(user_id, [])
        if t not in progress[user_id][today]
    ]

    if remaining_tasks:
        keyboard = [[
            InlineKeyboardButton(f"✅ {t}", callback_data=f"{user_id}|{t}")
        ] for t in remaining_tasks]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"✅ {task} done! Keep going 💪",
                                      reply_markup=reply_markup)

    else:
        if user_id not in streaks:
            streaks[user_id] = {"streak": 1, "last_update": today}
        else:
            if streaks[user_id]["last_update"] != today:
                streaks[user_id]["streak"] += 1
                streaks[user_id]["last_update"] = today
        save_json(STREAK_FILE, streaks)

        await query.edit_message_text(
            text=
            f"🔥 All workouts done for today!\nStreak: {streaks[user_id]['streak']} ✅ / {goal}"
        )


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
        progress[user_id][today] = []
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
        f"- {t}" for t in done) if done else "None") + "\n\n"
    msg += "⏳ Remaining:\n" + ("\n".join(
        f"- {t}" for t in remaining) if remaining else "None")

    await update.message.reply_text(msg, parse_mode="Markdown")

async def show_command_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/setreminder", "/setworkout"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("📝 Pick a command (it won't auto-send):", reply_markup=reply_markup)


# Main run
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setworkout", set_workout))
    app.add_handler(CommandHandler("setgoal", set_goal))
    app.add_handler(CommandHandler("setreminder", set_reminder))
    app.add_handler(CommandHandler("mysettings", my_settings))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("today", show_today_workouts))
    app.add_handler(CommandHandler("todaysprogress", todays_progress))
    app.add_handler(CommandHandler("menu", show_command_keyboard))

    app.run_polling()


if __name__ == '__main__':
    keep_alive()
    main()
