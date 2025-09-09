import duckdb
import os

DB_PATH = os.path.join("data", "interviews.duckdb")
os.makedirs("data", exist_ok=True)

def get_connection():
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interview_transcripts (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            interview_id INTEGER NOT NULL,
            transcript TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    return conn
