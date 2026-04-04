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
        print("DATABASE_URL ni nastavljen — baza preskočena.")
        return
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("DB inicializirana.")

def save_message(session_id, role, content):
    if not DATABASE_URL:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, role, content)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Napaka pri shranjevanju: {e}")
    finally:
        conn.close()

def get_history(session_id):
    if not DATABASE_URL:
        return []
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content, timestamp FROM chat_history WHERE session_id = %s ORDER BY timestamp ASC",
            (session_id,)
        )
        rows = cur.fetchall()
        cur.close()
        return [{"role": r[0], "content": r[1], "timestamp": str(r[2])} for r in rows]
    except Exception as e:
        print(f"Napaka pri branju: {e}")
        return []
    finally:
        conn.close()

def get_all_sessions():
    if not DATABASE_URL:
        return []
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT session_id, MIN(timestamp), COUNT(*) 
            FROM chat_history 
            GROUP BY session_id 
            ORDER BY MIN(timestamp) DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return [{"session_id": r[0], "started": str(r[1]), "messages": r[2]} for r in rows]
    except Exception as e:
        print(f"Napaka pri branju sej: {e}")
        return []
    finally:
        conn.close()

def delete_session(session_id):
    if not DATABASE_URL:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_history WHERE session_id = %s", (session_id,))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Napaka pri brisanju: {e}")
    finally:
        conn.close()