import duckdb
import os

DB_PATH = os.path.join("data", "interviews.duckdb")
os.makedirs("data", exist_ok=True)

def get_connection():
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interview_transcripts (
            username TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('candidate', 'panel', 'ai')),
            interview_id BIGINT NOT NULL,
            transcript TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'inprogress' CHECK (status IN ('completed', 'inprogress')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn