from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime
import os
import json
import asyncio
from keep_alive import keep_alive
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Files
STREAK_FILE = "streaks.json"
USER_FILE = "users.json"
WORKOUT_FILE = "workouts.json"
PROGRESS_FILE = "progress.json"
GOAL_FILE = "goals.json"
REMINDER_FILE = "reminders.json"
WAITING_COUNT_FILE = "waiting_count.json"
SLEEP_FILE = "sleep.json"
SLEEP_SENT_FILE = "sleep_sent.json"
WORKOUT_SENT_FILE = "workout_sent.json"
SLEEP_REMINDER_FILE = "sleep_reminders.json"




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


def set_waiting_count(user_id, task, date):
    waiting = load_json(WAITING_COUNT_FILE)
    waiting[str(user_id)] = {"task": task, "date": date}
    save_json(WAITING_COUNT_FILE, waiting)

def get_waiting_count(user_id):
    waiting = load_json(WAITING_COUNT_FILE)
    return waiting.get(str(user_id))

def clear_waiting_count(user_id):
    waiting = load_json(WAITING_COUNT_FILE)
    if str(user_id) in waiting:
        del waiting[str(user_id)]
        save_json(WAITING_COUNT_FILE, waiting)

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
    reminders = load_json(REMINDER_FILE)  # workout time
    sleep_times = load_json(SLEEP_REMINDER_FILE)   # sleep time

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



# Status command
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    today = datetime.now().strftime('%Y-%m-%d')

    # Load files
    streaks = load_json(STREAK_FILE)
    goals = load_json(GOAL_FILE)
    progress = load_json(PROGRESS_FILE)
    sleep_data = load_json(SLEEP_FILE)

    # Get goal and streak info
    goal = int(goals.get(user_id, 21))
    streak_info = streaks.get(user_id, {"streak": 0, "last_update": "N/A"})
    days = streak_info["streak"]
    last = streak_info["last_update"]

    # Workout progress (count today)
    workout_today = progress.get(user_id, {}).get(today, {})
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


# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    user_id, task = data[0], data[1]
    today = datetime.now().strftime('%Y-%m-%d')

    progress = load_json(PROGRESS_FILE)
    workouts = load_json(WORKOUT_FILE)
    goals = load_json(GOAL_FILE)
    streaks = load_json(STREAK_FILE)
    goal = int(goals.get(user_id, 21))

    # Initialize user progress if not already
    if user_id not in progress:
        progress[user_id] = {}
    if today not in progress[user_id]:
        progress[user_id][today] = {}

    # If task already logged, ignore
    if task in progress[user_id][today]:
        await query.edit_message_text(text=f"✅ {task} already logged.")
        return

    # Set waiting state for count
    set_waiting_count(user_id, task, today)

    # Ask user to input count
    await query.edit_message_text(text=f"✅ {task} done! How many did you do?")

async def handle_workout_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await update.message.reply_text(f"✅ Logged {count} for {task}. Keep going 💪")


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

async def set_sleep_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text("❗ Usage: /setsleeptime HH:MM (24hr format)")
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
        await update.message.reply_text("❗ Please enter a valid number of hours.")
        return
    today = datetime.now().strftime('%Y-%m-%d')
    sleep_data = load_json(SLEEP_FILE)
    if user_id not in sleep_data:
        sleep_data[user_id] = {}
    sleep_data[user_id][today] = hours
    save_json(SLEEP_FILE, sleep_data)
    await update.message.reply_text(f"✅ Logged {hours} hours of sleep.")

from datetime import timedelta

async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    sleep_data = load_json(SLEEP_FILE)
    if user_id not in sleep_data:
        await update.message.reply_text("❗ No sleep data found. Use /sleeplog to log.")
        return

    today = datetime.now()
    logs = []
    for i in range(7):
        day = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        if day in sleep_data[user_id]:
            logs.append(sleep_data[user_id][day])

    if not logs:
        await update.message.reply_text("❗ No sleep entries in the past 7 days.")
        return

    avg = sum(logs) / len(logs)
    await update.message.reply_text(f"🛌 Avg sleep (last 7 days): {avg:.1f} hrs")

async def send_sleep_reminders(app):
    reminders = load_json("sleep_reminders.json")
    sent_status = load_json(SLEEP_SENT_FILE)

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    for user_id, set_time in reminders.items():
        # Check if it's the right time AND not already sent today
        if current_time == set_time:
            if sent_status.get(user_id) == today:
                continue  # Already sent today

            try:
                await app.bot.send_message(chat_id=user_id, text="🌙 It's time to sleep! Good night 😴")
                sent_status[user_id] = today  # Mark as sent
                save_json(SLEEP_SENT_FILE, sent_status)
            except Exception as e:
                print(f"Error sending sleep reminder to {user_id}: {e}")


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



async def send_workout_reminders(app):
    reminders = load_json(REMINDER_FILE)
    sent_status = load_json(WORKOUT_SENT_FILE)

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    for user_id, set_time in reminders.items():
        if current_time == set_time:
            if sent_status.get(user_id) == today:
                continue  # Already sent today

            try:
                # Send workout reminder
                await app.bot.send_message(
                    chat_id=user_id,
                    text="🏋️ It's time for your daily workout! Tap /today to log today's workout."
                )
                sent_status[user_id] = today
                save_json(WORKOUT_SENT_FILE, sent_status)
            except Exception as e:
                print(f"Error sending workout reminder to {user_id}: {e}")


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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_workout_count))
    app.add_handler(CommandHandler("setsleeptime", set_sleep_time))
    app.add_handler(CommandHandler("sleeplog", log_sleep))
    app.add_handler(CommandHandler("sleepstatus", sleep_status))

    app.post_init = start_scheduler

    app.run_polling()


if __name__ == '__main__':
    keep_alive()
    main()
