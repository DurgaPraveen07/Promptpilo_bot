import telebot
from groq import Groq
from config import TELEGRAM_TOKEN, GROQ_API_KEY
from memory import get_user_memory, add_message_to_memory, reset_user_memory
import os

# 1. Initialize the Telegram bot
# Note: Handle cases where the token might be empty
if not TELEGRAM_TOKEN:
    print("❌ CRITICAL ERROR: TELEGRAM_TOKEN is missing! The bot cannot start.")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 2. Connect to the Groq client
# We initialize it inside a try-block to catch early key errors
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not initialize Groq client: {e}")
    groq_client = None

# Using Llama 3.1 - 8b which is extremely fast and reliable for free/basic tiers
MODEL_NAME = "llama-3.1-8b-instant"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command."""
    user_id = message.from_user.id
    reset_user_memory(user_id)
    
    welcome_text = (
        "🤖 *Welcome to the Promptpilo AI Bot!*\n\n"
        "I am powered by Llama 3.1 and ready to answer any question you have.\n\n"
        "*Available Commands:*\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/reset - Clear your conversation memory\n\n"
        "Go ahead! Ask me anything."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    """Handles the /help command."""
    help_text = (
        "*Available Commands:*\n"
        "/start - Welcome message and features\n"
        "/help - Show available commands\n"
        "/reset - Clear conversation memory"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_memory(message):
    """Handles the /reset command."""
    user_id = message.from_user.id
    reset_user_memory(user_id)
    bot.reply_to(message, "🧹 Your conversation memory has been cleared. Let's start fresh!")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_messages(message):
    """
    Handles all incoming text messages effectively.
    Sends user text to Groq and manages conversation history.
    """
    user_id = message.from_user.id
    user_text = message.text
    
    # 1. Check if Groq client is initialized
    if not groq_client or not GROQ_API_KEY:
        bot.reply_to(message, "⚠️ API Key Error: Please make sure you have added your `GROQ_API_KEY` to the `.env` file correctly.")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # 2. Add user's message to memory
        add_message_to_memory(user_id, "user", user_text)
        
        # 3. Retrieve history for context
        messages_history = get_user_memory(user_id)
        
        # 4. Request completion from Groq AI (Llama 3.1 8b)
        chat_completion = groq_client.chat.completions.create(
            messages=messages_history,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=1024,
            top_p=1
        )
        
        # 5. Extract and Validate AI response
        ai_response = chat_completion.choices[0].message.content
        
        if not ai_response:
            ai_response = "I'm sorry, I received an empty response from the AI. Could you try rephrasing your question?"
        
        # 6. Add AI's response to memory
        add_message_to_memory(user_id, "assistant", ai_response)
        
        # 7. Send final response back to Telegram
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        # Detailed logging for the developer/user to see in the terminal
        error_msg = str(e)
        print(f"❌ Error during AI processing: {error_msg}")
        
        if "rate_limit_exceeded" in error_msg.lower():
            bot.reply_to(message, "⚠️ I'm a bit overwhelmed with requests! Please wait a moment and try again.")
        elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            bot.reply_to(message, "⚠️ Authentication Error: Your Groq API Key appears to be invalid. Please double-check it in your `.env` file.")
        else:
            bot.reply_to(message, "⚠️ I encountered an error while thinking. This usually happens if the API key is missing or invalid. Please check your `.env` file configuration.")

if __name__ == "__main__":
    print("🤖 Promptpilo Bot is starting up...")
    print(f"Using Model: {MODEL_NAME}")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"❌ Polling Error: {e}")
