"""Project and research-plan schemas (spec §15.1, §15.2)."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.base import Mode, ProjectStatus


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(BaseModel):
    project_id: str = Field(default_factory=lambda: uuid4().hex)
    company_name: str
    user_role: str
    mode: Mode
    created_at: datetime = Field(default_factory=_utcnow)
    status: ProjectStatus = ProjectStatus.researching


class SourceRequirements(BaseModel):
    min_official_sources: int = 2
    min_competitor_sources: int = 3
    min_industry_sources: int = 3


class CompanyResearchPlan(BaseModel):
    company_name: str
    known_ticker: str | None = None
    research_tasks: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    source_requirements: SourceRequirements = Field(default_factory=SourceRequirements)
