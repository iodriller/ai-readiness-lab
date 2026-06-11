"""Tests for competitive-signal hygiene (peer-type reconciliation + relevance filter)."""

from app.models.base import Level, PeerType
from app.models.competitive import CompetitiveSignal
from app.research.competitive_signals import filter_relevant, reconcile_peer_types


def _signal(company, peer_type, confidence=0.8, source_ids=("s1",)):
    return CompetitiveSignal(
        company=company,
        peer_type=peer_type,
        signal="Announced an AI initiative",
        ai_area="operations",
        business_relevance="relevant",
        fomo_strength=Level.medium,
        source_ids=list(source_ids),
        confidence=confidence,
    )


def test_reconcile_overrides_misclassified_service_company():
    # The model wrongly called SLB a direct competitor of Oxy.
    signals = [_signal("SLB", PeerType.direct_competitor)]
    fixed = reconcile_peer_types("Occidental Petroleum", signals)
    assert fixed[0].peer_type == PeerType.service_company


def test_reconcile_leaves_unknown_company_label_untouched():
    signals = [_signal("Mystery Co", PeerType.direct_competitor)]
    fixed = reconcile_peer_types("Occidental Petroleum", signals)
    assert fixed[0].peer_type == PeerType.direct_competitor


def test_filter_drops_unsourced_signals():
    signals = [_signal("Chevron", PeerType.operator_peer, source_ids=())]
    assert filter_relevant(signals) == []


def test_filter_drops_low_confidence_signals():
    signals = [_signal("Chevron", PeerType.operator_peer, confidence=0.2)]
    assert filter_relevant(signals) == []


def test_filter_keeps_sourced_confident_signals():
    signals = [_signal("Chevron", PeerType.operator_peer, confidence=0.7)]
    assert len(filter_relevant(signals)) == 1
