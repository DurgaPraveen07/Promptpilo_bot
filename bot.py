import telebot
from groq import Groq
from config import TELEGRAM_TOKEN, GROQ_API_KEY
from memory import get_user_memory, add_message_to_memory, reset_user_memory

# ===============================
# 1. Validate Tokens
# ===============================

if not TELEGRAM_TOKEN:
    print("❌ CRITICAL ERROR: TELEGRAM_TOKEN is missing.")
    exit(1)

if not GROQ_API_KEY:
    print("❌ CRITICAL ERROR: GROQ_API_KEY is missing.")
    exit(1)

# ===============================
# 2. Initialize Services
# ===============================

bot = telebot.TeleBot(TELEGRAM_TOKEN)

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    exit(1)

# Correct Groq model
MODEL_NAME = "llama3-70b-8192"

# ===============================
# 3. Commands
# ===============================

@bot.message_handler(commands=['start'])
def send_welcome(message):

    user_id = message.from_user.id
    reset_user_memory(user_id)

    text = (
        "🤖 *Welcome to Promptpilo AI Bot*\n\n"
        "I am powered by Llama 3 (70B).\n\n"
        "*Commands*\n"
        "/start - restart bot\n"
        "/help - show commands\n"
        "/reset - clear memory\n\n"
        "Ask me anything!"
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['help'])
def help_command(message):

    text = (
        "*Available Commands*\n\n"
        "/start - restart bot\n"
        "/help - show commands\n"
        "/reset - clear conversation memory"
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['reset'])
def reset_command(message):

    user_id = message.from_user.id
    reset_user_memory(user_id)

    bot.reply_to(message, "🧹 Memory cleared.")


# ===============================
# 4. AI Chat Handler
# ===============================

@bot.message_handler(func=lambda message: True, content_types=['text'])
def chat_handler(message):

    user_id = message.from_user.id
    user_text = message.text

    bot.send_chat_action(message.chat.id, "typing")

    try:

        # Save user message
        add_message_to_memory(user_id, "user", user_text)

        # Get conversation history
        messages_history = get_user_memory(user_id)

        # Request Groq AI
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages_history,
            temperature=0.7,
            max_tokens=1024
        )

        ai_text = response.choices[0].message.content

        if not ai_text:
            ai_text = "I couldn't generate a response. Please try again."

        # Save AI response
        add_message_to_memory(user_id, "assistant", ai_text)

        # Send reply
        bot.reply_to(message, ai_text)

    except Exception as e:

        print("❌ AI Error:", e)

        error_msg = str(e).lower()

        if "rate_limit" in error_msg:
            bot.reply_to(message, "⚠️ Too many requests. Please wait a moment.")

        elif "authentication" in error_msg or "api_key" in error_msg:
            bot.reply_to(message, "⚠️ Invalid Groq API key.")

        else:
            bot.reply_to(message, "⚠️ AI service error. Please try again later.")


# ===============================
# 5. Start Bot
# ===============================

if __name__ == "__main__":

    print("🚀 Promptpilo Bot starting...")
    print("Model:", MODEL_NAME)

    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)

    except Exception as e:
        print("❌ Polling error:", e)