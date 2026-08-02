import uuid
from datetime import datetime
from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    id: uuid.UUID
    original_name: str
    file_size: int
    status: str
    message: str = "Audio uploaded successfully. Processing started."


class Segment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptionResponse(BaseModel):
    id: uuid.UUID
    text: str
    segments: list[Segment]
    language: str
    duration: float


class AudioStatusResponse(BaseModel):
    id: uuid.UUID
    original_name: str
    duration: float | None
    language: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    transcription_text: str | None
    transcription_segments: list[Segment] | None
    tags: list[str] | None
    tasks: list[dict] | None
    dates: list[str] | None
    emails: list[str] | None
    phones: list[str] | None
    links: list[str] | None
    summary_short: str | None
    summary_medium: str | None
    summary_detailed: str | None
    improved_text: str | None
    text_no_fillers: str | None


class ImproveRequest(BaseModel):
    text: str


class ImproveResponse(BaseModel):
    improved_text: str


class RemoveFillersResponse(BaseModel):
    cleaned_text: str


class SummarizeRequest(BaseModel):
    text: str
    level: str = "medium"


class SummarizeResponse(BaseModel):
    summary: str


class TasksResponse(BaseModel):
    tasks: list[dict]


class DatesResponse(BaseModel):
    dates: list[str]


class PhonesResponse(BaseModel):
    phones: list[str]


class EmailsResponse(BaseModel):
    emails: list[str]


class LinksResponse(BaseModel):
    links: list[str]


class TagsResponse(BaseModel):
    tags: list[str]


class ChatRequest(BaseModel):
    transcription_id: uuid.UUID
    question: str


class ChatResponse(BaseModel):
    answer: str
