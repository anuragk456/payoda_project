from .database import get_connection

def insert_transcript(username: str, interview_id: int, transcript: str, status: str):
    conn = get_connection()
    result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM interview_transcripts").fetchone()
    next_id = result[0] if result else 1

    conn.execute("""
        INSERT INTO interview_transcripts (id, username, interview_id, transcript, status)
        VALUES (?, ?, ?, ?, ?)
    """, (next_id, username, interview_id, transcript, status))

    conn.close()
    return next_id
