from app import models
from app.utils.pdf_generator import generate_transcript_pdf
import os
import datetime

def process_completed_transcripts():
    transcript_dir = os.path.join("data", "transcripts")

    transcripts = models.get_completed_transcripts()
    if transcripts:
        for t in transcripts:
            tid, username, role, interview_id, transcript = t
            pdf_path = generate_transcript_pdf(username, role, interview_id, transcript, transcript_dir)
            print(f"✅ PDF created at {pdf_path}")
            models.delete_transcript(tid)
            print(f"🗑️ Deleted transcript ID {tid}")

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    stale_transcripts = models.get_stale_inprogress_transcripts(cutoff)

    if stale_transcripts:
        for tid, username, role, interview_id in stale_transcripts:
            models.delete_transcript(tid)
            print(f"🗑️ Deleted stale transcript ID {tid} (interview {interview_id}, user {username})")
