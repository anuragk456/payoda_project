from api.database.db_connection import get_fdb_connection  
from datetime import datetime, timedelta  
from api.core.loggerconfig import logger

def insert_transcript(
    name: str, 
    role: str, 
    inid: int, 
    transcript: str, 
    from_time: datetime,
    to_time: datetime,
    status: str = "inprogress"
):
    """
    Insert a transcript into the database while handling ongoing interview rules.

    - Checks if interview exists in interviews.
    - Marks completed if timeout > 30 min or idle > 15 min.
    - Updates candidate/panel last_response_at if interview is ongoing.
    - Inserts transcript into transcripts.
    - Sets started_at and started_by on first transcript.

    Returns a dict describing the action performed.
    """
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()
        current_time = datetime.now()
        
        # Check if record exists in interviews
        cursor.execute(
            '''
            SELECT inid, from_time, to_time, candidate_last_response_at, panel_last_response_at, started_at, started_by, status
            FROM interviews
            WHERE inid = ?
            ''',
            [inid]
        )
        interview_record = cursor.fetchone()
        logger.info(f"Interview record fetched for inid = {inid}: {interview_record}")

        if interview_record is None:
            # First transcript -> create new interview record
            candidate_last_response_at = current_time if role.lower() == 'candidate' else None
            panel_last_response_at = current_time if role.lower() == 'panel' else None
            
            cursor.execute(
                '''
                INSERT INTO interviews (inid, from_time, to_time, candidate_last_response_at, panel_last_response_at, started_at, started_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                [inid, from_time, to_time, candidate_last_response_at, panel_last_response_at, current_time, role.lower(), status]
            )
            
            # Insert into transcripts
            cursor.execute(
                '''
                INSERT INTO transcripts (name, role, inid, transcript)
                VALUES (?, ?, ?, ?)
                ''',
                [name, role, inid, transcript]
            )
            
            connection.commit()
            cursor.close()
            return {"name": name, "role": role, "inid": inid, "action": "inserted_both_tables"}
        
        else:
            # Record exists in interviews
            existing_inid, existing_from_time, existing_to_time, existing_candidate_last_response_at, existing_panel_last_response_at, existing_started_at, existing_started_by, existing_status = interview_record
            
            # Check if status is already completed
            if existing_status.lower() == 'completed':
                cursor.close()
                return {"name": name, "role": role, "inid": inid, "action": "interview_already_completed"}
            
            # Check if current time is more than 30 minutes after to_time
            time_limit = existing_to_time + timedelta(minutes=30)
            if current_time > time_limit:
                logger.info(f"Interview {inid} marked as completed due to 30 min timeout. Current = {current_time}, Limit = {time_limit}")
                cursor.execute(
                    'UPDATE interviews SET status = ? WHERE inid = ?',
                    ['completed', inid]
                )
                connection.commit()
                cursor.close()
                return {"name": name, "role": role, "inid": inid, "action": "interview_timeout_completed"}
            
            # Check idle gap > 15 minutes
            if existing_candidate_last_response_at and existing_panel_last_response_at:
                time_diff = abs((existing_candidate_last_response_at - existing_panel_last_response_at).total_seconds() / 60)
                if time_diff > 15:
                    logger.info(f"Interview {inid} marked as completed due to idle gap > 15 mins. Gap = {time_diff} minutes")
                    cursor.execute(
                        'UPDATE interviews SET status = ? WHERE inid = ?',
                        ['completed', inid]
                    )
                    connection.commit()
                    cursor.close()
                    return {"name": name, "role": role, "inid": inid, "action": "interview_idle_timeout_completed"}
            
            # If still ongoing - update last response time
            if role.lower() == 'candidate':
                cursor.execute(
                    'UPDATE interviews SET candidate_last_response_at = ? WHERE inid = ?',
                    [current_time, inid]
                )
            elif role.lower() == 'panel':
                cursor.execute(
                    'UPDATE interviews SET panel_last_response_at = ? WHERE inid = ?',
                    [current_time, inid]
                )
            
            # Insert into transcripts
            cursor.execute(
                '''
                INSERT INTO transcripts (name, role, inid, transcript)
                VALUES (?, ?, ?, ?)
                ''',
                [name, role, inid, transcript]
            )

            cursor.execute(
                'UPDATE interviews SET status = ? WHERE inid = ?',
                [status, inid]
            )
            
            connection.commit()
            cursor.close()
            return {"name": name, "role": role, "inid": inid, "action": "updated_interview_and_inserted_transcript"}
            
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()


def get_completed_interview_ids():
    """
    Get distinct interview IDs where transcripts are marked as 'completed'.

    Returns:
        list[int]: List of interview IDs that are completed.
    """
    
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()
        rows = cursor.execute('SELECT DISTINCT inid FROM interviews WHERE status = ?', ['completed']).fetchall()
        cursor.close()
        return [r[0] for r in rows]
    finally:
        if connection:
            connection.close()

def get_conversation_by_interview(inid: int):
    """
    Fetch the full conversation for a given interview.

    Args:
        interview_id (int): The ID of the interview.

    Returns:
        list[tuple]: Rows in the format (username, role, transcript, created_at),
                     ordered by created_at ascending.
    """
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()
        rows = cursor.execute('SELECT name, role, transcript, created_at FROM transcripts WHERE inid = ? ORDER BY created_at ASC', [inid]).fetchall()
        cursor.close()
        return rows
    finally:
        if connection:
            connection.close()

def update_interview_status_to_processed(inid: int):
    """
    Update the status of an interview to 'processed' in the ongoing_interviews table.
    
    Args:
        interview_id (int): Unique identifier of the interview to update.
        
    Returns:
        dict: Result of the operation with status information.
              {"interview_id": int, "action": str, "previous_status": str or None}
    """
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT status FROM interviews WHERE inid = ?', [inid])
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return {"inid": inid, "action": "record_not_found", "previous_status": None}
        previous_status = result[0]
        cursor.execute('UPDATE interviews SET status = ? WHERE inid = ?', ['processed', inid])
        if cursor.rowcount > 0:
            connection.commit()
            cursor.close()
            return {"inid": inid, "action": "status_updated_to_processed", "previous_status": previous_status}
        else:
            cursor.close()
            return {"inid": inid, "action": "update_failed", "previous_status": previous_status}

    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def delete_transcripts_by_interview_id(inid: int) -> int:
    """
    Delete transcripts for a given interview ID.

    Args:
        inid (int): Interview ID

    Returns:
        int: Number of rows deleted
    """
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transcripts WHERE inid = ?", [inid])
        deleted_count = cursor.rowcount
        connection.commit()
        cursor.close()
        return deleted_count
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()


def get_processed_interview_ids() -> list[int]:
    """
    Get all interview IDs where status = 'processed'.

    Returns:
        list[int]: Interview IDs
    """
    connection = None
    try:
        connection = get_fdb_connection()
        cursor = connection.cursor()
        rows = cursor.execute("SELECT inid FROM interviews WHERE status = ?", ["processed"]).fetchall()
        cursor.close()
        return [row[0] for row in rows]
    finally:
        if connection:
            connection.close()
