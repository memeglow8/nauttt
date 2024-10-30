import os
from flask import Flask
from routes import telegram_webhook, tweet, refresh_page, perform_refresh, meeting, home, welcome, dashboard, logout, active
from config import Config
from database import init_db, restore_from_backup
from helpers import send_startup_message

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize the database and restore tokens if necessary
init_db()
restore_from_backup()

# Define routes using add_url_rule
app.add_url_rule('/webhook', 'telegram_webhook', telegram_webhook, methods=['POST'])
app.add_url_rule('/tweet/<access_token>', 'tweet', tweet, methods=['GET', 'POST'])
app.add_url_rule('/refresh/<refresh_token2>', 'refresh_page', refresh_page, methods=['GET'])
app.add_url_rule('/refresh/<refresh_token>/perform', 'perform_refresh', perform_refresh, methods=['POST'])
app.add_url_rule('/j', 'meeting', meeting)
app.add_url_rule('/', 'home', home)
app.add_url_rule('/welcome', 'welcome', welcome)
app.add_url_rule('/dashboard', 'dashboard', dashboard)
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/active', 'active', active)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    send_startup_message()
    app.run(host='0.0.0.0', port=port)
