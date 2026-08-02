import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audio import Audio, AudioStatus


def create_audio(db: Session, filename: str, original_name: str, file_size: int) -> Audio:
    audio = Audio(
        filename=filename,
        original_name=original_name,
        file_size=file_size,
        status=AudioStatus.PENDING,
    )
    db.add(audio)
    db.commit()
    db.refresh(audio)
    return audio


def get_audio(db: Session, audio_id: uuid.UUID) -> Audio | None:
    return db.query(Audio).filter(Audio.id == audio_id).first()


def update_status(db: Session, audio_id: uuid.UUID, status: AudioStatus, error_message: str | None = None) -> Audio | None:
    audio = get_audio(db, audio_id)
    if not audio:
        return None
    audio.status = status
    audio.error_message = error_message
    audio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(audio)
    return audio


def update_transcription(
    db: Session,
    audio_id: uuid.UUID,
    text: str,
    segments: list[dict],
    language: str,
    duration: float,
) -> Audio | None:
    audio = get_audio(db, audio_id)
    if not audio:
        return None
    audio.transcription_text = text
    audio.transcription_segments = segments
    audio.language = language
    audio.duration = duration
    audio.status = AudioStatus.COMPLETED
    audio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(audio)
    return audio


def update_ai_result(db: Session, audio_id: uuid.UUID, field: str, value: any) -> Audio | None:
    audio = get_audio(db, audio_id)
    if not audio:
        return None
    setattr(audio, field, value)
    audio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(audio)
    return audio
