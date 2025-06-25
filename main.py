from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters,ContextTypes
from keep_alive import keep_alive
import asyncio, nest_asyncio
import asyncio
from commands.start import start, my_settings
from commands.workout import set_workout, show_today_workouts, todays_progress, button_handler, handle_workout_count
from commands.goal import set_goal, check_status
from commands.sleep import set_sleep_time, log_sleep, sleep_status
from commands.reminders import set_reminder, start_scheduler
from dotenv import load_dotenv
import os
from commands.coach import coach
from commands.analyze import analyze
from commands.suggest import suggest
from commands.feedback import feedback
from utils.waiting_state import is_in_coach_mode
from telegram import Update


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not found. Check your .env file and variable name.")

async def smart_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip().lower()

    if text.startswith("/coach") or is_in_coach_mode(user_id):
        await coach(update, context)
    else:
        await handle_workout_count(update, context)


# Start bot
keep_alive()
nest_asyncio.apply()

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setworkout", set_workout))
    app.add_handler(CommandHandler("setgoal", set_goal))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CommandHandler("today", show_today_workouts))
    app.add_handler(CommandHandler("todaysprogress", todays_progress))
    app.add_handler(CommandHandler("setreminder", set_reminder))
    app.add_handler(CommandHandler("setsleeptime", set_sleep_time))
    app.add_handler(CommandHandler("sleeplog", log_sleep))
    app.add_handler(CommandHandler("sleepstatus", sleep_status))
    app.add_handler(CommandHandler("mysettings", my_settings))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_router))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("suggest", suggest))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(CommandHandler("coach", coach))       # ✅ Add this
    app.add_handler(CommandHandler("exitcoach", coach))   # ✅ Add this

    


    await start_scheduler(app)
    await app.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Fallback for "event loop is already running"
        if "already running" in str(e):
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
