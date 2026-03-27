import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"DB napaka: {e}")
        return None

def init_db():
    if not DATABASE_URL:
        return
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_message(session_id, role, content):
    if not DATABASE_URL:
        return
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, role, content)
    )
    conn.commit()
    cur.close()
    conn.close()