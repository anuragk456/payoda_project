from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_transcript_pdf(username: str, role: str, interview_id: int, transcript: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"transcript_{interview_id}_{username}.pdf")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)
    story = []

    story.append(Paragraph(f"Transcript for Interview {interview_id}", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Username: {username}", styles["Normal"]))
    story.append(Paragraph(f"Role: {role}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(transcript.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)
    return file_path
