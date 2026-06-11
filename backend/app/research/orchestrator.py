"""Research orchestrator — replaces the Phase 2 mock SSE job with real research.

When no API keys are configured (ANTHROPIC_API_KEY, TAVILY_API_KEY, SERPER_API_KEY)
and DuckDuckGo is unavailable, the mock path fires the same 8 steps with a
per-step delay (RESEARCH_STEP_DELAY_SECONDS env var, default 0.6 s). This keeps
the test suite and offline demo fully functional without credentials.

Real path: searches run in parallel → source classification → LLM company profiling
→ brief generation → brief persisted in ProjectRow.payload["brief"].
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from collections.abc import AsyncGenerator

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse
from app.db.base import SessionLocal
from app.db.models import ProjectRow
from app.models.base import Mode, ProjectStatus

log = logging.getLogger(__name__)

STEP_DELAY_SECONDS = float(os.getenv("RESEARCH_STEP_DELAY_SECONDS", "0.6"))

RESEARCH_STEPS = [
    "Identifying company profile",
    "Classifying company type and business segments",
    "Finding public financial and strategic signals",
    "Identifying direct competitors and adjacent peers",
    "Searching competitor AI and digital initiatives",
    "Searching industry AI patterns",
    "Building AI opportunity map",
    "Preparing executive brief",
]


def _step_event(index: int, total: int, label: str) -> dict:
    return {"type": "step", "index": index, "total": total, "label": label}


def _interim_event(label: str, detail: str = "") -> dict:
    return {"type": "interim", "label": label, "detail": detail}


def _source_event(result) -> dict:
    from app.research.source_ranker import confidence_for

    return {
        "type": "source",
        "url": result.url,
        "title": result.title,
        "source_type": result.source_type.value,
        "confidence": round(confidence_for(result.source_type), 2),
    }


def _done_event() -> dict:
    return {"type": "done"}


def _create_provider():
    """Build search provider from settings. Returns None if nothing is usable."""
    from app.config import get_settings
    from app.research.providers import get_provider

    s = get_settings()
    return get_provider(s.tavily_api_key or "", s.serper_api_key or "")


def _create_llm():
    """Build LLM client from settings. Returns None if ANTHROPIC_API_KEY is not set."""
    from app.llm.client import create_llm

    return create_llm()


def _research_budget() -> tuple[int, int]:
    """Return (max_sources, timeout_seconds) for one bounded research run."""
    from app.config import get_settings

    s = get_settings()
    return s.research_max_sources, s.research_timeout_seconds


def _brief_sources(sources, limit: int = 15) -> list:
    """Build the brief's Evidence panel from the ranked sources (top `limit`)."""
    from app.api.schemas import BriefSource
    from app.research.source_ranker import confidence_for

    return [
        BriefSource(
            url=r.url,
            title=r.title,
            source_type=r.source_type.value,
            confidence=round(confidence_for(r.source_type), 2),
        )
        for r in sources[:limit]
    ]


def _store_results(project_id, brief, profile=None, classifications=None) -> None:
    """Flip status to ready and persist the brief (incl. evidence), plus the profile
    and peer classifications when available, in ProjectRow.payload."""
    with SessionLocal() as session:
        row = session.get(ProjectRow, project_id)
        if row is None:
            return
        row.status = ProjectStatus.ready.value
        payload = {**row.payload, "status": ProjectStatus.ready.value}
        if brief is not None:
            payload["brief"] = json.loads(brief.model_dump_json())
        if profile is not None:
            payload["profile"] = json.loads(profile.model_dump_json())
        if classifications is not None:
            payload["peers"] = [json.loads(c.model_dump_json()) for c in classifications]
        row.payload = payload
        session.commit()


def _build_intelligence(subject: str, profile):
    """Phase 4+5: correct peer taxonomy, vet competitive signals, rank opportunities.

    Returns (enriched_profile, peer_classifications, opportunity_cards).
    """
    from app.opportunity.scorer import score_opportunities
    from app.research.competitive_signals import filter_relevant, reconcile_peer_types
    from app.research.peer_classifier import classify_peers, to_taxonomy

    tax = profile.peer_taxonomy
    candidates = list(
        dict.fromkeys(
            tax.direct_competitors
            + tax.operator_peers
            + tax.service_company_benchmarks
            + tax.technology_vendor_benchmarks
            + tax.adjacent_industry_benchmarks
            + [s.company for s in profile.competitive_ai_signals]
        )
    )
    classifications = classify_peers(subject, candidates)
    signals = filter_relevant(reconcile_peer_types(subject, profile.competitive_ai_signals))
    profile = profile.model_copy(
        update={"peer_taxonomy": to_taxonomy(classifications), "competitive_ai_signals": signals}
    )
    cards = score_opportunities(profile, signals)
    return profile, classifications, cards


async def run(project_id: str, company_name: str, mode: Mode) -> AsyncGenerator[dict, None]:
    """Yield SSE event dicts. Falls back to mock steps when no credentials are set."""
    total = len(RESEARCH_STEPS)
    provider = _create_provider()
    llm = _create_llm()

    if provider is None and llm is None:
        async for event in _mock_run(project_id, company_name):
            yield event
        return

    brief: BriefResponse | None = None

    yield _step_event(1, total, RESEARCH_STEPS[0])
    yield _step_event(2, total, RESEARCH_STEPS[1])
    yield _step_event(3, total, RESEARCH_STEPS[2])
    yield _step_event(4, total, RESEARCH_STEPS[3])

    # Collect sources, streaming each one to the UI as its search returns, bounded
    # by the research budget (max sources + wall-clock timeout). If the budget is
    # hit we synthesize from whatever evidence we gathered rather than blocking.
    sources = []
    if provider is not None:
        async for event in _stream_sources(company_name, mode, provider):
            if event["type"] == "source":
                sources.append(event.pop("_result"))
            yield event

    yield _step_event(5, total, RESEARCH_STEPS[4])
    yield _step_event(6, total, RESEARCH_STEPS[5])

    # Re-rank across all batches; resolve the company's own domain so its official
    # site is labeled correctly (not as a blog) in the evidence set.
    from app.research.source_ranker import classify_and_rank, resolve_company_domain

    domain = resolve_company_domain(company_name, sources)
    sources = classify_and_rank(sources, company_domain=domain)

    # LLM profiling, peer/opportunity enrichment, and brief generation.
    profile = None
    classifications = None
    if llm is not None and sources:
        try:
            from app.research.brief_generator import generate_brief
            from app.research.company_profiler import profile_company

            yield _interim_event("Analyzing evidence with Claude", "Extracting a company profile")
            profile = await asyncio.to_thread(profile_company, company_name, sources[:20], llm)
            profile, classifications, cards = _build_intelligence(company_name, profile)
            yield _step_event(7, total, RESEARCH_STEPS[6])
            brief = await asyncio.to_thread(generate_brief, profile, llm)
            if cards:
                brief = brief.model_copy(update={"opportunities": cards})
        except Exception:
            log.warning(
                "LLM phase failed for project=%r; using sample brief", project_id, exc_info=True
            )
            profile = classifications = None
            yield _step_event(7, total, RESEARCH_STEPS[6])
            brief = sample_brief(company_name)
    else:
        yield _step_event(7, total, RESEARCH_STEPS[6])
        brief = sample_brief(company_name)

    # Attach the real evidence set to the brief so it survives a reload.
    brief = brief.model_copy(update={"sources": _brief_sources(sources)})

    yield _step_event(8, total, RESEARCH_STEPS[7])
    await asyncio.to_thread(_store_results, project_id, brief, profile, classifications)
    yield _done_event()


async def _stream_sources(company_name, mode, provider) -> AsyncGenerator[dict, None]:
    """Run the planned searches and yield interim + source events as results arrive.

    Each `source` event carries a private `_result` SearchResult the caller pops
    off to accumulate the evidence set. Bounded by (max_sources, timeout_seconds).
    """
    from app.research.query_planner import plan_queries
    from app.research.source_ranker import classify_and_rank

    max_sources, timeout_s = _research_budget()
    queries = plan_queries(company_name, mode).all_queries()
    yield _interim_event("Searching public web sources", f"{len(queries)} research angles")

    async def _search(q: str) -> list:
        return await asyncio.to_thread(provider.search, q, 5)

    seen: set[str] = set()
    kept = 0
    tasks = [asyncio.create_task(_search(q)) for q in queries]
    try:
        for future in asyncio.as_completed(tasks, timeout=timeout_s):
            try:
                results = await future
            except Exception:
                continue
            for r in classify_and_rank(results):
                if not r.url or r.url in seen or kept >= max_sources:
                    continue
                seen.add(r.url)
                kept += 1
                yield {**_source_event(r), "_result": r}
            if kept >= max_sources:
                break
    except (TimeoutError, asyncio.TimeoutError):
        log.warning("Research budget timeout (%ss) for company=%r", timeout_s, company_name)
    finally:
        for t in tasks:
            t.cancel()

    yield _interim_event("Ranked sources by credibility", f"{kept} sources kept")


async def _mock_run(project_id: str, company_name: str) -> AsyncGenerator[dict, None]:
    total = len(RESEARCH_STEPS)
    for i, label in enumerate(RESEARCH_STEPS, start=1):
        await asyncio.sleep(STEP_DELAY_SECONDS)
        yield _step_event(i, total, label)
    await asyncio.to_thread(_store_results, project_id, sample_brief(company_name))
    yield _done_event()
