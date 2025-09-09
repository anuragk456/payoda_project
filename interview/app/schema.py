from pydantic import BaseModel

class TranscriptCreate(BaseModel):
    email: str
    role: str
    interview_id: int
    transcript: str
    status: str  # "completed" or "inprogress"
