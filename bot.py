import telebot
from config import TELEGRAM_TOKEN
from memory import get_user_memory, add_message_to_memory, reset_user_memory
from rag import query_rag

# Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command."""
    user_id = message.from_user.id
    reset_user_memory(user_id)
    
    welcome_text = (
        "🤖 *Welcome to our AI Assistant!*\n\n"
        "I am connected to our business knowledge base and ready to help you.\n\n"
        "*Available Commands:*\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/image <prompt> - Generate an AI image\n"
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
        "/image <prompt> - Generate an AI image\n"
        "/reset - Clear conversation memory"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_memory(message):
    """Handles the /reset command."""
    user_id = message.from_user.id
    reset_user_memory(user_id)
    bot.reply_to(message, "🧹 Your conversation memory has been cleared. Let's start fresh!")

@bot.message_handler(commands=['image'])
def generate_image(message):
    """
    Handles the /image command to generate images.
    Uses the free Pollinations AI API so no extra API key is needed!
    """
    prompt = message.text.replace("/image", "").strip()
    if not prompt:
        bot.reply_to(message, "🎨 Please provide a description for the image. Example:\n`/image A futuristic city at sunset`", parse_mode="Markdown")
        return
        
    bot.reply_to(message, f"🎨 Generating image for: '{prompt}'... Please wait a moment.")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # URL encode the prompt and use the free image generation API
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        # Telegram can directly send photos from a URL!
        bot.send_photo(message.chat.id, image_url, caption=f"Here is your image: '{prompt}'")
    except Exception as e:
        print(f"Error sending image: {e}")
        bot.reply_to(message, "⚠️ Sorry, I could not generate the image right now.")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_messages(message):
    """
    Handles all incoming text messages.
    Uses the RAG pipeline powered by LangChain and Groq.
    """
    user_id = message.from_user.id
    user_text = message.text
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Add user's message to memory
        add_message_to_memory(user_id, "user", user_text)
        
        # We can eventually pass conversation history to RAG.
        # For now, we query the new RAG system:
        ai_response = query_rag(user_text)
        
        # Add AI's response to memory
        add_message_to_memory(user_id, "assistant", ai_response)
        
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        print(f"Error processing Telegram message: {e}")
        bot.reply_to(message, "⚠️ Sorry, I encountered an error while processing your request. Please try again later.")

def run_telegram_bot():
    """Runs the Telegram bot in a separate thread/process if needed."""
    print("🤖 Telegram Bot is starting up...")
    bot.infinity_polling()

if __name__ == "__main__":
    run_telegram_bot()
