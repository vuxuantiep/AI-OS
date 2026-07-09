from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


def _new_id() -> str:
    return uuid4().hex


def _now() -> datetime:
    return datetime.now(UTC)


class DocumentMeta(BaseModel):
    id: str = Field(default_factory=_new_id)
    filename: str
    media_type: str = "text/plain"
    num_chunks: int = 0
    created_at: datetime = Field(default_factory=_now)


class ChunkRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    document_id: str
    index: int
    text: str
    embedding: list[float] = Field(default_factory=list)
