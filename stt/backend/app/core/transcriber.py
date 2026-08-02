import logging

from faster_whisper import WhisperModel

from app.config import settings

logger = logging.getLogger(__name__)

_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info("Loading Whisper model '%s'...", settings.whisper_model_size)
        _model = WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")
        logger.info("Whisper model loaded successfully")
    return _model


def transcribe_audio(audio_path: str) -> tuple[str, list[dict], str, float]:
    model = get_model()
    logger.info("Transcribing %s ...", audio_path)
    segments, info = model.transcribe(audio_path, beam_size=5)

    language = info.language
    duration = info.duration
    text_parts: list[str] = []
    segment_list: list[dict] = []

    for seg in segments:
        text_parts.append(seg.text.strip())
        segment_list.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })

    full_text = " ".join(text_parts)
    logger.info("Transcription complete: %d chars, language=%s, duration=%.2fs", len(full_text), language, duration)
    return full_text, segment_list, language, duration
