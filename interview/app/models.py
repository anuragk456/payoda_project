from app.database import get_connection

def insert_transcript(username, role, interview_id, transcript, status):
    conn = get_connection()
    conn.execute(
        "INSERT INTO interview_transcripts (username, role, interview_id, transcript, status) VALUES (?, ?, ?, ?, ?)",
        [username, role, interview_id, transcript, status]
    )
    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return row_id


def get_completed_transcripts():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, username, role, interview_id, transcript
        FROM interview_transcripts
        WHERE status = 'completed'
    """).fetchall()
    conn.close()
    return rows


def delete_transcript(tid: int):
    conn = get_connection()
    conn.execute("DELETE FROM interview_transcripts WHERE id = ?", [tid])
    conn.close()


def get_stale_inprogress_transcripts(cutoff):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, username, role, interview_id
        FROM interview_transcripts
        WHERE status = 'inprogress' AND created_at < ?
        """,
        [cutoff]
    ).fetchall()
    conn.close()
    return rows
