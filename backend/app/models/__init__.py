"""Domain contracts for AI Readiness Lab (spec §8 and §15).

These Pydantic models are the single source of truth for the API, the database
payloads, and the generated frontend TypeScript types.
"""

from app.models.base import (
    Confidence,
    Level,
    Mode,
    PeerType,
    ProjectStatus,
    Recommendation,
    Score,
    SourceType,
    TimeToPilot,
)
from app.models.company import CompanyIntelligenceProfile
from app.models.competitive import CompetitiveSignal, PeerClassification
from app.models.opportunity import OpportunityCard
from app.models.project import CompanyResearchPlan, Project, SourceRequirements
from app.models.readiness import ReadinessDimensions, ReadinessScorecard
from app.models.source import SourceRecord

# Top-level models that round-trip through persistence and the frontend.
TOP_LEVEL_MODELS = [
    Project,
    CompanyResearchPlan,
    SourceRecord,
    CompanyIntelligenceProfile,
    CompetitiveSignal,
    PeerClassification,
    OpportunityCard,
    ReadinessScorecard,
]

__all__ = [
    "Confidence",
    "Level",
    "Mode",
    "PeerType",
    "ProjectStatus",
    "Recommendation",
    "Score",
    "SourceType",
    "TimeToPilot",
    "CompanyIntelligenceProfile",
    "CompetitiveSignal",
    "PeerClassification",
    "OpportunityCard",
    "CompanyResearchPlan",
    "Project",
    "SourceRequirements",
    "ReadinessDimensions",
    "ReadinessScorecard",
    "SourceRecord",
    "TOP_LEVEL_MODELS",
]
