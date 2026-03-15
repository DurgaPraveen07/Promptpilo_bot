# Omnichannel AI Business Assistant

A complete Python platform powered by the Groq API (Llama 3). This project act as a unified AI assistant supporting:
1. **Telegram Bot**
2. **Website Chatbot** (FastAPI Backend + HTML/JS Widget)
3. **WhatsApp Bot** (via Twilio Webhook)
4. **RAG Knowledge Base** (Retrieval-Augmented Generation context using ChromaDB)

## Features

- **Groq API Integration:** Lightning-fast AI responses using Groq.
- **RAG Capability:** Ingest your business PDFs and text files so the AI knows everything about your business.
- **Unified FastAPI Backend:** Serves the website widget and Twilio webhook endpoints simultaneously.
- **Business Automation Hooks:** Intercepts emails and contact requests and saves them locally.
- **24/7 Deployment Setup:** Dockerized and ready for VPS deployment.

## Project Structure

```
ai-telegram-bot/
├── app.py             # Main FastAPI entry point (runs Telegram bot in background)
├── bot.py             # Telegram specific handling logic
├── rag.py             # LangChain + ChromaDB RAG implementation
├── config.py          # Environment configuration
├── memory.py          # In-memory dictionary for conversation history
├── data/              # Put your business knowledge documents (txt/pdf) here
├── static/            # Frontend resources (index.html web widget)
├── requirements.txt   # Dependencies
├── Dockerfile         # Docker container definition
├── docker-compose.yml # Easy deployment orchestrator
└── .env.example       # Example environment variables
```

## Setup Instructions

### 1. Install dependencies

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your keys:
- `TELEGRAM_TOKEN` from [@BotFather](https://t.me/botfather)
- `GROQ_API_KEY` from [Groq Console](https://console.groq.com/keys)

### 3. Add Business Knowledge (For RAG)

Drop any text files (`.txt`), CSVs, or PDFs into the `/data` folder. These will form the knowledge base the AI uses to answer questions.

### 4. Run the Bot Locally

```bash
python app.py
```
This single command will:
- Process the knowledge base into ChromaDB.
- Start the Telegram Bot.
- Start the Website Widget at `http://localhost:8000/`.
- Open webhook ports for WhatsApp at `http://localhost:8000/api/whatsapp`.

---

## Setting up WhatsApp (Twilio)

1. Create a Twilio account and activate the WhatsApp Sandbox.
2. Run Ngrok locally to expose your server:
   ```bash
   ngrok http 8000
   ```
3. Copy your Ngrok URL (e.g., `https://xxxx.ngrok-free.app/api/whatsapp`) and paste it into your Twilio Sandbox settings under **"When a message comes in"**.

---

## 24/7 Deployment Guide (Run your bot forever)

If you close your computer, the bot stops. To make it run 24/7, you need to deploy it using **Docker** on a cloud server (VPS like DigitalOcean, Hetzner, AWS, etc.).

### Deploying via Docker (Recommended)

Assuming you have cloned this repository on a VPS that has Docker installed:

1. Create and configure your `.env` file on the server.
2. Put any knowledge base files into the `data/` directory.
3. Run the container in the background:
   ```bash
   docker-compose up -d --build
   ```

The bot is now running 24/7. It will automatically restart if the server reboots or if the application crashes.

### Deploying via PM2 (Non-Docker Alternative)

If you prefer not to use Docker, you can use PM2 to keep it alive:
```bash
# Install Node and PM2
npm install -g pm2

# Start the app
pm2 start app.py --name "ai-assistant" --interpreter python3

# Make it start on boot
pm2 startup
pm2 save
```
