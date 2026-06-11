"""SourceRecord — a single retrieved, ranked source (spec §15.3)."""

from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.base import Confidence, SourceType


class SourceRecord(BaseModel):
    source_id: str = Field(default_factory=lambda: uuid4().hex)
    url: str
    title: str
    publisher: str | None = None
    published_date: str | None = None
    source_type: SourceType
    confidence: Confidence
    claims_extracted: list[str] = Field(default_factory=list)
