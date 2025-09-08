import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to disk and return the file path."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path
