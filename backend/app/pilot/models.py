"""Guided pilot drill-down models (spec §11)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.readiness import ReadinessScorecard


class PilotQuestion(BaseModel):
    id: str
    prompt: str


class PilotQuestionsResponse(BaseModel):
    """The plain-English questions to ask after an opportunity is selected (§11.1)."""

    opportunity_name: str
    questions: list[PilotQuestion]


class PilotProfile(BaseModel):
    """A selected opportunity narrowed by the executive's answers."""

    opportunity_name: str
    answers: dict[str, str] = Field(default_factory=dict)


class TechnicalChecklistGroup(BaseModel):
    category: str
    items: list[str]


class PilotPlan(BaseModel):
    """The drill-down output: the profile, a readiness score, and the technical
    discovery checklist that bridges executive intent to technical execution (§11.2)."""

    profile: PilotProfile
    scorecard: ReadinessScorecard
    technical_checklist: list[TechnicalChecklistGroup]
