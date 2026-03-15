import telebot
from groq import Groq
from config import TELEGRAM_TOKEN, GROQ_API_KEY
from memory import get_user_memory, add_message_to_memory, reset_user_memory
import urllib.parse

# 1. Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 2. Connect to the Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Define the Groq model
MODEL_NAME = "llama3-70b-8192"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command."""
    user_id = message.from_user.id
    reset_user_memory(user_id)
    
    welcome_text = (
        "🤖 *Welcome to the Promptpilo AI Bot!*\n\n"
        "I am connected to an advanced AI model and ready to help you.\n\n"
        "*Available Commands:*\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/reset - Clear your conversation memory\n\n"
        "How can I assist you today?"
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
    Handles all incoming text messages.
    Sends the user message to the Groq API with conversation context.
    """
    user_id = message.from_user.id
    user_text = message.text
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # 1. Add user's message to memory
        add_message_to_memory(user_id, "user", user_text)
        
        # 2. Retrieve history for context
        messages_history = get_user_memory(user_id)
        
        # 3. Request completion from Groq AI
        chat_completion = groq_client.chat.completions.create(
            messages=messages_history,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=1024
        )
        
        # 4. Extract AI response
        ai_response = chat_completion.choices[0].message.content
        
        # 5. Add AI's response to memory
        add_message_to_memory(user_id, "assistant", ai_response)
        
        # 6. Send response
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        print(f"Error communicating with Groq or Telegram: {e}")
        bot.reply_to(message, "⚠️ Sorry, I encountered an error while processing your request. Please try again later.")

# Railway Nixpack builders just need a script that runs infinitely.
# Since this is purely a Telegram bot using polling, it does not need a web port.
# Make sure your Railway deployment settings have NO PORT and NO TCP Healthchecks enforced.
if __name__ == "__main__":
    print("🤖 Telegram Bot is starting up...")
    bot.infinity_polling()
