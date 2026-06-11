"""Unit tests for the query planner (no network, no LLM)."""

from app.models.base import Mode
from app.research.query_planner import plan_queries


def test_all_base_buckets_populated():
    qs = plan_queries("Acme Corp", Mode.discover_opportunities)
    assert qs.identity
    assert qs.financial
    assert qs.strategic
    assert qs.competitors
    assert qs.competitor_ai
    assert qs.industry_ai
    assert qs.company_ai


def test_company_name_appears_in_every_query():
    qs = plan_queries("Big Oil Inc", Mode.discover_opportunities)
    for q in qs.all_queries():
        assert "Big Oil Inc" in q


def test_evaluate_idea_adds_extra_queries():
    base = plan_queries("Co", Mode.discover_opportunities)
    ev = plan_queries("Co", Mode.evaluate_idea)
    assert len(ev.company_ai) > len(base.company_ai)
    assert len(ev.industry_ai) > len(base.industry_ai)


def test_strategy_question_adds_extra_queries():
    base = plan_queries("Co", Mode.discover_opportunities)
    sq = plan_queries("Co", Mode.strategy_question)
    assert len(sq.competitors) > len(base.competitors)
    assert len(sq.industry_ai) > len(base.industry_ai)


def test_compare_competitors_adds_extra_competitor_ai_queries():
    base = plan_queries("Co", Mode.discover_opportunities)
    cc = plan_queries("Co", Mode.compare_competitors)
    assert len(cc.competitor_ai) > len(base.competitor_ai)


def test_all_queries_returns_flat_list():
    qs = plan_queries("Co", Mode.discover_opportunities)
    flat = qs.all_queries()
    assert isinstance(flat, list)
    assert len(flat) >= 7
