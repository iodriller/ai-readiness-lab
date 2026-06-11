"""Guided pilot drill-down — scorer rubric + API contract (spec §11)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.sample import sample_brief
from app.db.base import Base, get_session
from app.main import app
from app.pilot.questions import QUESTIONS, technical_checklist
from app.pilot.scorer import score_pilot
from app.research import orchestrator

_FULL = {q.id: f"A clear, substantive answer about {q.id}; data in AWS S3." for q in QUESTIONS}


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_session():
        with factory() as session:
            yield session

    monkeypatch.setattr(orchestrator, "SessionLocal", factory)
    app.dependency_overrides[get_session] = override_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _project(client) -> str:
    return client.post(
        "/projects",
        json={"company_name": "Occidental", "user_role": "CTO", "mode": "discover_opportunities"},
    ).json()["project_id"]


# --- scorer rubric -----------------------------------------------------------


def _card():
    return sample_brief("Acme").opportunities[0]


def test_score_is_deterministic():
    a = score_pilot(_card(), _FULL)
    b = score_pilot(_card(), _FULL)
    assert a.model_dump() == b.model_dump()


def test_complete_answers_score_higher_than_empty():
    full = score_pilot(_card(), _FULL)
    empty = score_pilot(_card(), {})
    assert full.overall_score > empty.overall_score
    assert full.recommendation.value in {"proceed", "limited_pilot"}


def test_empty_answers_produce_blockers_and_next_actions():
    empty = score_pilot(_card(), {})
    assert empty.blockers  # weak dimensions are flagged
    # Every unanswered question becomes a next action.
    assert len([a for a in empty.next_actions if a.startswith("Clarify:")]) == len(QUESTIONS)


def test_checklist_surfaces_a_named_platform():
    items = technical_checklist({"data_sources": "Everything is in SharePoint and S3."})[0].items
    assert "SharePoint" in items[0] or "S3" in items[0]


def test_checklist_has_three_spec_groups():
    groups = [g.category for g in technical_checklist({})]
    assert groups == ["Data and systems", "Architecture", "Risk and operations"]


# --- API contract ------------------------------------------------------------


def test_questions_endpoint_returns_seven_questions(client):
    pid = _project(client)
    name = sample_brief("Occidental").opportunities[0].name
    r = client.get(f"/projects/{pid}/pilot/questions", params={"opportunity": name})
    assert r.status_code == 200
    body = r.json()
    assert body["opportunity_name"] == name
    assert len(body["questions"]) == 7


def test_questions_404_for_unknown_opportunity(client):
    pid = _project(client)
    r = client.get(f"/projects/{pid}/pilot/questions", params={"opportunity": "Nope"})
    assert r.status_code == 404


def test_submit_returns_plan_and_persists(client):
    pid = _project(client)
    name = sample_brief("Occidental").opportunities[0].name
    r = client.post(f"/projects/{pid}/pilot", json={"opportunity_name": name, "answers": _FULL})
    assert r.status_code == 200
    plan = r.json()
    assert plan["profile"]["opportunity_name"] == name
    assert 0 <= plan["scorecard"]["overall_score"] <= 100
    assert len(plan["technical_checklist"]) == 3

    # Persisted and retrievable.
    stored = client.get(f"/projects/{pid}/pilot").json()
    assert stored["profile"]["opportunity_name"] == name


def test_submit_404_for_unknown_opportunity(client):
    pid = _project(client)
    r = client.post(f"/projects/{pid}/pilot", json={"opportunity_name": "Nope", "answers": {}})
    assert r.status_code == 404


def test_get_pilot_is_null_before_submit(client):
    pid = _project(client)
    assert client.get(f"/projects/{pid}/pilot").json() is None


def test_report_includes_pilot_after_submit(client):
    pid = _project(client)
    name = sample_brief("Occidental").opportunities[0].name
    client.post(f"/projects/{pid}/pilot", json={"opportunity_name": name, "answers": _FULL})
    md = client.get(f"/projects/{pid}/report.md").text
    assert "Readiness Scorecard" in md
    assert "Technical Leader Questions" in md
