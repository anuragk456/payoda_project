from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
import os

def generate_transcript_pdf(candidate, interview_id, conversation, transcript_dir, header_date):
    os.makedirs(transcript_dir, exist_ok=True)
    
    candidate_display = candidate.split("@")[0] if "@" in candidate else candidate
    pdf_path = os.path.join(transcript_dir, f"{candidate_display}_{interview_id}.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=14, spaceAfter=12)
    speaker_style = ParagraphStyle("Speaker", parent=styles["Normal"], fontSize=10, spaceAfter=4, leading=14)

    story = []
    story.append(Paragraph(f"Interview with {candidate_display} - {header_date} - Transcript", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Transcript", styles["Heading2"]))
    story.append(Spacer(1, 12))

    for username, role, text, created_at in conversation:
        display_name = username.split("@")[0] if "@" in username else username
        line = f"{display_name} [{created_at.strftime('%H:%M:%S')}] : {text}"
        story.append(Paragraph(line, speaker_style))

    doc.build(story)
    return pdf_path
