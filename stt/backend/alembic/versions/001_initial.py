"""initial

Revision ID: 001
Revises:
Create Date: 2025-01-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audios",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("original_name", sa.String(512), nullable=False),
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("file_size", sa.Integer, nullable=False, default=0),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("status", sa.Enum("pending", "processing", "completed", "failed", name="audiostatus"), nullable=False, default="pending"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("transcription_text", sa.Text, nullable=True),
        sa.Column("transcription_segments", JSONB, nullable=True),
        sa.Column("summary_short", sa.Text, nullable=True),
        sa.Column("summary_medium", sa.Text, nullable=True),
        sa.Column("summary_detailed", sa.Text, nullable=True),
        sa.Column("improved_text", sa.Text, nullable=True),
        sa.Column("text_no_fillers", sa.Text, nullable=True),
        sa.Column("tags", JSONB, nullable=True, server_default="[]"),
        sa.Column("tasks", JSONB, nullable=True, server_default="[]"),
        sa.Column("dates", JSONB, nullable=True, server_default="[]"),
        sa.Column("emails", JSONB, nullable=True, server_default="[]"),
        sa.Column("phones", JSONB, nullable=True, server_default="[]"),
        sa.Column("links", JSONB, nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audios")
    op.execute("DROP TYPE IF EXISTS audiostatus")
