from app.database import get_connection

def insert_transcript(username: str, interview_id: int, transcript: str, status: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO interview_transcripts (username, interview_id, transcript, status)
        VALUES (?, ?, ?, ?)
    """, [username, interview_id, transcript, status])

def get_completed_transcripts():
    conn = get_connection()
    return conn.execute("""
        SELECT id, username, interview_id, transcript
        FROM interview_transcripts
        WHERE status = 'completed'
    """).fetchall()

def delete_transcript(tid: int):
    conn = get_connection()
    conn.execute("DELETE FROM interview_transcripts WHERE id = ?", [tid])
