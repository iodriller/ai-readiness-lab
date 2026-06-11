"""Shared enums and value types used across the domain schemas.

`source_refs` / `source_ids` everywhere hold `SourceRecord.source_id` values —
that is the single citation convention for the whole system.
"""

from enum import Enum
from typing import Annotated

from pydantic import Field

# A normalized model/research confidence in [0, 1].
Confidence = Annotated[float, Field(ge=0.0, le=1.0)]

# A 0-100 readiness/score value.
Score = Annotated[int, Field(ge=0, le=100)]


class Level(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Mode(str, Enum):
    discover_opportunities = "discover_opportunities"
    evaluate_idea = "evaluate_idea"
    strategy_question = "strategy_question"
    compare_competitors = "compare_competitors"


class ProjectStatus(str, Enum):
    researching = "researching"
    ready = "ready"
    report_generated = "report_generated"


class SourceType(str, Enum):
    official = "official"
    filing = "filing"
    news = "news"
    analyst = "analyst"
    vendor = "vendor"
    blog = "blog"
    academic = "academic"
    job_posting = "job_posting"


class PeerType(str, Enum):
    """Peer classification. Mislabeling a peer is a correctness bug (spec §3.3)."""

    direct_competitor = "direct_competitor"
    operator_peer = "operator_peer"
    service_company = "service_company"
    technology_vendor = "technology_vendor"
    supplier = "supplier"
    customer = "customer"
    adjacent_benchmark = "adjacent_benchmark"


class Recommendation(str, Enum):
    proceed = "proceed"
    limited_pilot = "limited_pilot"
    needs_discovery = "needs_discovery"
    defer = "defer"
    not_recommended = "not_recommended"


class TimeToPilot(str, Enum):
    d30 = "30_days"
    d60 = "60_days"
    d90 = "90_days"
    longer = "longer"
