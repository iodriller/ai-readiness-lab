"""Round-trip and validation tests for the domain schemas."""

import pytest
from pydantic import ValidationError

from app.models import (
    TOP_LEVEL_MODELS,
    CompanyIntelligenceProfile,
    CompetitiveSignal,
    OpportunityCard,
    Project,
    ReadinessScorecard,
    SourceRecord,
)
from app.models.base import Level, Mode, PeerType, Recommendation, TimeToPilot
from app.models.company import CompanyIdentity
from app.models.readiness import ReadinessDimensions


def _dimensions() -> ReadinessDimensions:
    return ReadinessDimensions(
        business_value=80,
        workflow_clarity=70,
        data_readiness=60,
        risk_controls=75,
        evaluation_readiness=65,
        integration_feasibility=70,
        operational_ownership=60,
        user_adoption=72,
    )


def test_project_defaults_are_populated():
    project = Project(company_name="Acme", user_role="CTO", mode=Mode.discover_opportunities)
    assert project.project_id  # uuid assigned
    assert project.status.value == "researching"
    assert project.created_at.tzinfo is not None


@pytest.mark.parametrize(
    "model, payload",
    [
        (
            SourceRecord,
            {"url": "https://x.com", "title": "T", "source_type": "official", "confidence": 0.9},
        ),
        (
            CompetitiveSignal,
            {
                "company": "SLB",
                "peer_type": PeerType.service_company.value,
                "signal": "AI drilling platform",
                "ai_area": "drilling",
                "business_relevance": "ecosystem signal, not a direct operator competitor",
                "fomo_strength": Level.medium.value,
                "confidence": 0.7,
            },
        ),
        (
            OpportunityCard,
            {
                "name": "Field Engineer Assistant",
                "category": "knowledge",
                "executive_summary": "s",
                "why_now": "w",
                "competitive_pressure": "p",
                "business_value": Level.high.value,
                "pilot_feasibility": Level.medium.value,
                "risk_level": Level.low.value,
                "time_to_pilot": TimeToPilot.d60.value,
                "recommended_first_step": "scope data",
                "technical_depth_required": Level.medium.value,
            },
        ),
        (
            CompanyIntelligenceProfile,
            {"company_identity": {"name": "Occidental Petroleum"}},
        ),
        (
            ReadinessScorecard,
            {
                "overall_score": 71,
                "recommendation": Recommendation.limited_pilot.value,
                "dimensions": _dimensions().model_dump(),
            },
        ),
    ],
)
def test_model_json_round_trip(model, payload):
    instance = model.model_validate(payload)
    assert model.model_validate_json(instance.model_dump_json()) == instance


def test_confidence_must_be_within_bounds():
    with pytest.raises(ValidationError):
        SourceRecord(url="u", title="t", source_type="news", confidence=1.5)


def test_score_must_be_within_bounds():
    fields = _dimensions().model_dump()
    fields["business_value"] = 120
    with pytest.raises(ValidationError):
        ReadinessDimensions(**fields)


def test_unlabeled_peer_type_is_rejected():
    with pytest.raises(ValidationError):
        CompetitiveSignal(
            company="X",
            peer_type="frenemy",
            signal="s",
            ai_area="a",
            business_relevance="r",
            fomo_strength="high",
            confidence=0.5,
        )


def test_financials_default_to_none_not_guesses():
    profile = CompanyIntelligenceProfile(company_identity=CompanyIdentity(name="Acme"))
    assert profile.financial_snapshot.revenue_latest is None
    assert profile.financial_snapshot.market_cap is None


def test_all_top_level_models_are_exported():
    assert len(TOP_LEVEL_MODELS) == 8
