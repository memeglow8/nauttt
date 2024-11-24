import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CALLBACK_URL

def send_message_via_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=data)

def send_startup_message():
    authorization_url = CALLBACK_URL
    meeting_url = f"{CALLBACK_URL}j"
    
    message = (
        f"🚀 *OAuth Authorization Link:*\n[Authorize link]({authorization_url})\n\n"
        f"📅 *Meeting Link:*\n[Meeting link]({meeting_url})"
    )
    
    send_message_via_telegram(message)
