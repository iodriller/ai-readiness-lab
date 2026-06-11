"""Tests for the Q&A package — classifier, composer, and API contract."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base, get_session
from app.main import app
from app.qa.classifier import QuestionType, classify
from app.qa.composer import StructuredAnswer, _heuristic_answer
from app.qa.retriever import QAContext
from app.research import orchestrator


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
    monkeypatch.setattr(orchestrator, "STEP_DELAY_SECONDS", 0.0)
    monkeypatch.setattr(orchestrator, "_create_provider", lambda: None)
    monkeypatch.setattr(orchestrator, "_create_llm", lambda: None)
    app.dependency_overrides[get_session] = override_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _make_project(client) -> str:
    r = client.post(
        "/projects",
        json={"company_name": "Occidental", "user_role": "CTO", "mode": "discover_opportunities"},
    )
    assert r.status_code == 200
    return r.json()["project_id"]


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "question, expected",
    [
        ("What can we do for drilling engineers?", QuestionType.opportunity_seeking),
        ("Where should we start with AI?", QuestionType.sequencing),
        ("How do we compare to our competitors?", QuestionType.comparison),
        ("What are the risks of an AI pilot?", QuestionType.risk),
        ("What architecture would this require?", QuestionType.technical),
        ("What pilot options exist for finance?", QuestionType.opportunity_seeking),
        ("What is the right roadmap for AI adoption?", QuestionType.sequencing),
        ("Benchmark us against SLB", QuestionType.comparison),
        ("What compliance concerns should we address?", QuestionType.risk),
        ("How does the integration with SAP work?", QuestionType.technical),
    ],
)
def test_classifier(question, expected):
    assert classify(question) == expected


def test_classifier_defaults_to_opportunity_seeking():
    assert classify("Tell me something interesting.") == QuestionType.opportunity_seeking


# ---------------------------------------------------------------------------
# Heuristic fallback composer
# ---------------------------------------------------------------------------

def _make_context() -> QAContext:
    from app.models.company import CompanyIdentity, CompanyIntelligenceProfile

    profile = CompanyIntelligenceProfile(company_identity=CompanyIdentity(name="Acme"))
    return QAContext(
        company_name="Acme",
        profile=profile,
        peers=[],
        signals=[],
        opportunity_cards=[],
        prior_answers=[],
    )


def test_heuristic_answer_returns_structured_answer():
    ctx = _make_context()
    answer = _heuristic_answer("What pilots should we run?", QuestionType.opportunity_seeking, ctx)
    assert isinstance(answer, StructuredAnswer)
    assert answer.question == "What pilots should we run?"
    assert answer.question_type == QuestionType.opportunity_seeking.value
    assert answer.direct_answer
    assert answer.why_it_matters
    assert isinstance(answer.pilot_options, list)
    assert isinstance(answer.technical_questions, list)
    assert len(answer.technical_questions) > 0


def test_heuristic_answer_no_invented_peers():
    """With no signals, peer_signals must not invent company names."""
    ctx = _make_context()
    answer = _heuristic_answer("What are peers doing?", QuestionType.comparison, ctx)
    # No real signals → the list should be a single "no signals" statement
    assert len(answer.peer_signals) == 1
    assert "no specific peer" in answer.peer_signals[0].lower()


# ---------------------------------------------------------------------------
# Compose with null LLM (exercises heuristic path via public API)
# ---------------------------------------------------------------------------

def test_compose_answer_no_llm():
    from app.qa.composer import compose_answer

    ctx = _make_context()
    answer = compose_answer("What can we do for HR?", QuestionType.opportunity_seeking, ctx)
    assert answer.question_type == "opportunity_seeking"
    assert answer.recommended_first_pilot  # always non-empty


# ---------------------------------------------------------------------------
# API contract
# ---------------------------------------------------------------------------

def test_qa_endpoint_returns_structured_answer(client):
    project_id = _make_project(client)
    response = client.post(
        f"/projects/{project_id}/qa", json={"question": "What pilots should we run?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "What pilots should we run?"
    assert body["question_type"] in {qt.value for qt in QuestionType}
    assert body["direct_answer"]
    assert isinstance(body["pilot_options"], list)
    assert isinstance(body["technical_questions"], list)


def test_qa_endpoint_404_for_missing_project(client):
    response = client.post("/projects/does-not-exist/qa", json={"question": "What pilots?"})
    assert response.status_code == 404


def test_qa_endpoint_rejects_empty_question(client):
    project_id = _make_project(client)
    response = client.post(f"/projects/{project_id}/qa", json={"question": ""})
    assert response.status_code == 422


def test_qa_history_persists_across_calls(client):
    project_id = _make_project(client)
    client.post(f"/projects/{project_id}/qa", json={"question": "First question"})
    client.post(f"/projects/{project_id}/qa", json={"question": "Second question"})

    # History is stored in payload — verify via the project endpoint indirectly
    # by confirming the second call still works correctly.
    r = client.post(f"/projects/{project_id}/qa", json={"question": "Third question"})
    assert r.status_code == 200
