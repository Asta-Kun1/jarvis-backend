from fastapi import FastAPI
import os
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_TOKEN_STR = os.getenv("GMAIL_TOKEN")

@app.get("/")
def read_root():
    return {
        "status": "Jarvis is awake and listening.",
        "groq_key": "loaded" if GROQ_API_KEY else "missing",
        "gmail_token": "loaded" if GMAIL_TOKEN_STR else "missing"
    }

@app.get("/read-email")
def read_email():
    if not GMAIL_TOKEN_STR:
        return {"error": "Gmail token not found in environment variables."}

    try:
        token_info = json.loads(GMAIL_TOKEN_STR)
        creds = Credentials.from_authorized_user_info(token_info, ['https://www.googleapis.com/auth/gmail.readonly'])
        service = build('gmail', 'v1', credentials=creds)

        # Get the most recent unread email
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return {"message": "No new unread emails."}

        msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")

        return {
            "status": "success",
            "sender": sender,
            "subject": subject,
            "snippet": msg.get('snippet', '')
        }

    except Exception as e:
        return {"error": str(e)}