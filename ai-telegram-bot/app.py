from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from twilio.twiml.messaging_response import MessagingResponse
import threading
import uvicorn
import os

from rag import query_rag
# Import the Telegram bot running function
from bot import run_telegram_bot 

# We run the Telegram bot in a background thread
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background Telegram Bot thread...")
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    yield
    print("Shutting down...")

app = FastAPI(title="Omnichannel AI Assistant API", lifespan=lifespan)

# Allow CORS for the web widget if hosted on a different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
# Ensure data directory exists for RAG
os.makedirs("data", exist_ok=True)

# Mount static files (the web widget)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models for the API
class ChatRequest(BaseModel):
    message: str
    user_id: str = "web_user"

class ChatResponse(BaseModel):
    response: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve a demo page with the chat widget."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"<html><body><h1>Error loading widget</h1><p>{str(e)}</p></body></html>"

@app.post("/api/chat", response_model=ChatResponse)
async def web_chat_endpoint(req: ChatRequest):
    """
    Endpoint for the web chat widget.
    Receives user message, runs it through RAG, returns AI response.
    """
    ai_response = query_rag(req.message)
    # Simple automation hook: Check if user includes an email (very naive approach)
    if "@" in req.message and "." in req.message.split("@")[-1]:
        print(f"Lead captured from web chat: {req.message}")
        with open("data/leads.txt", "a") as f:
            f.write(f"Web User Requesting Contact with potential email: {req.message}\n")

    return ChatResponse(response=ai_response)

@app.post("/api/whatsapp")
async def whatsapp_webhook(Body: str = Form(""), From: str = Form("")):
    """
    Twilio webhook endpoint for WhatsApp.
    Receives incoming WhatsApp messages configured in Twilio Console.
    """
    print(f"Received WhatsApp message from {From}: {Body}")
    
    # Run through RAG
    ai_response = query_rag(Body)
    
    # Optional business automation for WhatsApp
    if "book" in Body.lower() or "appointment" in Body.lower():
        print(f"Appointment request captured from {From}")
        with open("data/appointments.txt", "a") as f:
            f.write(f"WhatsApp User {From} wants an appointment. Details: {Body}\n")
    
    # Twilio requires a TwiML response
    twiml_response = MessagingResponse()
    twiml_response.message(ai_response)
    
    # FastAPI returns XML for Twilio
    return Response(content=str(twiml_response), media_type="application/xml")

if __name__ == "__main__":
    # Run the unified server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
