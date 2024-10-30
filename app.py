import os
from flask import Flask
from routes import app
from database import init_db, restore_from_backup
from helpers import send_message_via_telegram
from config import Config

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    init_db()
    restore_from_backup()  # Restore tokens from backup if needed
    send_message_via_telegram("🚀 Application started successfully!")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
