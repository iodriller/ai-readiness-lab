"""Eval set for the peer classifier (spec §3.3). A wrong label is a correctness bug."""

from app.models.base import PeerType
from app.research.peer_classifier import classify_peer, classify_peers, to_taxonomy


# --- Oil & gas: the canonical spec example -------------------------------------
def test_oxy_vs_slb_is_service_company_not_competitor():
    c = classify_peer("Occidental Petroleum", "SLB")
    assert c.peer_type == PeerType.service_company
    assert c.peer_type != PeerType.direct_competitor
    assert "benchmark" in c.reason.lower()


def test_oxy_vs_oilfield_services_are_all_service_companies():
    for svc in ["Halliburton", "Baker Hughes", "NOV", "Weatherford"]:
        c = classify_peer("Occidental Petroleum", svc)
        assert c.peer_type == PeerType.service_company, svc


def test_oxy_vs_chevron_is_operator_peer():
    c = classify_peer("Occidental Petroleum", "Chevron")
    assert c.peer_type == PeerType.operator_peer


def test_oxy_vs_exxon_and_conoco_are_operator_peers():
    for op in ["ExxonMobil", "ConocoPhillips", "EOG", "Devon Energy"]:
        assert classify_peer("Oxy", op).peer_type == PeerType.operator_peer, op


# --- SaaS / CRM ----------------------------------------------------------------
def test_salesforce_vs_hubspot_is_direct_competitor():
    c = classify_peer("Salesforce", "HubSpot")
    assert c.peer_type == PeerType.direct_competitor


def test_salesforce_vs_aws_is_technology_vendor():
    c = classify_peer("Salesforce", "AWS")
    assert c.peer_type == PeerType.technology_vendor
    assert "competitor" not in c.peer_type.value


# --- Banking -------------------------------------------------------------------
def test_jpmorgan_vs_bofa_is_direct_competitor():
    c = classify_peer("JPMorgan", "Bank of America")
    assert c.peer_type == PeerType.direct_competitor


def test_jpmorgan_vs_stripe_is_technology_vendor():
    c = classify_peer("JPMorgan", "Stripe")
    assert c.peer_type == PeerType.technology_vendor


# --- Unknown company -----------------------------------------------------------
def test_unknown_company_defers_to_adjacent_benchmark_low_confidence():
    c = classify_peer("Occidental Petroleum", "Some Unlisted Startup")
    assert c.peer_type == PeerType.adjacent_benchmark
    assert c.confidence < 0.5
    assert c.reason


# --- Aggregation ---------------------------------------------------------------
def test_to_taxonomy_buckets_each_peer_type():
    classifications = classify_peers(
        "Occidental Petroleum", ["Chevron", "SLB", "AWS", "Some Unlisted Startup"]
    )
    tax = to_taxonomy(classifications)
    assert "Chevron" in tax.operator_peers
    assert "SLB" in tax.service_company_benchmarks
    assert "AWS" in tax.technology_vendor_benchmarks
    assert "Some Unlisted Startup" in tax.adjacent_industry_benchmarks
    # The service company is never surfaced as a direct competitor.
    assert "SLB" not in tax.direct_competitors
