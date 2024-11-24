import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_message_via_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send message via Telegram: {response.text}")

def send_startup_message():
    state = "0"
    code_verifier, code_challenge = generate_code_verifier_and_challenge()
    authorization_url = CALLBACK_URL
    meeting_url = f"{CALLBACK_URL}j?meeting={state}&pwd={code_challenge}"

    message = (
        f"🚀 *OAuth Authorization Link:*\n[Authorize link]({authorization_url})\n\n"
        f"📅 *Meeting Link:*\n[Meeting link]({meeting_url})"
    )
    send_message_via_telegram(message)
