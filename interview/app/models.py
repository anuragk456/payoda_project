from app.database import get_connection
from typing import List, Tuple
import datetime

def insert_transcript(username: str, role: str, interview_id: int, transcript: str, status: str = "inprogress"):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO interview_transcripts (username, role, interview_id, transcript, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            [username, role, interview_id, transcript, status]
        )
        connection.commit()
        cursor.close()
        return {"username": username, "role": role, "interview_id": interview_id}
    finally:
        if connection:
            connection.close()


def get_stale_inprogress_transcripts(cutoff: datetime.datetime):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        rows = cursor.execute(
            """
            SELECT username, role, interview_id
            FROM interview_transcripts
            WHERE status = 'inprogress' AND created_at < ?
            """,
            [cutoff]
        ).fetchall()
        cursor.close()
        return rows
    finally:
        if connection:
            connection.close()


def get_completed_interview_ids():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        rows = cursor.execute("""
            SELECT DISTINCT interview_id
            FROM interview_transcripts
            WHERE status = 'completed'
        """).fetchall()
        cursor.close()
        return [r[0] for r in rows]
    finally:
        if connection:
            connection.close()


def get_conversation_by_interview(interview_id: int):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        rows = cursor.execute("""
            SELECT username, role, transcript, created_at
            FROM interview_transcripts
            WHERE interview_id = ?
            ORDER BY created_at ASC
        """, [interview_id]).fetchall()
        cursor.close()
        return rows
    finally:
        if connection:
            connection.close()


def delete_transcripts_by_interview(interview_id: int):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM interview_transcripts WHERE interview_id = ?", [interview_id])
        connection.commit()
        cursor.close()
    finally:
        if connection:
            connection.close()


def delete_transcript(transcript_id: int):
    """Delete a specific transcript by ID"""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM interview_transcripts WHERE id = ?", [transcript_id])
        connection.commit()
        cursor.close()
    finally:
        if connection:
            connection.close()