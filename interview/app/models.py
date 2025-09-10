from app.database import get_connection
from typing import List, Tuple
import datetime

def insert_transcript(username: str, role: str, interview_id: int, transcript: str, status: str = "inprogress"):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO interview_transcripts (username, role, interview_id, transcript, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        [username, role, interview_id, transcript, status]
    )
    conn.close()
    return {"username": username, "role": role, "interview_id": interview_id}


def get_stale_inprogress_transcripts(cutoff: datetime.datetime):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT username, role, interview_id
        FROM interview_transcripts
        WHERE status = 'inprogress' AND created_at < ?
        """,
        [cutoff]
    ).fetchall()
    conn.close()
    return rows


def get_completed_interview_ids():
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT interview_id
        FROM interview_transcripts
        WHERE status = 'completed'
    """).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_conversation_by_interview(interview_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT username, role, transcript, created_at
        FROM interview_transcripts
        WHERE interview_id = ?
        ORDER BY created_at ASC
    """, [interview_id]).fetchall()
    conn.close()
    return rows


def delete_transcripts_by_interview(interview_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM interview_transcripts WHERE interview_id = ?", [interview_id])
    conn.close()
