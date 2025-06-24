# commands/feedback.py

from telegram import Update
from telegram.ext import ContextTypes
from utils.constants import FEEDBACK_FILE
from utils.json_store import load_json, save_json
from datetime import datetime
from utils.timezone import get_ist_timestamp

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message = " ".join(context.args)

    if not message:
        await update.message.reply_text(
            "📝 Please send your feedback like:\n`/feedback The new coach is amazing!`",
            parse_mode="Markdown"
        )
        return

    # Load existing feedback
    feedback_data = load_json(FEEDBACK_FILE)

    if user_id not in feedback_data:
        feedback_data[user_id] = []

    feedback_data[user_id].append({
        "timestamp": get_ist_timestamp(),
        "message": message
    })

    save_json(FEEDBACK_FILE, feedback_data)

    await update.message.reply_text("✅ Thanks for your feedback! I’ve noted it down.")
