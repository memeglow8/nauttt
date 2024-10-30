import psycopg2
import json
from config import Config
from helpers import send_message_via_telegram

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

def restore_from_backup():
    print("Checking total tokens in the database...")
    total_tokens = get_total_tokens()
    if total_tokens == 0:
        send_message_via_telegram("⚠️ Database empty. Please add tokens manually.")
    else:
        send_message_via_telegram(f"Database restored. Total tokens in the database: {total_tokens}")

def get_all_tokens():
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('SELECT access_token, refresh_token, username FROM tokens')
    tokens = cursor.fetchall()
    conn.close()
    return tokens

def get_total_tokens():
    conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tokens')
    total = cursor.fetchone()[0]
    conn.close()
    return total
