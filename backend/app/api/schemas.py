"""Request/response schemas for the executive-shell API (Phase 2)."""

from pydantic import BaseModel, Field

from app.models.base import Mode
from app.models.opportunity import OpportunityCard


class CreateProjectRequest(BaseModel):
    company_name: str = Field(min_length=1)
    user_role: str = Field(min_length=1)
    mode: Mode


class BriefSource(BaseModel):
    """A credibility-tagged public source backing the brief (the Evidence panel)."""

    url: str
    title: str = ""
    source_type: str
    confidence: float


class BriefResponse(BaseModel):
    """Executive AI Readiness Brief (spec §4.4).

    Phase 2 serves illustrative sample content so the shell is fully navigable;
    real research replaces it in Phase 3. Text is framed as illustrative and
    makes no factual claims about the company.
    """

    company_name: str
    is_sample: bool
    what_matters: str
    competitive_pressure: str
    the_opening: str
    recommended_next_move: str
    opportunities: list[OpportunityCard]
    sources: list[BriefSource] = Field(default_factory=list)
