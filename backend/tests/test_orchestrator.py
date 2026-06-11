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

    def _fake_store(project_id, brief):
        stored["brief"] = brief
        stored["project_id"] = project_id

    monkeypatch.setattr(orchestrator, "_store_brief", _fake_store)
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
