from flask import Flask
from routes import app
from database import init_db, restore_from_backup
from helpers import send_startup_message
from config import Config

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY  # Use SECRET_KEY from Config for consistency
    init_db()  # Initialize database on app startup
    restore_from_backup()  # Restore tokens from backup if needed
    send_startup_message()  # Send startup message via Telegram
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))