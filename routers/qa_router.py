from fastapi import APIRouter, UploadFile, HTTPException, Depends
from services.file_service import save_upload_file
from utils.parser_utils import extract_text_from_pdf
from services.llama_service import generate_questions_and_answers
from auth.jwt_handler import get_current_username

router = APIRouter(prefix="/qa", tags=["Q&A"])

@router.post("/generate", summary="Upload Resume + JD (PDFs) to generate interview Q&A")
async def generate_qa(
    resume: UploadFile,
    jd: UploadFile,
    username: str = Depends(get_current_username),
):
    """
    Upload Resume + Job Description (PDFs).
    Returns tailored interview Q&A using LLaMA (via Ollama).
    """
    try:
        resume_path = save_upload_file(resume)
        jd_path = save_upload_file(jd)

        resume_text = extract_text_from_pdf(resume_path)
        jd_text = extract_text_from_pdf(jd_path)

        qa_output = generate_questions_and_answers(jd_text, resume_text)
        return {"user": username, **qa_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))