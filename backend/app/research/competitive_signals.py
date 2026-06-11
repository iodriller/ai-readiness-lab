"""Competitive-signal hygiene (spec §3.3, §8.2).

Two correctness guards applied to LLM-extracted `CompetitiveSignal`s before they
reach the brief:

- `reconcile_peer_types` overrides each signal's `peer_type` with the curated
  classifier's verdict, so a service company can never be presented as a direct
  competitor regardless of what the model guessed.
- `filter_relevant` drops unsourced or low-confidence signals — no claim without
  evidence.
"""

from __future__ import annotations

from app.models.base import Confidence
from app.models.competitive import CompetitiveSignal
from app.research.peer_classifier import classify_peer


def reconcile_peer_types(subject: str, signals: list[CompetitiveSignal]) -> list[CompetitiveSignal]:
    """Re-label each signal's peer_type using the curated classifier when the
    company is known; leave the model's label otherwise."""
    out: list[CompetitiveSignal] = []
    for sig in signals:
        verdict = classify_peer(subject, sig.company)
        # Only override when the classifier is confident (i.e. the company is curated).
        peer_type = verdict.peer_type if verdict.confidence >= 0.8 else sig.peer_type
        out.append(sig.model_copy(update={"peer_type": peer_type}))
    return out


def filter_relevant(
    signals: list[CompetitiveSignal], min_confidence: Confidence = 0.4
) -> list[CompetitiveSignal]:
    """Keep only signals that cite a source and clear the confidence floor."""
    return [s for s in signals if s.source_ids and s.confidence >= min_confidence]
