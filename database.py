import psycopg2
from config import Config

DATABASE_URL = Config.DATABASE_URL

def init_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
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
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tokens WHERE username = %s", (username,))
        cursor.execute('''
            INSERT INTO tokens (access_token, refresh_token, username)
            VALUES (%s, %s, %s)
        ''', (access_token, refresh_token, username))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error while storing token: {e}")

def get_all_tokens():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute('SELECT access_token, refresh_token, username FROM tokens')
        tokens = cursor.fetchall()
        conn.close()
        return tokens
    except Exception as e:
        print(f"Error retrieving tokens from database: {e}")
        return []

def get_total_tokens():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tokens')
        total = cursor.fetchone()[0]
        conn.close()
        return total
    except Exception as e:
        print(f"Error counting tokens in database: {e}")
        return 0

def restore_from_backup():
    try:
        total_tokens = get_total_tokens()
        print(f"Total tokens in the database: {total_tokens}")
    except Exception as e:
        print(f"Error restoring from backup: {e}")
