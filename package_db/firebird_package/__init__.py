"""
Firebird Database Package

A package for managing interview transcripts in Firebird database.
Provides easy-to-use functions for inserting, retrieving, and managing interview data.
"""

from .firebird_db import (
    insert_transcript,
    get_completed_interview_ids,
    get_conversation_by_interview,
    update_interview_status_to_processed,
    delete_transcripts_by_interview_id,
    get_processed_interview_ids
)

__version__ = "1.0.0"
__author__ = "Anurag kurmi"

__all__ = [
    "insert_transcript",
    "get_completed_interview_ids",
    "get_conversation_by_interview",
    "update_interview_status_to_processed",
    "delete_transcripts_by_interview_id",
    "get_processed_interview_ids"
]