"""Persistence tables.

Each row keeps queryable columns plus the full validated Pydantic payload as
JSON, so the domain schemas in `app.models` stay the single source of truth.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectRow(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String, primary_key=True)
    company_name: Mapped[str] = mapped_column(String, index=True)
    user_role: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict] = mapped_column(JSON)


class SourceRow(Base):
    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    url: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String, index=True)
    confidence: Mapped[float] = mapped_column()
    payload: Mapped[dict] = mapped_column(JSON)
