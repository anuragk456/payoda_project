from fastapi import APIRouter
from app import models, schema

router = APIRouter()

@router.post("/interviews/{inid}/transcript/upload")
def upload_transcript(inid: int, request: schema.TranscriptCreate):
    transcript_key = models.insert_transcript(
        username=request.username,
        role=request.role,
        interview_id=inid,
        transcript=request.transcript,
        status=request.status
    )
    return {"username": transcript_key["username"], "role": transcript_key["role"], "interview_id": transcript_key["interview_id"]}
