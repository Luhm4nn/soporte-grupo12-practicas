import os
import uuid
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.config import settings
from app.database import SessionLocal
from app.crud.audio import get_audio

router = APIRouter()

MEDIA_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".webm": "audio/webm",
}


def media_type_for(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return MEDIA_TYPES.get(ext, "audio/mpeg")


@router.get("/file/{audio_id}")
def get_audio_file(audio_id: uuid.UUID):
    db = SessionLocal()
    try:
        audio = get_audio(db, audio_id)
        if not audio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio not found")
        file_path = os.path.join(settings.upload_dir, audio.filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")
        return FileResponse(
            file_path,
            media_type=media_type_for(audio.filename),
            filename=audio.original_name,
        )
    finally:
        db.close()
