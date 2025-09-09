from fastapi import FastAPI
from app.routers import transcript

app = FastAPI(title="Interview Transcript Service with DuckDB")

app.include_router(transcript.router)

@app.get("/")
def root():
    return {"message": "Transcript API running with DuckDB"}
