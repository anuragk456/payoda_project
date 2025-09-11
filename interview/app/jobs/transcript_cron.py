import os, datetime
from app import models
from app.utils.pdf_generator import generate_transcript_pdf

def process_completed_transcripts():
    completed_ids = models.get_completed_interview_ids()
    if not completed_ids:
        return

    transcript_dir = os.path.join("data", "transcripts")

    for interview_id in completed_ids:
        conversation = models.get_conversation_by_interview(interview_id)
        if not conversation:
            continue

        candidate = next((u for u, r, t, c in conversation if r == "candidate"), "Unknown")

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        formatted_date = now.strftime("%Y/%m/%d %H:%M %Z")

        pdf_path = generate_transcript_pdf(
            candidate=candidate,
            interview_id=interview_id,
            conversation=conversation,
            transcript_dir=transcript_dir,
            header_date=formatted_date
        )
        if os.path.exists(pdf_path):
            print(f"PDF created at {pdf_path}")
            models.delete_transcripts_by_interview(interview_id)
            print(f"Deleted all transcripts for interview {interview_id}")
        else:
            print(f"Failed to create PDF for interview {interview_id}, skipping delete")

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    stale_transcripts = models.get_stale_inprogress_transcripts(cutoff)

    if stale_transcripts:
        for tid, username, interview_id in stale_transcripts:
            models.delete_transcript(tid)
            print(f"Deleted stale transcript ID {tid} (interview {interview_id}, user {username})")
