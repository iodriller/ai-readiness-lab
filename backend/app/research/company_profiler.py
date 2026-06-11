"""Extract CompanyIntelligenceProfile from search results via LLM (spec §8.1).

Only information explicitly present in the sources is used — the prompt instructs
the model to leave fields null/empty when data is absent.
"""

from __future__ import annotations

import json
import logging

from app.llm.client import AnthropicClient
from app.llm.repair import parse_with_repair
from app.models.company import CompanyIdentity, CompanyIntelligenceProfile
from app.research.providers import SearchResult

log = logging.getLogger(__name__)

_SCHEMA = json.dumps(CompanyIntelligenceProfile.model_json_schema(), indent=2)

_PROMPT = """Extract structured company intelligence from the search results below.
IMPORTANT: Use ONLY information explicitly stated in the sources.
Set fields to null or empty lists/strings when information is not found. Never invent or guess.

Company: {company_name}

Search results (reference them by index number in source_refs fields):
{sources_text}

Return ONLY a valid JSON object matching this schema. No markdown, no explanation.
Schema:
{schema}""".strip()


def _format_sources(results: list[SearchResult]) -> str:
    lines: list[str] = []
    for i, r in enumerate(results, start=1):
        lines.append(f"[{i}] {r.url}\nTitle: {r.title}\n{r.snippet}")
    return "\n\n".join(lines)


def profile_company(
    company_name: str,
    sources: list[SearchResult],
    llm: AnthropicClient,
) -> CompanyIntelligenceProfile:
    if not sources:
        return CompanyIntelligenceProfile(
            company_identity=CompanyIdentity(name=company_name, confidence=0.0)
        )

    prompt = _PROMPT.format(
        company_name=company_name,
        sources_text=_format_sources(sources[:20]),
        schema=_SCHEMA,
    )
    raw = llm.complete(prompt, max_tokens=4096)
    try:
        return parse_with_repair(raw, CompanyIntelligenceProfile, llm.as_repair_fn())
    except Exception:
        log.warning(
            "Company profiling failed for %r; returning minimal profile",
            company_name,
            exc_info=True,
        )
        return CompanyIntelligenceProfile(
            company_identity=CompanyIdentity(name=company_name, confidence=0.1)
        )
