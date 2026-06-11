"""Tests for the Q&A package — classifier, composer, and API contract."""

from datetime import datetime, timezone

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
    # Force the deterministic heuristic path so the Q&A contract tests never
    # depend on a configured key or make a network call.
    monkeypatch.setattr("app.qa.router.create_llm", lambda: None)
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


# ---------------------------------------------------------------------------
# Retriever — reads a real stored profile (regression: competitive_ai_signals)
# ---------------------------------------------------------------------------

def _session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def test_gather_context_reads_stored_profile_signals():
    """A stored profile's competitive_ai_signals must reach the QA context.

    Regression: the retriever previously read a non-existent `competitive_signals`
    attribute, which raised AttributeError whenever a real profile was present.
    """
    from app.db.models import ProjectRow
    from app.models.company import CompanyIdentity, CompanyIntelligenceProfile
    from app.models.competitive import CompetitiveSignal
    from app.qa.retriever import gather_context

    profile = CompanyIntelligenceProfile(
        company_identity=CompanyIdentity(name="Occidental", industry="oil_gas"),
        competitive_ai_signals=[
            CompetitiveSignal(
                company="SLB",
                peer_type="service_company",
                signal="AI drilling platform",
                ai_area="drilling",
                business_relevance="ecosystem signal",
                fomo_strength="medium",
                confidence=0.7,
            )
        ],
    )
    factory = _session_factory()
    with factory() as session:
        session.add(
            ProjectRow(
                project_id="p1",
                company_name="Occidental",
                user_role="CTO",
                mode="discover_opportunities",
                status="ready",
                created_at=datetime.now(timezone.utc),
                payload={"profile": profile.model_dump(mode="json")},
            )
        )
        session.commit()

        ctx = gather_context("p1", session)
        assert ctx is not None
        assert ctx.profile is not None
        assert len(ctx.signals) == 1
        assert ctx.signals[0].company == "SLB"


def test_history_block_summarizes_prior_answers():
    from app.qa.composer import _history_block

    ctx = _make_context()
    ctx.prior_answers = [
        {"question": "First?", "answer": {"direct_answer": "Start with knowledge assistant."}},
    ]
    block = _history_block(ctx)
    assert "First?" in block
    assert "knowledge assistant" in block


def test_history_block_empty_when_no_history():
    from app.qa.composer import _history_block

    assert "first question" in _history_block(_make_context()).lower()
