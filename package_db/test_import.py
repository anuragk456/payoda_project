#!/usr/bin/env python3
"""
Test script to verify package import functionality
"""

try:
    from firebird_package import (
        insert_transcript,
        get_completed_interview_ids,
        get_conversation_by_interview,
        update_interview_status_to_processed,
        delete_transcripts_by_interview_id,
        get_processed_interview_ids
    )

    print("✅ Successfully imported all functions from firebird_package!")
    print("Available functions:")
    print("  - insert_transcript")
    print("  - get_completed_interview_ids")
    print("  - get_conversation_by_interview")
    print("  - update_interview_status_to_processed")
    print("  - delete_transcripts_by_interview_id")
    print("  - get_processed_interview_ids")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Make sure to install the package first: pip install -e .")