"""Generate BriefResponse from CompanyIntelligenceProfile via LLM.

Falls back to sample_brief() if LLM generation fails, so the caller always
gets a valid response.
"""

from __future__ import annotations

import logging

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse
from app.llm.client import AnthropicClient
from app.llm.repair import parse_with_repair
from app.models.company import CompanyIntelligenceProfile

log = logging.getLogger(__name__)

_PROMPT = """Generate an executive AI readiness brief using the company profile below.
Use ONLY information from the profile. Do not invent companies, facts, or figures.

Company: {company_name}
Profile:
{profile_json}

Return ONLY a valid JSON object with these exact fields:
{{
  "company_name": "{company_name}",
  "is_sample": false,
  "what_matters": "<2-3 sentences about strategic context most relevant to AI adoption>",
  "competitive_pressure": "<1-2 sentences on competitive AI dynamics, from provided signals only>",
  "the_opening": "<1-2 sentences on why now is the right moment for AI here>",
  "recommended_next_move": "<one specific, concrete first action>",
  "opportunities": [
    {{
      "name": "<short name>",
      "category": "<Knowledge & Decision Support | Operations & Automation"
      " | Customer & Commercial | Data & Analytics | Process Efficiency>",
      "executive_summary": "<2-3 sentences>",
      "why_now": "<why this is timely>",
      "competitive_pressure": "<what peers are doing in this area>",
      "business_value": "<low|medium|high>",
      "pilot_feasibility": "<low|medium|high>",
      "risk_level": "<low|medium|high>",
      "time_to_pilot": "<30_days|60_days|90_days|longer>",
      "recommended_first_step": "<specific first action>",
      "technical_depth_required": "<low|medium|high>"
    }}
  ]
}}

Include 2-4 opportunities grounded in the company's specific context.
Return ONLY the JSON, no markdown.""".strip()


def generate_brief(
    profile: CompanyIntelligenceProfile,
    llm: AnthropicClient,
) -> BriefResponse:
    company_name = profile.company_identity.name
    prompt = _PROMPT.format(
        company_name=company_name,
        profile_json=profile.model_dump_json(indent=2),
    )
    raw = llm.complete(prompt, max_tokens=4096)
    try:
        return parse_with_repair(raw, BriefResponse, llm.as_repair_fn())
    except Exception:
        log.warning(
            "Brief generation failed for %r; using sample brief",
            company_name,
            exc_info=True,
        )
        return sample_brief(company_name)
