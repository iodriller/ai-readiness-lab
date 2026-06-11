"""CompanyIntelligenceProfile — the structured research output (spec §8.1).

Numeric financial fields are nullable on purpose: when a figure is not isolated
in public sources, it stays `None` rather than being guessed (spec §3.2, no
hallucination). Use `financial_trend_summary` and `source_refs` to qualify.
"""

from pydantic import BaseModel, Field

from app.models.base import Confidence
from app.models.competitive import CompetitiveSignal


class CompanyIdentity(BaseModel):
    name: str
    ticker: str | None = None
    website: str | None = None
    headquarters: str | None = None
    company_type: str | None = None
    industry: str | None = None
    subindustries: list[str] = Field(default_factory=list)
    business_segments: list[str] = Field(default_factory=list)
    operating_regions: list[str] = Field(default_factory=list)
    confidence: Confidence = 0.0


class FinancialSnapshot(BaseModel):
    revenue_latest: float | None = None
    net_income_latest: float | None = None
    market_cap: float | None = None
    capex_latest: float | None = None
    financial_trend_summary: str = ""
    source_refs: list[str] = Field(default_factory=list)


class StrategicPriorities(BaseModel):
    themes: list[str] = Field(default_factory=list)
    earnings_call_signals: list[str] = Field(default_factory=list)
    investor_presentation_signals: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class AIDigitalSignals(BaseModel):
    company_ai_initiatives: list[str] = Field(default_factory=list)
    digital_transformation_signals: list[str] = Field(default_factory=list)
    automation_signals: list[str] = Field(default_factory=list)
    data_platform_signals: list[str] = Field(default_factory=list)
    job_posting_signals: list[str] = Field(default_factory=list)
    partnership_signals: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class PeerTaxonomy(BaseModel):
    direct_competitors: list[str] = Field(default_factory=list)
    operator_peers: list[str] = Field(default_factory=list)
    service_company_benchmarks: list[str] = Field(default_factory=list)
    technology_vendor_benchmarks: list[str] = Field(default_factory=list)
    adjacent_industry_benchmarks: list[str] = Field(default_factory=list)


class ProfileConfidence(BaseModel):
    overall: Confidence = 0.0
    company_identity: Confidence = 0.0
    financials: Confidence = 0.0
    peer_taxonomy: Confidence = 0.0
    ai_signals: Confidence = 0.0
    opportunity_hypotheses: Confidence = 0.0


class CompanyIntelligenceProfile(BaseModel):
    company_identity: CompanyIdentity
    financial_snapshot: FinancialSnapshot = Field(default_factory=FinancialSnapshot)
    strategic_priorities: StrategicPriorities = Field(default_factory=StrategicPriorities)
    ai_and_digital_signals: AIDigitalSignals = Field(default_factory=AIDigitalSignals)
    peer_taxonomy: PeerTaxonomy = Field(default_factory=PeerTaxonomy)
    competitive_ai_signals: list[CompetitiveSignal] = Field(default_factory=list)
    industry_ai_patterns: list[str] = Field(default_factory=list)
    opportunity_hypotheses: list[str] = Field(default_factory=list)
    confidence: ProfileConfidence = Field(default_factory=ProfileConfidence)
    sources: list[str] = Field(default_factory=list)
