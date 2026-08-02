import uuid
import os
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from rq import Queue

from app.database import get_db
from app.config import settings
from app.models.audio import AudioStatus
from app.schemas.audio import (
    AudioUploadResponse,
    AudioStatusResponse,
    TranscriptionResponse,
    Segment,
    ImproveRequest,
    ImproveResponse,
    RemoveFillersResponse,
    SummarizeRequest,
    SummarizeResponse,
    TasksResponse,
    DatesResponse,
    PhonesResponse,
    EmailsResponse,
    LinksResponse,
    TagsResponse,
    ChatRequest,
    ChatResponse,
)
from app.crud.audio import create_audio, get_audio, update_ai_result
from app.core.audio_converter import is_supported
from app.services.ai_service import (
    improve_text,
    remove_fillers,
    summarize,
    extract_tasks,
    extract_dates,
    extract_phones,
    extract_emails,
    extract_links,
    extract_tags,
    chat_with_transcription,
)
from app.workers.tasks import process_transcription
from app.workers.rq_worker import redis_conn

logger = logging.getLogger(__name__)

router = APIRouter()
task_queue = Queue("default", connection=redis_conn)


ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "opus", "aac", "webm"}


@router.post("/upload", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    audio = create_audio(db, filename=unique_name, original_name=file.filename or "audio", file_size=len(content))

    task_queue.enqueue(process_transcription, str(audio.id), file_path)

    return AudioUploadResponse(
        id=audio.id,
        original_name=audio.original_name,
        file_size=audio.file_size,
        status=audio.status.value if hasattr(audio.status, 'value') else str(audio.status),
    )


@router.get("/{audio_id}", response_model=AudioStatusResponse)
def get_audio_status(audio_id: uuid.UUID, db: Session = Depends(get_db)):
    audio = get_audio(db, audio_id)
    if not audio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio not found")

    segments = None
    if audio.transcription_segments:
        segments = [Segment(**s) for s in audio.transcription_segments]

    return AudioStatusResponse(
        id=audio.id,
        original_name=audio.original_name,
        duration=audio.duration,
        language=audio.language,
        status=audio.status.value if hasattr(audio.status, 'value') else str(audio.status),
        error_message=audio.error_message,
        created_at=audio.created_at,
        updated_at=audio.updated_at,
        transcription_text=audio.transcription_text,
        transcription_segments=segments,
        tags=audio.tags,
        tasks=audio.tasks,
        dates=audio.dates,
        emails=audio.emails,
        phones=audio.phones,
        links=audio.links,
        summary_short=audio.summary_short,
        summary_medium=audio.summary_medium,
        summary_detailed=audio.summary_detailed,
        improved_text=audio.improved_text,
        text_no_fillers=audio.text_no_fillers,
    )


@router.post("/improve", response_model=ImproveResponse)
def improve(req: ImproveRequest):
    result = improve_text(req.text)
    return ImproveResponse(improved_text=result)


@router.post("/remove-fillers", response_model=RemoveFillersResponse)
def remove_fillers_endpoint(req: ImproveRequest):
    result = remove_fillers(req.text)
    return RemoveFillersResponse(cleaned_text=result)


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_endpoint(req: SummarizeRequest):
    result = summarize(req.text, req.level)
    return SummarizeResponse(summary=result)


@router.post("/tasks", response_model=TasksResponse)
def tasks_endpoint(req: ImproveRequest):
    result = extract_tasks(req.text)
    return TasksResponse(tasks=result)


@router.post("/dates", response_model=DatesResponse)
def dates_endpoint(req: ImproveRequest):
    result = extract_dates(req.text)
    return DatesResponse(dates=result)


@router.post("/phones", response_model=PhonesResponse)
def phones_endpoint(req: ImproveRequest):
    result = extract_phones(req.text)
    return PhonesResponse(phones=result)


@router.post("/emails", response_model=EmailsResponse)
def emails_endpoint(req: ImproveRequest):
    result = extract_emails(req.text)
    return EmailsResponse(emails=result)


@router.post("/links", response_model=LinksResponse)
def links_endpoint(req: ImproveRequest):
    result = extract_links(req.text)
    return LinksResponse(links=result)


@router.post("/tags", response_model=TagsResponse)
def tags_endpoint(req: ImproveRequest):
    result = extract_tags(req.text)
    return TagsResponse(tags=result)


@router.post("/{audio_id}/chat", response_model=ChatResponse)
def chat_endpoint(audio_id: uuid.UUID, req: ChatRequest, db: Session = Depends(get_db)):
    audio = get_audio(db, audio_id)
    if not audio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio not found")
    if not audio.transcription_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not yet transcribed")

    answer = chat_with_transcription(audio.transcription_text, req.question)
    return ChatResponse(answer=answer)
