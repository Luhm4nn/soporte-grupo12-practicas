import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audio import Audio
from app.crud.audio import get_audio


def get_audio_or_404(db: Annotated[Session, Depends(get_db)], audio_id: uuid.UUID) -> Audio:
    audio = get_audio(db, audio_id)
    if not audio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio not found")
    return audio
