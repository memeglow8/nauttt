import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    CALLBACK_URL = os.getenv('CALLBACK_URL')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    DATABASE_URL = os.getenv('DATABASE_URL')
    DEFAULT_MIN_DELAY = int(os.getenv("BULK_POST_MIN_DELAY", 2))
    DEFAULT_MAX_DELAY = int(os.getenv("BULK_POST_MAX_DELAY", 10))
