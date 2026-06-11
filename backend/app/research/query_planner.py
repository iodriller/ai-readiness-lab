"""Search query templates per research step (spec §7.3)."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.base import Mode


@dataclass
class QuerySet:
    identity: list[str] = field(default_factory=list)
    financial: list[str] = field(default_factory=list)
    strategic: list[str] = field(default_factory=list)
    competitors: list[str] = field(default_factory=list)
    competitor_ai: list[str] = field(default_factory=list)
    industry_ai: list[str] = field(default_factory=list)
    company_ai: list[str] = field(default_factory=list)

    def all_queries(self) -> list[str]:
        return (
            self.identity
            + self.financial
            + self.strategic
            + self.competitors
            + self.competitor_ai
            + self.industry_ai
            + self.company_ai
        )


def plan_queries(company_name: str, mode: Mode) -> QuerySet:
    n = company_name
    qs = QuerySet(
        identity=[f"{n} company overview headquarters industry employees"],
        financial=[f"{n} annual revenue financial results 2024 2025"],
        strategic=[f"{n} strategy priorities CEO earnings call investor presentation 2024"],
        competitors=[f"{n} competitors market share competitive landscape"],
        competitor_ai=[f"{n} competitors AI machine learning digital transformation 2024"],
        industry_ai=[f"{n} industry sector AI technology adoption trends 2025"],
        company_ai=[f"{n} artificial intelligence machine learning initiative announcement"],
    )
    if mode == Mode.evaluate_idea:
        qs.company_ai.append(f"{n} technology implementation pilot program ROI")
        qs.industry_ai.append(f"{n} sector automation efficiency case study")
    elif mode == Mode.strategy_question:
        qs.competitors.append(f"{n} competitive advantage strategic positioning")
        qs.industry_ai.append(f"{n} industry digital transformation maturity benchmark")
    elif mode == Mode.compare_competitors:
        qs.competitor_ai.extend(
            [
                f"{n} competitor AI investment spending 2024 2025",
                f"{n} peer comparison AI readiness digital maturity",
            ]
        )
    return qs
