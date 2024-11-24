import random
import time
import requests
from telegram_utils import send_message_via_telegram
from database import get_all_tokens, refresh_token_in_db
from config import DEFAULT_MIN_DELAY, DEFAULT_MAX_DELAY
from utils import generate_random_string

def post_tweet(access_token, tweet_text):
    TWITTER_API_URL = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"text": tweet_text}
    
    response = requests.post(TWITTER_API_URL, json=payload, headers=headers)
    
    if response.status_code == 201:
        tweet_data = response.json()
        return f"Tweet posted successfully: {tweet_data['data']['id']}"
    else:
        error_message = response.json().get("detail", "Failed to post tweet")
        return f"Error posting tweet: {error_message}"

def handle_post_single(tweet_text):
    tokens = get_all_tokens()
    if tokens:
        access_token, _, username = tokens[0]
        result = post_tweet(access_token, tweet_text)
        send_message_via_telegram(f"📝 Tweet posted with @{username}: {result}")
    else:
        send_message_via_telegram("❌ No tokens found to post a tweet.")

def handle_post_bulk(message):
    tokens = get_all_tokens()
    parts = message.split(' ', 1)
    
    if len(parts) < 2:
        send_message_via_telegram("❌ Incorrect format. Use `/post_bulk <tweet content>`.")
        return
        
    base_tweet_text = parts[1]
    
    if not tokens:
        send_message_via_telegram("❌ No tokens found to post tweets.")
        return
    
    for access_token, _, username in tokens:
        random_suffix = generate_random_string(10)
        tweet_text = f"{base_tweet_text} {random_suffix}"
        
        result = post_tweet(access_token, tweet_text)
        delay = random.randint(DEFAULT_MIN_DELAY, DEFAULT_MAX_DELAY)
        
        send_message_via_telegram(
            f"📝 Tweet posted with @{username}: {result}\n"
            f"⏱ Delay before next post: {delay} seconds."
        )
        
        time.sleep(delay)
        
    send_message_via_telegram(f"✅ Bulk tweet posting complete. {len(tokens)} tweets posted.")

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
        send_message_via_telegram(f"✅ Bulk token refresh complete. {len(tokens)} tokens refreshed.")
    else:
        send_message_via_telegram("❌ No tokens found to refresh.")
