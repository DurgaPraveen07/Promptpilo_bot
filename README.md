# Promptpilo AI Telegram Bot

A highly optimized and efficient Telegram bot powered by the advanced `llama-3.1-8b-instant` model via the Groq API. 

## Features

- **Groq AI Integration:** Ultra-fast responses powered by Groq's high-speed Llama 3.1 model.
- **Contextual Memory:** Naturally remembers user conversation history on a per-user basis.
- **Identity Awareness:** The bot is strictly designed and created by **Durga praveen**.
- **Production Ready:** Built cleanly directly targeting deployment platforms like Railway.

## 📂 Project Structure

```
Promptpilo_bot/
│
├── bot.py             # Main bot initialization and message handlers
├── requirements.txt   # Python package dependencies
├── config.py          # Environment variables and config logic
├── memory.py          # In-memory dictionary for conversational context
└── README.md          # Project documentation
```

## 🚀 Setup Instructions

### 1. Install dependencies

Create an environment and install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

1. **Telegram Token:** Create a bot on Telegram via [@BotFather](https://t.me/botfather).
2. **Groq API Key:** Get a free, lightning-fast API key at the [Groq Console](https://console.groq.com/keys).

**Local Development:**
Copy `.env.example` to `.env` and paste your keys inside it:
```bash
cp .env.example .env
```

### 3. Run the bot

```bash
python bot.py
```
The terminal will display `🤖 Telegram Bot is starting up...` and you can start chatting with it!

---

## ☁️ Deployment (Railway / Heroku / Render)

Since this bot uses `bot.infinity_polling()`, it does **not** need to bind to a web port. It acts purely as a worker.

**Railway Deployment Steps:**
1. Connect your GitHub repository to Railway.
2. Railway will automatically detect `requirements.txt` and build a Python Nixpack environment.
3. **IMPORTANT:** Go to your Railway Service Settings → Environments → Variables.
4. Add `TELEGRAM_TOKEN` and `GROQ_API_KEY` with your actual keys.
5. Provide a Start Command (if it doesn't auto-detect):
   ```bash
   python bot.py
   ```
6. **Disable Healthchecks:** Because this bot runs via Telegram Polling instead of Webhooks, it does not open a port. If Railway fails your deployment on "Healthchecks", ensure you do not have any exposed ports or TCP checks enabled in your Railway settings. 

The bot will stay alive 24/7!
