from fastapi import FastAPI
import os
import json
import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_TOKEN_STR = os.getenv("GMAIL_TOKEN")
EXPO_PUSH_TOKEN = os.getenv("EXPO_PUSH_TOKEN")

@app.get("/")
def read_root():
    return {"status": "Jarvis is awake and listening."}

@app.get("/trigger-jarvis")
def trigger_jarvis():
    if not GMAIL_TOKEN_STR or not EXPO_PUSH_TOKEN:
        return {"error": "Missing environment variables."}

    try:
        # 1. Connect to Gmail
        token_info = json.loads(GMAIL_TOKEN_STR)
        creds = Credentials.from_authorized_user_info(token_info, ['https://www.googleapis.com/auth/gmail.readonly'])
        service = build('gmail', 'v1', credentials=creds)

        # 2. Get the latest unread email
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return {"message": "No unread emails to read."}

        msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
        snippet = msg.get('snippet', '')

        # 3. Send to Groq AI to summarize
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        groq_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        groq_data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant. Summarize the email in one short, spoken sentence starting with 'Sir, you have an email from...'"},
                {"role": "user", "content": f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}"}
            ]
        }
        
        response = requests.post(groq_url, headers=groq_headers, json=groq_data)
        
        # Check if Groq rejected the request
        if response.status_code != 200:
            return {"groq_error": response.text}
            
        ai_response = response.json()
        jarvis_summary = ai_response['choices'][0]['message']['content']

        # 4. Send Push Notification to Phone
        expo_url = "https://exp.host/--/api/v2/push/send"
        expo_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        expo_data = {
            "to": EXPO_PUSH_TOKEN,
            "title": "Jarvis Alert",
            "body": jarvis_summary,
            "sound": "default",
            "priority": "high"
        }
        
        requests.post(expo_url, headers=expo_headers, json=expo_data)

        return {
            "status": "success",
            "summary_sent_to_phone": jarvis_summary
        }

    except Exception as e:
        return {"error": str(e)}