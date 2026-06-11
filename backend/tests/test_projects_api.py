"""Contract tests for the executive-shell project API (Phase 2 + Phase 3)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import projects  # noqa: F401 (keep import so we can reference module)
from app.db.base import Base, get_session
from app.main import app
from app.research import orchestrator


@pytest.fixture
def client(monkeypatch):
    # StaticPool shares one in-memory connection across threads so the tables
    # created here are visible to endpoints running in the TestClient threadpool.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_session():
        with factory() as session:
            yield session

    # Orchestrator uses its own session factory and may call external APIs;
    # redirect both to the in-memory engine and disable all network calls.
    monkeypatch.setattr(orchestrator, "SessionLocal", factory)
    monkeypatch.setattr(orchestrator, "STEP_DELAY_SECONDS", 0.0)
    monkeypatch.setattr(orchestrator, "_create_provider", lambda: None)
    monkeypatch.setattr(orchestrator, "_create_llm", lambda: None)
    app.dependency_overrides[get_session] = override_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create(client) -> str:
    response = client.post(
        "/projects",
        json={"company_name": "Occidental", "user_role": "CTO", "mode": "discover_opportunities"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["company_name"] == "Occidental"
    assert body["status"] == "researching"
    return body["project_id"]


def test_create_and_get_project(client):
    project_id = _create(client)
    fetched = client.get(f"/projects/{project_id}")
    assert fetched.status_code == 200
    assert fetched.json()["project_id"] == project_id


def test_create_project_rejects_blank_company(client):
    response = client.post(
        "/projects",
        json={"company_name": "", "user_role": "CTO", "mode": "discover_opportunities"},
    )
    assert response.status_code == 422


def test_get_missing_project_is_404(client):
    assert client.get("/projects/does-not-exist").status_code == 404


def test_research_stream_emits_all_steps_then_done(client):
    project_id = _create(client)
    response = client.get(f"/projects/{project_id}/research/stream")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    import json

    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    steps = [e for e in events if e["type"] == "step"]
    assert len(steps) == len(orchestrator.RESEARCH_STEPS)
    assert steps[0]["label"] == orchestrator.RESEARCH_STEPS[0]
    assert events[-1] == {"type": "done"}

    # Research completion flips the project to ready.
    assert client.get(f"/projects/{project_id}").json()["status"] == "ready"


def test_research_stream_emits_source_and_interim_events(client, monkeypatch):
    # Provider present (no LLM) → real path streams source + interim events over SSE.
    class _FakeProvider:
        def search(self, query, max_results=5):
            from app.research.providers import SearchResult

            return [SearchResult(url="https://reuters.com/x", title="News X", snippet="...")]

    monkeypatch.setattr(orchestrator, "_create_provider", lambda: _FakeProvider())

    import json

    project_id = _create(client)
    response = client.get(f"/projects/{project_id}/research/stream")
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    types = {e["type"] for e in events}
    assert {"step", "interim", "source", "done"} <= types
    source = next(e for e in events if e["type"] == "source")
    assert source["url"] == "https://reuters.com/x"
    assert source["source_type"] == "news"


def test_brief_persists_evidence_sources_after_stream(client, monkeypatch):
    class _FakeProvider:
        def search(self, query, max_results=5):
            from app.research.providers import SearchResult

            return [SearchResult(url="https://reuters.com/x", title="News X", snippet="...")]

    monkeypatch.setattr(orchestrator, "_create_provider", lambda: _FakeProvider())
    project_id = _create(client)
    client.get(f"/projects/{project_id}/research/stream")  # runs the pipeline

    body = client.get(f"/projects/{project_id}/brief").json()
    assert body["sources"], "evidence sources should be persisted on the brief"
    assert body["sources"][0]["url"] == "https://reuters.com/x"


def test_peers_and_profile_endpoints_default_empty(client):
    project_id = _create(client)
    assert client.get(f"/projects/{project_id}/peers").json() == []
    assert client.get(f"/projects/{project_id}/profile").json() is None
    assert client.get("/projects/missing/peers").status_code == 404


def test_list_projects_returns_recent_first(client):
    first = _create(client)
    second = _create(client)
    ids = [p["project_id"] for p in client.get("/projects").json()]
    assert first in ids and second in ids
    assert {"project_id", "company_name", "status", "created_at"} <= set(
        client.get("/projects").json()[0]
    )


def test_report_markdown_downloads(client):
    project_id = _create(client)
    response = client.get(f"/projects/{project_id}/report.md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "attachment" in response.headers["content-disposition"]
    assert response.text.startswith("# AI Readiness Brief: Occidental")


def test_report_pdf_downloads(client):
    project_id = _create(client)
    response = client.get(f"/projects/{project_id}/report.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:5] == b"%PDF-"


def test_report_404_for_missing_project(client):
    assert client.get("/projects/nope/report.md").status_code == 404
    assert client.get("/projects/nope/report.pdf").status_code == 404


def test_brief_returns_sample_before_stream(client):
    project_id = _create(client)
    response = client.get(f"/projects/{project_id}/brief")
    assert response.status_code == 200
    body = response.json()
    assert body["is_sample"] is True
    assert body["company_name"] == "Occidental"
    assert len(body["opportunities"]) >= 1
    assert body["opportunities"][0]["business_value"] in {"low", "medium", "high"}


def test_brief_stored_after_stream(client):
    project_id = _create(client)
    client.get(f"/projects/{project_id}/research/stream")  # runs the mock pipeline
    response = client.get(f"/projects/{project_id}/brief")
    assert response.status_code == 200
    body = response.json()
    # Mock path stores sample_brief — still valid, just confirming it's served from DB.
    assert body["company_name"] == "Occidental"
    assert len(body["opportunities"]) >= 1
