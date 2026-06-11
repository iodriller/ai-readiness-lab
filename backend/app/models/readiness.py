"""ReadinessScorecard — pilot readiness score and explanation (spec §15.4, §9)."""

from pydantic import BaseModel, Field

from app.models.base import Recommendation, Score


class ReadinessDimensions(BaseModel):
    business_value: Score
    workflow_clarity: Score
    data_readiness: Score
    risk_controls: Score
    evaluation_readiness: Score
    integration_feasibility: Score
    operational_ownership: Score
    user_adoption: Score


class ReadinessScorecard(BaseModel):
    overall_score: Score
    recommendation: Recommendation
    dimensions: ReadinessDimensions
    blockers: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
