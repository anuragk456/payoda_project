# Firebird Package

A Python package for managing interview transcripts in Firebird database.

## Installation

```bash
pip install -e .
```

## Usage

```python
from firebird_package import (
    insert_transcript,
    get_completed_interview_ids,
    get_conversation_by_interview,
    update_interview_status_to_processed,
    delete_transcripts_by_interview_id,
    get_processed_interview_ids
)

# Insert a transcript
result = insert_transcript(
    name="John Doe",
    role="candidate",
    inid=123,
    transcript="Hello, this is my response",
    from_time=datetime.now(),
    to_time=datetime.now() + timedelta(hours=1)
)

# Get completed interview IDs
completed_ids = get_completed_interview_ids()

# Get conversation for an interview
conversation = get_conversation_by_interview(123)
```

## Functions

- `insert_transcript()` - Insert a transcript with interview management
- `get_completed_interview_ids()` - Get IDs of completed interviews
- `get_conversation_by_interview()` - Fetch full conversation for an interview
- `update_interview_status_to_processed()` - Mark interview as processed
- `delete_transcripts_by_interview_id()` - Delete transcripts for an interview
- `get_processed_interview_ids()` - Get IDs of processed interviews