"""Illustrative sample brief content for Phase 2 (no real research yet).

The opportunities are generic enterprise AI pilots drawn from the spec's
opportunity library (§6); the narrative is explicitly illustrative and asserts
no facts about the company. Replaced by real research output in Phase 3.
"""

from app.api.schemas import BriefResponse
from app.models.base import Level, TimeToPilot
from app.models.opportunity import OpportunityCard

_SAMPLE_OPPORTUNITIES = [
    OpportunityCard(
        name="Enterprise Knowledge Assistant",
        category="Knowledge & Decision Support",
        executive_summary=(
            "A grounded assistant over internal documents so staff can find answers "
            "without hunting across systems."
        ),
        why_now="Retrieval-grounded assistants are a low-risk, high-frequency starting point.",
        competitive_pressure=(
            "Peers commonly begin enterprise AI here before higher-risk workflows."
        ),
        business_value=Level.high,
        pilot_feasibility=Level.high,
        risk_level=Level.low,
        time_to_pilot=TimeToPilot.d60,
        recommended_first_step="Pick one document corpus with a clear owner and known pain.",
        technical_depth_required=Level.medium,
    ),
    OpportunityCard(
        name="Field/Operations Troubleshooting Assistant",
        category="Agentic / Tool-Using Assistants",
        executive_summary=(
            "A read-only copilot that helps frontline staff resolve common issues using "
            "manuals, SOPs, and historical cases."
        ),
        why_now="High-frequency operational need with a clear value path and human oversight.",
        competitive_pressure=(
            "Operational decision-support is a visible direction across the sector."
        ),
        business_value=Level.high,
        pilot_feasibility=Level.medium,
        risk_level=Level.medium,
        time_to_pilot=TimeToPilot.d90,
        recommended_first_step="Scope one workflow where SOPs and case history already exist.",
        technical_depth_required=Level.medium,
    ),
    OpportunityCard(
        name="Document & Reporting Summarizer",
        category="Document & Reporting",
        executive_summary=(
            "Turn long reports, filings, and meeting notes into concise, reviewable summaries."
        ),
        why_now="Summarization is mature, easy to evaluate, and broadly useful.",
        competitive_pressure="A common, low-risk early win for knowledge-heavy organizations.",
        business_value=Level.medium,
        pilot_feasibility=Level.high,
        risk_level=Level.low,
        time_to_pilot=TimeToPilot.d30,
        recommended_first_step="Choose one recurring report type and define a good-summary rubric.",
        technical_depth_required=Level.low,
    ),
    OpportunityCard(
        name="Analytics Copilot",
        category="Analytics & Decision Intelligence",
        executive_summary=(
            "A copilot that explains dashboards, variances, and anomalies in plain language."
        ),
        why_now="Pairs well with existing BI and lowers the bar to self-serve insight.",
        competitive_pressure=(
            "Analytics copilots are a frequent next step after knowledge assistants."
        ),
        business_value=Level.medium,
        pilot_feasibility=Level.medium,
        risk_level=Level.medium,
        time_to_pilot=TimeToPilot.d90,
        recommended_first_step="Target one well-governed dataset with reliable definitions.",
        technical_depth_required=Level.high,
    ),
]


def sample_brief(company_name: str) -> BriefResponse:
    return BriefResponse(
        company_name=company_name,
        is_sample=True,
        what_matters=(
            f"This is an illustrative readiness brief for {company_name}. Once research is "
            "connected, this section will summarize the company's segments and the workflows "
            "where AI is most likely to help — each tied to a cited public source."
        ),
        competitive_pressure=(
            "This section will describe where correctly classified peers and adjacent "
            "benchmarks are publicly signaling AI investment, with confidence notes."
        ),
        the_opening=(
            "The stronger starting point is usually a targeted, high-value workflow where data "
            "already exists, users feel pain, and human approval stays in control — not a broad "
            "enterprise chatbot."
        ),
        recommended_next_move=(
            "Select one practical pilot below and scope it with data requirements, tool "
            "boundaries, risk controls, and evaluation criteria."
        ),
        opportunities=_SAMPLE_OPPORTUNITIES,
    )
