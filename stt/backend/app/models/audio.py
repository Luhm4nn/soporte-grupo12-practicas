import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

import enum


class AudioStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Audio(Base):
    __tablename__ = "audios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_name: Mapped[str] = mapped_column(String(512), nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(AudioStatus, values_callable=lambda e: [m.value for m in e]),
        default=AudioStatus.PENDING,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    transcription_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcription_segments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    summary_short: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_medium: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_detailed: Mapped[str | None] = mapped_column(Text, nullable=True)
    improved_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_no_fillers: Mapped[str | None] = mapped_column(Text, nullable=True)

    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    tasks: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    dates: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    emails: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    phones: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    links: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
