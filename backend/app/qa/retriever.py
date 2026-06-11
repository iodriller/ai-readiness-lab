"""Context retriever for the Q&A composer.

Assembles everything the composer needs from the project's stored state:
the company profile, peer classifications, competitive signals, the resolved
opportunity cards, and any prior Q&A answers in this project session.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.db.models import ProjectRow
from app.models.company import CompanyIntelligenceProfile
from app.models.competitive import CompetitiveSignal
from app.models.opportunity import OpportunityCard
from app.opportunity.scorer import score_opportunities


@dataclass
class QAContext:
    company_name: str
    profile: CompanyIntelligenceProfile | None
    signals: list[CompetitiveSignal]
    opportunity_cards: list[OpportunityCard]
    prior_answers: list[dict] = field(default_factory=list)


def gather_context(project_id: str, session: Session) -> QAContext | None:
    """Load everything needed for a Q&A response from the project's stored state."""
    row = session.get(ProjectRow, project_id)
    if row is None:
        return None

    company_name = row.company_name
    payload = row.payload

    profile: CompanyIntelligenceProfile | None = None
    if payload.get("profile"):
        try:
            profile = CompanyIntelligenceProfile.model_validate(payload["profile"])
        except Exception:
            pass

    signals: list[CompetitiveSignal] = []
    if profile and profile.competitive_ai_signals:
        signals = profile.competitive_ai_signals

    if profile:
        opportunity_cards = score_opportunities(profile, signals)
    else:
        # No profile yet — return all library cards as context (unfiltered).
        from app.models.company import CompanyIdentity
        from app.models.company import CompanyIntelligenceProfile as CIP

        placeholder = CIP(company_identity=CompanyIdentity(name=company_name))
        opportunity_cards = score_opportunities(placeholder)

    prior_answers: list[dict] = payload.get("qa_history", [])

    return QAContext(
        company_name=company_name,
        profile=profile,
        signals=signals,
        opportunity_cards=opportunity_cards,
        prior_answers=prior_answers,
    )
