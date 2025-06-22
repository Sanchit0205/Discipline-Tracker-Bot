
# 🏋️‍♂️ Discipline Tracker Bot

A simple, personal Telegram bot built using `python-telegram-bot` to track your daily workout streaks for 21 days (or a custom goal)!

✅ Set your workouts  
✅ Set a daily reminder time  
✅ Track your streak day by day  
✅ Mark completed workouts using inline buttons  
✅ View your progress any time  

---

## 📦 Features

- `/start` — Start the bot and register yourself
- `/setworkout` — Set your workout list (comma-separated)
- `/setgoal` — Set your target streak goal (in days)
- `/setreminder` — Set a daily reminder time (24hr format)
- `/mysettings` — View your current workout list, goal, and reminder time
- `/status` — Check your current streak and progress
- `/today` — View today’s workout tasks with inline buttons to mark as done
- `/todaysprogress` — See completed and remaining tasks for today
- `/menu` — Quick reply keyboard for `/setworkout` and `/setreminder`

---

## 📂 Project Structure

```
Mission21Bot/
├── bot.py                # Main bot code
├── keep_alive.py         # Keep-alive server for Replit (if needed)
├── .env                  # Your Telegram bot token (not committed)
├── .gitignore
├── requirements.txt
├── streaks.json          # User streak data
├── users.json            # User ID list
├── workouts.json         # User workouts
├── progress.json         # Daily progress log
├── goals.json            # User goal targets
├── reminders.json        # User reminder times
└── README.md
```

---

## 🔒 Environment Variables

Create a `.env` file in your project root with:

```
BOT_TOKEN=your-telegram-bot-token-here
```

**Note:** Never commit this file to GitHub.  
It's already listed in `.gitignore`.

---

## 📦 Install Dependencies

Install all required Python packages with:

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the Bot

To run locally:

```bash
python bot.py
```

To deploy on **Replit** with `keep_alive` for 24/7 uptime, make sure `keep_alive.py` is properly configured.

---

## 📌 Notes

- This bot uses **JSON files for data storage** (streaks, users, workouts, progress, etc.)
- You can deploy it on **Replit + UptimeRobot** for continuous uptime.
- Or test and run locally using **VS Code / Terminal**.

---

## 📖 License

MIT — Free to use, learn, and improve.

---

## ✨ Author

Made with ❤️ by **Sanchit Chavan**
