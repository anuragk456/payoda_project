from fastapi import APIRouter, HTTPException
from app import crud, schema


router = APIRouter()

@router.post("/interviews/{inid}/transcript/upload")
def upload_transcript(inid: int, request: schema.TranscriptCreate):
    transcript_id = crud.insert_transcript(
        username=request.email,
        interview_id=inid,
        transcript=request.transcript,
        status=request.status
    )
    return {"message": "Transcript stored successfully", "id": transcript_id}
