from flask import Flask
from routes import app as routes_blueprint
from database import init_db, restore_from_backup
from helpers import send_startup_message
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY  # Use SECRET_KEY from Config for consistency
    
    # Register the Blueprint for routes
    app.register_blueprint(routes_blueprint, url_prefix="/")
    
    # Initialize the database and perform any required startup actions
    init_db()  # Initialize the database tables if not present
    restore_from_backup()  # Check and notify total tokens in the database
    send_startup_message()  # Send startup message via Telegram to notify app is running
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Define the host and port for running the application
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
