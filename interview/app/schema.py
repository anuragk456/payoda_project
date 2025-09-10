from pydantic import BaseModel

class TranscriptCreate(BaseModel):
    username: str
    role: str
    interview_id: int
    transcript: str
    status: str  # "completed" or "inprogress"
