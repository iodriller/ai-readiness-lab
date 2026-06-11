"""Tests for the opportunity library, scorer, and ranker (Phase 5)."""

from app.models.base import Level, PeerType
from app.models.company import (
    AIDigitalSignals,
    CompanyIdentity,
    CompanyIntelligenceProfile,
    StrategicPriorities,
)
from app.models.competitive import CompetitiveSignal
from app.opportunity.library import load_library
from app.opportunity.scorer import score_opportunities


def _profile(**ai):
    return CompanyIntelligenceProfile(
        company_identity=CompanyIdentity(name="Acme", industry="oil_gas"),
        ai_and_digital_signals=AIDigitalSignals(**ai),
        strategic_priorities=StrategicPriorities(themes=["operations efficiency"]),
    )


def test_library_loads_with_expected_shape():
    lib = load_library()
    assert len(lib) >= 10
    assert all(uc.keywords for uc in lib)
    assert all(uc.name and uc.category for uc in lib)


def test_returns_between_five_and_ten_cards():
    cards = score_opportunities(_profile(), [])
    assert 5 <= len(cards) <= 10


def test_profile_keywords_pull_relevant_cards_to_the_top():
    # A maintenance-heavy profile should rank the predictive-maintenance card highly.
    profile = _profile(automation_signals=["predictive maintenance on equipment"])
    cards = score_opportunities(profile, [])
    top_names = [c.name for c in cards[:3]]
    assert any("Maintenance" in n for n in top_names)


def test_competitive_pressure_names_a_peer_only_when_a_signal_backs_it():
    profile = _profile(company_ai_initiatives=["document assistant rollout"])
    signal = CompetitiveSignal(
        company="Chevron",
        peer_type=PeerType.operator_peer,
        signal="Chevron launched a document assistant",
        ai_area="document knowledge assistant",
        business_relevance="same workflow",
        fomo_strength=Level.high,
        source_ids=["s1"],
        confidence=0.8,
    )
    cards = score_opportunities(profile, [signal])
    backed = [c for c in cards if "Chevron" in c.competitive_pressure]
    assert backed, "a card matching the signal should cite the peer"


def test_no_card_invents_peer_pressure_without_a_signal():
    # With zero signals, no card may name a peer in its competitive_pressure text.
    cards = score_opportunities(_profile(), [])
    knowns = ["Chevron", "SLB", "Halliburton", "Salesforce", "Stripe", "AWS"]
    for card in cards:
        assert not any(name in card.competitive_pressure for name in knowns)


def test_cards_carry_valid_enum_fields():
    cards = score_opportunities(_profile(), [])
    for c in cards:
        assert c.business_value in Level
        assert c.risk_level in Level
        assert c.recommended_first_step
