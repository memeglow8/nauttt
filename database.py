import os  # Add this import
import psycopg2
import json
from config import Config
from helpers import send_message_via_telegram

# Initialize PostgreSQL database
def init_db():
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Store token information in the database
def store_token(access_token, refresh_token, username):
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tokens WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.execute("DELETE FROM tokens WHERE username = %s", (username,))

    cursor.execute('''
        INSERT INTO tokens (access_token, refresh_token, username)
        VALUES (%s, %s, %s)
    ''', (access_token, refresh_token, username))
    conn.commit()
    conn.close()

    send_message_via_telegram(f"Token added for @{username}.")

# Restore tokens from backup if database is empty
def restore_from_backup():
    if os.path.exists(Config.BACKUP_FILE):
        # Check if the backup file is empty
        if os.path.getsize(Config.BACKUP_FILE) == 0:
            print("Backup file is empty. Skipping restoration.")
            return

        try:
            with open(Config.BACKUP_FILE, 'r') as f:
                backup_data = json.load(f)

            restored_count = 0
            for token_data in backup_data:
                store_token(
                    token_data['access_token'],
                    token_data.get('refresh_token'),
                    token_data['username']
                )
                restored_count += 1

            send_message_via_telegram(f"📂 Backup restored. Total tokens restored: {restored_count}")

        except json.JSONDecodeError:
            print("Error: Backup file contains invalid JSON. Skipping restoration.")
            send_message_via_telegram("⚠️ Error: Backup file contains invalid JSON and could not be restored.")

# Retrieve all tokens
def get_all_tokens():
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('SELECT access_token, refresh_token, username FROM tokens')
    tokens = cursor.fetchall()
    conn.close()
    return tokens

# Retrieve the total count of tokens
def get_total_tokens():
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tokens')
    total = cursor.fetchone()[0]
    conn.close()
    return total
