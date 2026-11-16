from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import requests

# 1. Load the .env file (this only works locally on your laptop)
load_dotenv()

# 2. Initialize the app
app = FastAPI()

# 3. Securely grab the API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# (We will add the Expo push token later)

# --- ROUTES ---

@app.get("/")
def read_root():
    # This is the health check route Render and UptimeRobot will ping
    key_status = "loaded" if GROQ_API_KEY else "missing"
    return {
        "status": "Jarvis is awake and listening.",
        "api_key_status": key_status
    }

# We will fill this in later when we connect Gmail
@app.post("/webhook/gmail")
async def receive_gmail(request: Request):
    data = await request.json()
    print("Received Gmail data:", data)
    return {"status": "success"}

# We will use this later to trigger the phone call/app
@app.get("/trigger-call")
def trigger_call():
    return {"message": "This will eventually trigger the phone app."}