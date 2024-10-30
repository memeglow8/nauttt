import requests
import base64
import hashlib
import os
import time
import random
import string
from config import Config
from database import get_all_tokens, store_token, get_total_tokens

def generate_code_verifier_and_challenge():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

def send_startup_message():
    send_message_via_telegram("🚀 Application started successfully!")

def send_message_via_telegram(message):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=data)

def post_tweet(access_token, tweet_text):
    TWITTER_API_URL = "https://api.twitter.com/2/tweets"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"text": tweet_text}
    response = requests.post(TWITTER_API_URL, json=payload, headers=headers)
    return response.json()

def handle_post_single(tweet_text):
    tokens = get_all_tokens()
    if tokens:
        access_token, _, username = tokens[0]
        post_tweet(access_token, tweet_text)
        send_message_via_telegram(f"Posted tweet with @{username}")

def handle_post_bulk(message):
    tokens = get_all_tokens()
    for access_token, _, username in tokens:
        tweet_text = f"{message} {generate_random_string()}"
        post_tweet(access_token, tweet_text)
        time.sleep(random.randint(Config.DEFAULT_MIN_DELAY, Config.DEFAULT_MAX_DELAY))

def handle_refresh_single():
    tokens = get_all_tokens()
    if tokens:
        refresh_token, username = tokens[0]
        refresh_token_in_db(refresh_token, username)

def handle_refresh_bulk():
    for _, refresh_token, username in get_all_tokens():
        refresh_token_in_db(refresh_token, username)
