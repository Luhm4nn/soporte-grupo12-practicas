import logging
import subprocess
import os

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"mp3", "wav", "m4a", "ogg", "opus", "aac", "webm"}


def is_supported(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in SUPPORTED_FORMATS


def convert_to_wav(input_path: str, output_path: str) -> str:
    logger.info("Converting %s to WAV ...", input_path)
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("FFmpeg conversion failed: %s", result.stderr)
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
    logger.info("Conversion complete: %s", output_path)
    return output_path


def get_wav_path(audio_path: str) -> str:
    base, _ = os.path.splitext(audio_path)
    return f"{base}_converted.wav"


def ensure_wav(input_path: str) -> str:
    ext = input_path.rsplit(".", 1)[-1].lower() if "." in input_path else ""
    if ext == "wav":
        return input_path
    wav_path = get_wav_path(input_path)
    return convert_to_wav(input_path, wav_path)
