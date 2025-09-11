import os, datetime
from app import models
from app.utils.pdf_generator import generate_transcript_pdf

def process_completed_transcripts():
    try:
        completed_ids = models.get_completed_interview_ids()
        if not completed_ids:
            print("No completed interviews found")
            return

        transcript_dir = os.path.join("data", "transcripts")

        for interview_id in completed_ids:
            try:
                conversation = models.get_conversation_by_interview(interview_id)
                if not conversation:
                    print(f"No conversation found for interview {interview_id}")
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
            except Exception as e:
                print(f"Error processing interview {interview_id}: {e}")
                continue

        # Clean up stale transcripts
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        stale_transcripts = models.get_stale_inprogress_transcripts(cutoff)

        if stale_transcripts:
            for username, role, interview_id in stale_transcripts:  # Fixed unpacking
                try:
                    models.delete_transcript(interview_id)  # You might need to adjust this based on your actual delete method
                    print(f"Deleted stale transcript (interview {interview_id}, user {username})")
                except Exception as e:
                    print(f"Error deleting stale transcript for interview {interview_id}: {e}")
        else:
            print("No stale transcripts found")

    except Exception as e:
        print(f"Error in process_completed_transcripts: {e}")
