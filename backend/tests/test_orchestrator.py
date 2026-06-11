"""Unit tests for the research orchestrator (no network, no LLM API calls)."""

import pytest

from app.models.base import Mode
from app.research import orchestrator


def _collect(project_id, company_name, mode):
    """Run the async generator and collect all events synchronously."""
    import asyncio

    async def _run():
        events = []
        async for event in orchestrator.run(project_id, company_name, mode):
            events.append(event)
        return events

    return asyncio.run(_run())


@pytest.fixture(autouse=True)
def _disable_external(monkeypatch):
    """Force mock path in every test by disabling providers and LLM."""
    monkeypatch.setattr(orchestrator, "STEP_DELAY_SECONDS", 0.0)
    monkeypatch.setattr(orchestrator, "_create_provider", lambda: None)
    monkeypatch.setattr(orchestrator, "_create_llm", lambda: None)
    stored: dict = {}

    def _fake_store(project_id, brief, profile=None, classifications=None):
        stored["brief"] = brief
        stored["project_id"] = project_id
        stored["profile"] = profile
        stored["classifications"] = classifications

    monkeypatch.setattr(orchestrator, "_store_results", _fake_store)
    return stored


def test_mock_path_emits_all_steps(_disable_external):
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)
    steps = [e for e in events if e["type"] == "step"]
    assert len(steps) == len(orchestrator.RESEARCH_STEPS)
    assert events[-1] == {"type": "done"}


def test_mock_path_step_labels_match_constants(_disable_external):
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)
    step_labels = [e["label"] for e in events if e["type"] == "step"]
    assert step_labels == orchestrator.RESEARCH_STEPS


def test_mock_path_step_indices_are_sequential(_disable_external):
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)
    steps = [e for e in events if e["type"] == "step"]
    for i, step in enumerate(steps, start=1):
        assert step["index"] == i
        assert step["total"] == len(orchestrator.RESEARCH_STEPS)


def test_mock_path_stores_brief(_disable_external):
    stored = _disable_external
    _collect("p1", "Test Corp", Mode.discover_opportunities)
    assert stored.get("brief") is not None
    assert stored["brief"].company_name == "Test Corp"


def test_mock_path_done_is_last(_disable_external):
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)
    assert events[-1]["type"] == "done"


def test_all_four_modes_work(_disable_external):
    for mode in Mode:
        events = _collect("p1", "Co", mode)
        assert events[-1]["type"] == "done"


class _FakeProvider:
    """Returns two fixed results per query so the real path runs offline."""

    def search(self, query, max_results=5):
        from app.research.providers import SearchResult

        return [
            SearchResult(url="https://reuters.com/a", title="News A", snippet="..."),
            SearchResult(url="https://sec.gov/b", title="Filing B", snippet="..."),
        ]


def test_real_path_streams_source_and_interim_events(monkeypatch, _disable_external):
    # Provider present, no LLM → real search path, sample brief.
    monkeypatch.setattr(orchestrator, "_create_provider", lambda: _FakeProvider())
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)

    sources = [e for e in events if e["type"] == "source"]
    interims = [e for e in events if e["type"] == "interim"]
    assert sources, "expected source events on the real path"
    assert interims, "expected interim events on the real path"
    # Sources are deduplicated by URL across all query batches.
    assert len({s["url"] for s in sources}) == len(sources)
    # Each source event carries classification + confidence; no private field leaks.
    first = sources[0]
    assert set(first) == {"type", "url", "title", "source_type", "confidence"}
    assert 0.0 <= first["confidence"] <= 1.0
    assert events[-1] == {"type": "done"}


def test_real_path_respects_max_sources_budget(monkeypatch, _disable_external):
    monkeypatch.setattr(orchestrator, "_create_provider", lambda: _FakeProvider())
    monkeypatch.setattr(orchestrator, "_research_budget", lambda: (1, 600))
    events = _collect("p1", "Test Corp", Mode.discover_opportunities)
    sources = [e for e in events if e["type"] == "source"]
    assert len(sources) == 1
