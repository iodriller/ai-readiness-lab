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
