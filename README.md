# 🧠 Discipline Tracker Bot [Telegram]

A smart Telegram bot to help you build habits, stay consistent, and reach your fitness & lifestyle goals — now powered with **AI coaching** 💪🧠

---

## 🚀 Features

### 🏋️ Habit & Workout Tracking
- `/setworkout` – Choose your daily workouts (e.g. pushups, squats)
- `/today` – Log today’s workouts with interactive buttons
- `/todaysprogress` – See what you’ve completed and what’s pending
- `/status` – View your current streak, last update, and goal

### 💤 Sleep Tracking
- `/sleeplog` – Log how many hours you slept last night
- `/sleepstatus` – View your 7-day average sleep

### ⏰ Daily Reminders
- `/setreminder` – Set workout reminder time
- `/setsleeptime` – Set sleep reminder time

### 🎯 Goal Setting & Progress
- `/setgoal` – Set your consistency goal in days
- `/mysettings` – View all your current setup (workouts, goal, reminders)

---

## 🤖 NEW! AI-Powered Coach

> Let the bot talk to you like a **personal buddy + trainer**

- `/coach I'm feeling lazy today`  
  → Get motivating, funny, or tough-love responses based on your streak, workouts & mood!

- Personalised replies based on:
  - Streak history
  - Sleep & workout data
  - Your recent conversations

---

## 📊 Analyze & 💡 Suggest

- `/analyze` – Get weekly/monthly summaries of your progress
- `/suggest` – Get smart workout/habit suggestions from AI based on your performance

---

## 💬 Feedback
Use `/feedback` to send your thoughts and help improve the bot! Every input matters.

---

## 📁 Project Structure

```
Mission21Bot/
│
├── main.py                  # 🚀 Entry point: starts the Telegram bot and routes all commands
├── keep_alive.py            # 🌐 Keeps bot alive on Replit or similar platforms
├── notify_users.py          # 📢 Sends update notifications to all users
├── requirements.txt         # 📦 Python package dependencies
├── .env                     # 🔐 Environment variables (e.g., bot token, API keys)
│
├── commands/                # 💬 Telegram command handlers
│   ├── coach.py             # ↪️ Handles AI Coach interactions
│   ├── workout.py           # 🏋️ Logs and tracks workouts
│   ├── sleep.py             # 💤 Tracks sleep routines
│   ├── goal.py              # 🎯 Goal setting and management
│   ├── reminders.py         # ⏰ Reminder system
│   ├── feedback.py          # 📩 Collects user feedback
│   ├── analyze.py           # 📊 Weekly/monthly user stats and progress
│   ├── suggest.py           # 💡 Suggests workouts/habits based on data
│   └── start.py             # 👋 Welcome/start command with onboarding info
│
├── utils/                   # 🔧 Utility modules
│   ├── json_store.py        # 📦 JSON read/write helpers
│   ├── constants.py         # 📘 Shared constants
│   ├── timezone.py          # 🕒 IST timestamp generator
│   ├── escape.py            # 🔒 Input sanitization
│   ├── gemini.py            # 🤖 Gemini AI interaction logic
│   └── waiting_state.py     # ⏳ Track user waiting states (like pending replies)
│
├── prompts/                 # 🧠 Prompt generators for Gemini AI
│   └── coach_prompt.py      # 🗣️ Builds personality-based prompt for AI Coach
│
├── data/                    # 🗃️ Persistent user data storage (JSON)
│   ├── workouts.json        # 🏋️ Workout logs per user
│   ├── streaks.json         # 🔥 User streaks and consistency
│   ├── coach_history.json   # 🧠 AI conversation memory
│   └── ...                  # 📁 Other per-user data files
```

---

## 🔧 Tech Stack

- **Python 3.10+**
- `python-telegram-bot` v20+
- **APScheduler** for scheduling reminders
- **Google Gemini API** – for AI coaching replies
- **Replit + UptimeRobot** – for free bot hosting

---

## 📦 Coming Soon
- 📊 Weekly / Monthly summary reports
- 🏆 Badges & leaderboard system
- 🤝 Group challenge support
- 🧠 More AI features: mood tracking, goal coaching, custom voice tones

---

## 🛡️ License

MIT License – Free to use, improve, and share.

---

### 👤 Made with consistency by [Your Name] 🙌  
> "Discipline is choosing what you want most over what you want now."
