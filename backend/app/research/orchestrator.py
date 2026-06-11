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
    from app.config import get_settings
    from app.llm.client import AnthropicClient

    s = get_settings()
    if not s.anthropic_api_key:
        return None
    return AnthropicClient(s.anthropic_api_key)


def _research_budget() -> tuple[int, int]:
    """Return (max_sources, timeout_seconds) for one bounded research run."""
    from app.config import get_settings

    s = get_settings()
    return s.research_max_sources, s.research_timeout_seconds


def _store_brief(project_id: str, brief: BriefResponse | None) -> None:
    """Flip status to ready and persist brief (if available) in ProjectRow.payload."""
    with SessionLocal() as session:
        row = session.get(ProjectRow, project_id)
        if row is None:
            return
        row.status = ProjectStatus.ready.value
        payload = {**row.payload, "status": ProjectStatus.ready.value}
        if brief is not None:
            payload["brief"] = json.loads(brief.model_dump_json())
        row.payload = payload
        session.commit()


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

    # Collect search results in parallel, bounded by the research budget
    # (max sources + wall-clock timeout). If the budget is hit we synthesize
    # from whatever evidence has been gathered so far rather than blocking.
    max_sources, timeout_s = _research_budget()
    sources = []
    try:
        from app.research.query_planner import plan_queries
        from app.research.source_ranker import classify_and_rank

        queries = plan_queries(company_name, mode)

        async def _search(q: str) -> list:
            if provider is None:
                return []
            return await asyncio.to_thread(provider.search, q, 5)

        result_lists = await asyncio.wait_for(
            asyncio.gather(*[_search(q) for q in queries.all_queries()], return_exceptions=True),
            timeout=timeout_s,
        )
        for r in result_lists:
            if not isinstance(r, Exception):
                sources.extend(r)
        sources = classify_and_rank(sources)[:max_sources]
    except TimeoutError:
        log.warning("Research budget timeout (%ss) for project=%r", timeout_s, project_id)
    except Exception:
        log.warning("Search phase failed for project=%r", project_id, exc_info=True)

    yield _step_event(3, total, RESEARCH_STEPS[2])
    yield _step_event(4, total, RESEARCH_STEPS[3])
    yield _step_event(5, total, RESEARCH_STEPS[4])
    yield _step_event(6, total, RESEARCH_STEPS[5])

    # LLM profiling and brief generation.
    if llm is not None and sources:
        try:
            from app.research.brief_generator import generate_brief
            from app.research.company_profiler import profile_company

            profile = await asyncio.to_thread(profile_company, company_name, sources[:20], llm)
            yield _step_event(7, total, RESEARCH_STEPS[6])
            brief = await asyncio.to_thread(generate_brief, profile, llm)
        except Exception:
            log.warning(
                "LLM phase failed for project=%r; using sample brief", project_id, exc_info=True
            )
            yield _step_event(7, total, RESEARCH_STEPS[6])
            brief = sample_brief(company_name)
    else:
        yield _step_event(7, total, RESEARCH_STEPS[6])
        brief = sample_brief(company_name)

    yield _step_event(8, total, RESEARCH_STEPS[7])
    await asyncio.to_thread(_store_brief, project_id, brief)
    yield _done_event()


async def _mock_run(project_id: str, company_name: str) -> AsyncGenerator[dict, None]:
    total = len(RESEARCH_STEPS)
    for i, label in enumerate(RESEARCH_STEPS, start=1):
        await asyncio.sleep(STEP_DELAY_SECONDS)
        yield _step_event(i, total, label)
    await asyncio.to_thread(_store_brief, project_id, sample_brief(company_name))
    yield _done_event()
