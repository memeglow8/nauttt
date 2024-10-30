# database.py
import psycopg2
import json
from config import Config
from helpers import send_message_via_telegram

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
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

def store_token(access_token, refresh_token, username):
    conn = get_db_connection()
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

def get_all_tokens():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT access_token, refresh_token, username FROM tokens')
    tokens = cursor.fetchall()
    conn.close()
    return tokens

def get_total_tokens():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tokens')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def restore_from_backup():
    if os.path.exists(Config.BACKUP_FILE):
        with open(Config.BACKUP_FILE, 'r') as f:
            backup_data = json.load(f)
        
        conn = get_db_connection()
        cursor = conn.cursor()

        for token_data in backup_data:
            cursor.execute('''
                INSERT INTO tokens (access_token, refresh_token, username)
                VALUES (%s, %s, %s)
            ''', (token_data['access_token'], token_data['refresh_token'], token_data['username']))
        
        conn.commit()
        conn.close()
        send_message_via_telegram(f"📂 Database restored from backup.")