import os
from dotenv import load_dotenv

# Load environment variables from a .env file (for local development)
load_dotenv()

# ==============================================================================
# OS ENVIRONMENT VARIABLES (FOR DEPLOYMENT)
# The os.getenv() function natively grabs keys from your Hosting App (like Render, Heroku)
# So when you deploy, you just paste your API keys into the hosting provider's 
# "Environment Variables" dashboard. The code below will automatically read them!
# ==============================================================================

# Telegram Bot Token from BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Groq API Key from Groq Console
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Ensure both keys are provided before running
# THESE ARE LOADED FROM YOUR .env FILE AUTOMATICALLY.
# DO NOT PASTE YOUR REAL KEYS HERE IN THIS FILE.
# ALWAYS PASTE THEM IN THE .env FILE ONLY.
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or GROQ_API_KEY. Please create a .env file and add them.")
