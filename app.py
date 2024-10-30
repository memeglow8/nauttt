from flask import Flask
from config import Config
from database import init_db, restore_from_backup
from helpers import send_startup_message
import os

# Initialize Flask application
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY  # Use SECRET_KEY from Config

# Initialize database and restore from backup
init_db()
restore_from_backup()
send_startup_message()

# Import all routes after initializing the app to ensure routes are registered
import routes  # Ensure this is placed after app initialization

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
