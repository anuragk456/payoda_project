from app import models
from app.utils.pdf_generator import generate_transcript_pdf
import os

def process_completed_transcripts():
    transcripts = models.get_completed_transcripts()
    if not transcripts:
        return

    transcript_dir = os.path.join("data", "transcripts")

    for t in transcripts:
        tid, username, interview_id, transcript = t
        pdf_path = generate_transcript_pdf(username, interview_id, transcript, transcript_dir)
        print(f"✅ PDF created at {pdf_path}")
        models.delete_transcript(tid)
        print(f"🗑️ Deleted transcript ID {tid}")
