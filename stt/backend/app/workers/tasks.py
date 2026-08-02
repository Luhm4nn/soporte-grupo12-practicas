import logging
import uuid
import os

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.audio import AudioStatus
from app.crud.audio import update_status, update_transcription
from app.core.audio_converter import ensure_wav
from app.core.transcriber import transcribe_audio

logger = logging.getLogger(__name__)


def process_transcription(audio_id_str: str, file_path: str) -> None:
    audio_id = uuid.UUID(audio_id_str)
    db: Session = SessionLocal()
    try:
        update_status(db, audio_id, AudioStatus.PROCESSING)

        wav_path = ensure_wav(file_path)

        text, segments, language, duration = transcribe_audio(wav_path)

        update_transcription(db, audio_id, text, segments, language, duration)

        if wav_path != file_path and os.path.exists(wav_path):
            os.remove(wav_path)

        logger.info("Transcription complete for audio %s", audio_id)
    except Exception as e:
        logger.exception("Transcription failed for audio %s: %s", audio_id, e)
        update_status(db, audio_id, AudioStatus.FAILED, str(e))
    finally:
        db.close()
