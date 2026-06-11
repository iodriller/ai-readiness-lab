"""Opportunity scoring & ranking (spec §6, §8.3).

Maps a `CompanyIntelligenceProfile` (+ vetted competitive signals) onto the
opportunity library and returns 5–10 ranked `OpportunityCard`s.

No-hallucination guard: a card's `competitive_pressure` only names a peer when a
real `CompetitiveSignal` backs it (`_pressure_text`). With no matching signal the
text is generic and makes no peer claim — so a card never implies competitive
activity it cannot cite.
"""

from __future__ import annotations

from app.models.base import Level
from app.models.company import CompanyIntelligenceProfile
from app.models.competitive import CompetitiveSignal
from app.models.opportunity import OpportunityCard
from app.opportunity.library import UseCase, load_library

_LEVEL_SCORE = {Level.low: 1, Level.medium: 2, Level.high: 3}
_RISK_BONUS = {Level.low: 2, Level.medium: 1, Level.high: 0}

_MIN_CARDS = 5
_MAX_CARDS = 10


def _profile_corpus(profile: CompanyIntelligenceProfile) -> str:
    ident = profile.company_identity
    ai = profile.ai_and_digital_signals
    parts: list[str] = [
        ident.industry or "",
        *ident.subindustries,
        *ident.business_segments,
        *profile.strategic_priorities.themes,
        *ai.company_ai_initiatives,
        *ai.digital_transformation_signals,
        *ai.automation_signals,
        *ai.data_platform_signals,
        *profile.opportunity_hypotheses,
        *profile.industry_ai_patterns,
    ]
    return " ".join(parts).lower()


def _fit_score(use_case: UseCase, corpus: str) -> int:
    return sum(1 for kw in use_case.keywords if kw in corpus)


def _matching_signal(
    use_case: UseCase, signals: list[CompetitiveSignal]
) -> CompetitiveSignal | None:
    for sig in signals:
        haystack = f"{sig.ai_area} {sig.signal} {sig.business_relevance}".lower()
        if any(kw in haystack for kw in use_case.keywords):
            return sig
    return None


def _pressure_text(use_case: UseCase, signal: CompetitiveSignal | None) -> str:
    if signal is None:
        # No backing signal → make no peer claim.
        return "A practical, broadly adopted starting point; no specific peer signal found here."
    return (
        f"{signal.company} ({signal.peer_type.value.replace('_', ' ')}) is signaling activity "
        f"in {signal.ai_area} — relevant competitive pressure for this opportunity."
    )


def _rank(use_case: UseCase, fit: int, has_signal: bool) -> int:
    return (
        fit * 3
        + _LEVEL_SCORE[use_case.business_value] * 2
        + _LEVEL_SCORE[use_case.pilot_feasibility] * 2
        + _RISK_BONUS[use_case.risk_level]
        + (2 if has_signal else 0)
    )


def score_opportunities(
    profile: CompanyIntelligenceProfile,
    signals: list[CompetitiveSignal] | None = None,
) -> list[OpportunityCard]:
    """Return 5–10 ranked opportunity cards grounded in the profile and signals."""
    signals = signals or []
    corpus = _profile_corpus(profile)

    scored: list[tuple[int, int, OpportunityCard]] = []
    for use_case in load_library():
        fit = _fit_score(use_case, corpus)
        signal = _matching_signal(use_case, signals)
        rank = _rank(use_case, fit, signal is not None)
        card = OpportunityCard(
            name=use_case.name,
            category=use_case.category,
            executive_summary=use_case.executive_summary,
            why_now=use_case.why_now,
            competitive_pressure=_pressure_text(use_case, signal),
            business_value=use_case.business_value,
            pilot_feasibility=use_case.pilot_feasibility,
            risk_level=use_case.risk_level,
            time_to_pilot=use_case.time_to_pilot,
            recommended_first_step=use_case.first_step,
            technical_depth_required=use_case.technical_depth_required,
        )
        scored.append((rank, fit, card))

    scored.sort(key=lambda t: t[0], reverse=True)

    # Prefer cards with a profile fit; backfill with the highest-ranked remainder
    # so we always return at least _MIN_CARDS.
    fitted = [c for rank, fit, c in scored if fit > 0]
    if len(fitted) >= _MIN_CARDS:
        return fitted[:_MAX_CARDS]
    backfill = [c for rank, fit, c in scored if fit == 0]
    return (fitted + backfill)[:_MIN_CARDS]
