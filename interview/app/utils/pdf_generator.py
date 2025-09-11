from fpdf import FPDF
import os

def generate_transcript_pdf(candidate, interview_id, conversation, transcript_dir, header_date):
    os.makedirs(transcript_dir, exist_ok=True)
    
    candidate_display = candidate.split("@")[0] if "@" in candidate else candidate
    pdf_path = os.path.join(transcript_dir, f"{candidate_display}_{interview_id}.pdf")

    # Create PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Interview with {candidate_display} - {header_date} - Transcript", ln=True, align='C')
    pdf.ln(5)

    # Transcript heading
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Transcript", ln=True)
    pdf.ln(5)

    # Conversation content
    pdf.set_font('Arial', '', 10)
    
    for username, role, text, created_at in conversation:
        display_name = username.split("@")[0] if "@" in username else username
        line = f"{display_name} [{created_at.strftime('%H:%M:%S')}] : {text}"
        
        # Handle text wrapping for long lines
        pdf.multi_cell(0, 6, line)
        pdf.ln(2)
    print("hello")
    pdf.output(pdf_path)
    return pdf_path