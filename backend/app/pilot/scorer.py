"""Deterministic pilot readiness scoring (spec §9).

Rubrics are code, not vibes: identical inputs always yield identical scores. Each
of the eight dimensions is derived from the selected opportunity card plus the
executive's drill-down answers, with an explicit reason so the scorecard explains
*why* it scored as it did. No LLM, so it works offline and in sample mode.
"""

from __future__ import annotations

from app.models.base import Level, Recommendation
from app.models.opportunity import OpportunityCard
from app.models.readiness import ReadinessDimensions, ReadinessScorecard
from app.pilot.questions import QUESTIONS

_MEASURABLE_HINTS = ("%", "percent", "hours", "hour", "reduce", "save", "faster", "cost", "$", "x ")
_PLATFORMS = (
    "sharepoint",
    "box",
    "s3",
    "aws",
    "azure",
    "gcp",
    "snowflake",
    "databricks",
    "on-prem",
)


def _substantive(text: str) -> bool:
    """A real answer, not a blank or one-word placeholder."""
    return len(text.strip()) >= 15


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _measurable(text: str) -> bool:
    lower = text.lower()
    return any(hint in lower for hint in _MEASURABLE_HINTS)


def _named_platform(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in _PLATFORMS)


def _dimensions(card: OpportunityCard, answers: dict[str, str]) -> dict[str, int]:
    def ans(key: str) -> str:
        return answers.get(key, "")

    value_base = {Level.low: 45, Level.medium: 70, Level.high: 90}[card.business_value]
    feasibility_base = {Level.low: 40, Level.medium: 65, Level.high: 85}[card.pilot_feasibility]
    risk_base = {Level.low: 75, Level.medium: 55, Level.high: 35}[card.risk_level]
    adoption_base = {Level.low: 85, Level.medium: 65, Level.high: 45}[card.technical_depth_required]

    return {
        "business_value": _clamp(value_base + (10 if _substantive(ans("success_outcome")) else 0)),
        "workflow_clarity": _clamp(
            30
            + (35 if _substantive(ans("workflow")) else 0)
            + (20 if _substantive(ans("users")) else 0)
            + (15 if _substantive(ans("never_do")) else 0)
        ),
        "data_readiness": _clamp(
            25
            + (45 if _substantive(ans("data_sources")) else 0)
            + (20 if _named_platform(ans("data_sources")) else 0)
        ),
        "risk_controls": _clamp(
            risk_base
            + (15 if _substantive(ans("never_do")) else 0)
            + (10 if _substantive(ans("unacceptable_risk")) else 0)
        ),
        "evaluation_readiness": _clamp(
            30
            + (40 if _substantive(ans("success_outcome")) else 0)
            + (20 if _measurable(ans("success_outcome")) else 0)
        ),
        "integration_feasibility": _clamp(
            feasibility_base + (10 if _named_platform(ans("data_sources")) else 0)
        ),
        "operational_ownership": _clamp(
            25
            + (50 if _substantive(ans("approver")) else 0)
            + (15 if _substantive(ans("users")) else 0)
        ),
        "user_adoption": _clamp(adoption_base + (10 if _substantive(ans("users")) else 0)),
    }


_LABELS = {
    "business_value": "business value",
    "workflow_clarity": "workflow clarity",
    "data_readiness": "data readiness",
    "risk_controls": "risk controls",
    "evaluation_readiness": "evaluation readiness",
    "integration_feasibility": "integration feasibility",
    "operational_ownership": "operational ownership",
    "user_adoption": "user adoption",
}


def _recommendation(overall: int, blockers: list[str]) -> Recommendation:
    if overall >= 80 and not blockers:
        return Recommendation.proceed
    if overall >= 65:
        return Recommendation.limited_pilot
    if overall >= 50:
        return Recommendation.needs_discovery
    if overall >= 35:
        return Recommendation.defer
    return Recommendation.not_recommended


def score_pilot(card: OpportunityCard, answers: dict[str, str]) -> ReadinessScorecard:
    dims = _dimensions(card, answers)
    overall = round(sum(dims.values()) / len(dims))

    blockers = [f"Low {_LABELS[k]} ({v}/100)" for k, v in dims.items() if v < 50]
    strengths = [f"Strong {_LABELS[k]} ({v}/100)" for k, v in dims.items() if v >= 80]

    next_actions = [
        f'Clarify: "{q.prompt}"' for q in QUESTIONS if not _substantive(answers.get(q.id, ""))
    ]
    # A weak dimension that the questions can't fix on their own gets a concrete action.
    if dims["data_readiness"] < 60:
        next_actions.append("Inventory the source systems and confirm access before building.")
    if dims["evaluation_readiness"] < 60:
        next_actions.append("Define a measurable success metric and an evaluation threshold.")

    return ReadinessScorecard(
        overall_score=overall,
        recommendation=_recommendation(overall, blockers),
        dimensions=ReadinessDimensions(**dims),
        blockers=blockers,
        strengths=strengths,
        next_actions=next_actions,
    )
