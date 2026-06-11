"""Peer taxonomy classifier (spec §3.3).

Distinguishing a *direct competitor* from a *service company* or *technology
vendor* is the credibility differentiator: a service company surfaced as a direct
operator competitor is a correctness bug, not a style nit.

The classifier is rule-based over a curated set of well-known companies plus their
business *role*. Given a subject and a candidate it returns a `PeerClassification`
with a stated reason. Unknown companies fall back to a low-confidence
`adjacent_benchmark` so the caller can defer to source-based judgment rather than
guess a direct-competitor label.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.base import PeerType
from app.models.company import PeerTaxonomy
from app.models.competitive import PeerClassification


@dataclass(frozen=True)
class _Role:
    industry: str
    role: str  # operator | service_company | technology_vendor | software_vendor | bank


# Curated reference set. Roles drive classification; expand as eval coverage grows.
_KNOWN: dict[str, _Role] = {
    # Oil & gas operators / producers
    "occidental petroleum": _Role("oil_gas", "operator"),
    "occidental": _Role("oil_gas", "operator"),
    "oxy": _Role("oil_gas", "operator"),
    "chevron": _Role("oil_gas", "operator"),
    "exxonmobil": _Role("oil_gas", "operator"),
    "exxon": _Role("oil_gas", "operator"),
    "conocophillips": _Role("oil_gas", "operator"),
    "eog resources": _Role("oil_gas", "operator"),
    "eog": _Role("oil_gas", "operator"),
    "devon energy": _Role("oil_gas", "operator"),
    "devon": _Role("oil_gas", "operator"),
    "shell": _Role("oil_gas", "operator"),
    "bp": _Role("oil_gas", "operator"),
    "totalenergies": _Role("oil_gas", "operator"),
    # Oilfield services & technology (NOT operator competitors)
    "slb": _Role("oil_gas", "service_company"),
    "schlumberger": _Role("oil_gas", "service_company"),
    "halliburton": _Role("oil_gas", "service_company"),
    "baker hughes": _Role("oil_gas", "service_company"),
    "nov": _Role("oil_gas", "service_company"),
    "weatherford": _Role("oil_gas", "service_company"),
    # SaaS / CRM software vendors
    "salesforce": _Role("crm_software", "software_vendor"),
    "hubspot": _Role("crm_software", "software_vendor"),
    "zoho": _Role("crm_software", "software_vendor"),
    "microsoft dynamics": _Role("crm_software", "software_vendor"),
    # Cloud / AI infrastructure technology vendors
    "amazon web services": _Role("cloud_infra", "technology_vendor"),
    "aws": _Role("cloud_infra", "technology_vendor"),
    "microsoft azure": _Role("cloud_infra", "technology_vendor"),
    "google cloud": _Role("cloud_infra", "technology_vendor"),
    "snowflake": _Role("cloud_infra", "technology_vendor"),
    "databricks": _Role("cloud_infra", "technology_vendor"),
    # Banks
    "jpmorgan chase": _Role("banking", "bank"),
    "jpmorgan": _Role("banking", "bank"),
    "bank of america": _Role("banking", "bank"),
    "wells fargo": _Role("banking", "bank"),
    "citigroup": _Role("banking", "bank"),
    "citi": _Role("banking", "bank"),
    # Fintech / payments technology vendors (not direct bank competitors)
    "stripe": _Role("fintech", "technology_vendor"),
    "paypal": _Role("fintech", "technology_vendor"),
    "block": _Role("fintech", "technology_vendor"),
    "square": _Role("fintech", "technology_vendor"),
}

# How a candidate's role maps to a peer_type when it differs from the subject's.
_ROLE_TO_PEER: dict[str, PeerType] = {
    "service_company": PeerType.service_company,
    "technology_vendor": PeerType.technology_vendor,
    "software_vendor": PeerType.technology_vendor,
    "operator": PeerType.operator_peer,
    "bank": PeerType.operator_peer,
}

# Roles where two same-role, same-industry companies are direct product-market rivals.
_DIRECT_RIVAL_ROLES = {"software_vendor", "bank"}


def _lookup(name: str) -> _Role | None:
    return _KNOWN.get(name.strip().lower())


def classify_peer(subject: str, candidate: str) -> PeerClassification:
    """Classify `candidate` relative to `subject` with a stated reason."""
    s_role = _lookup(subject)
    c_role = _lookup(candidate)

    if s_role is None or c_role is None:
        return PeerClassification(
            company=candidate,
            peer_type=PeerType.adjacent_benchmark,
            reason=(
                f"{candidate} is not in the curated peer set; classify from sources "
                "before treating it as a direct competitor."
            ),
            confidence=0.3,
        )

    same_industry = s_role.industry == c_role.industry

    if same_industry and s_role.role == c_role.role:
        if c_role.role in _DIRECT_RIVAL_ROLES:
            return PeerClassification(
                company=candidate,
                peer_type=PeerType.direct_competitor,
                reason=f"{candidate} competes in the same product market as {subject}.",
                confidence=0.9,
            )
        return PeerClassification(
            company=candidate,
            peer_type=PeerType.operator_peer,
            reason=f"{candidate} is a same-industry operator peer of {subject}.",
            confidence=0.9,
        )

    peer_type = _ROLE_TO_PEER.get(c_role.role, PeerType.adjacent_benchmark)
    if peer_type in (PeerType.service_company, PeerType.technology_vendor):
        reason = (
            f"{candidate} is a {c_role.role.replace('_', ' ')}; its AI activity is an "
            f"ecosystem benchmark, not a direct competitor to {subject}."
        )
        confidence = 0.85
    else:
        reason = f"{candidate} operates in {c_role.industry}, adjacent to {subject}."
        confidence = 0.5
        peer_type = PeerType.adjacent_benchmark

    return PeerClassification(
        company=candidate, peer_type=peer_type, reason=reason, confidence=confidence
    )


def classify_peers(subject: str, candidates: list[str]) -> list[PeerClassification]:
    return [classify_peer(subject, c) for c in candidates]


def to_taxonomy(classifications: list[PeerClassification]) -> PeerTaxonomy:
    """Group classifications into the profile's PeerTaxonomy buckets."""
    tax = PeerTaxonomy()
    for c in classifications:
        if c.peer_type == PeerType.direct_competitor:
            tax.direct_competitors.append(c.company)
        elif c.peer_type == PeerType.operator_peer:
            tax.operator_peers.append(c.company)
        elif c.peer_type == PeerType.service_company:
            tax.service_company_benchmarks.append(c.company)
        elif c.peer_type == PeerType.technology_vendor:
            tax.technology_vendor_benchmarks.append(c.company)
        else:
            tax.adjacent_industry_benchmarks.append(c.company)
    return tax
