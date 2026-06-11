"""CompetitiveSignal — one source-backed competitor/peer AI signal (spec §8.2).

Every signal carries its `peer_type`; an unlabeled or mislabeled signal is a
correctness bug, not a style nit (spec §3.3).
"""

from pydantic import BaseModel, Field

from app.models.base import Confidence, Level, PeerType


class CompetitiveSignal(BaseModel):
    company: str
    peer_type: PeerType
    signal: str
    ai_area: str
    business_relevance: str
    fomo_strength: Level
    source_ids: list[str] = Field(default_factory=list)
    confidence: Confidence


class PeerClassification(BaseModel):
    """A subject↔peer relationship with a stated, reviewable reason (spec §3.3).

    The `reason` is mandatory: a label without an explanation is what makes bad
    comparisons hard to catch. A wrong `peer_type` is a correctness bug.
    """

    company: str
    peer_type: PeerType
    reason: str
    confidence: Confidence = 0.0
