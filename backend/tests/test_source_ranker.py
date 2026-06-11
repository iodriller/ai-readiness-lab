"""Unit tests for source classification and ranking (no network)."""

from app.models.base import SourceType
from app.research.providers import SearchResult
from app.research.source_ranker import (
    classify_and_rank,
    classify_source_type,
    confidence_for,
    resolve_company_domain,
)


def test_sec_gov_classified_as_filing():
    assert classify_source_type("https://www.sec.gov/cgi-bin/browse-edgar") == SourceType.filing


def test_edgar_classified_as_filing():
    assert classify_source_type("https://edgar.sec.gov/cgi-bin/browse-edgar") == SourceType.filing


def test_reuters_classified_as_news():
    assert classify_source_type("https://www.reuters.com/article/xyz") == SourceType.news


def test_bloomberg_classified_as_news():
    assert classify_source_type("https://bloomberg.com/news/abc") == SourceType.news


def test_mckinsey_classified_as_analyst():
    assert classify_source_type("https://www.mckinsey.com/insights") == SourceType.analyst


def test_company_domain_takes_priority_over_patterns():
    # A URL on the company's own domain is official even if bloomberg is a substring.
    assert classify_source_type("https://ir.acme.com/press", "acme.com") == SourceType.official


def test_unknown_domain_falls_back_to_blog():
    assert classify_source_type("https://randomblog.io/post") == SourceType.blog


def test_filing_has_highest_confidence():
    assert confidence_for(SourceType.filing) > confidence_for(SourceType.official)
    assert confidence_for(SourceType.official) > confidence_for(SourceType.news)
    assert confidence_for(SourceType.news) > confidence_for(SourceType.blog)


def test_classify_and_rank_orders_by_confidence():
    results = [
        SearchResult(url="https://randomblog.io/post", title="Blog", snippet=""),
        SearchResult(url="https://sec.gov/filing/123", title="SEC", snippet=""),
        SearchResult(url="https://reuters.com/news/abc", title="News", snippet=""),
    ]
    ranked = classify_and_rank(results)
    assert ranked[0].source_type == SourceType.filing
    assert ranked[-1].source_type == SourceType.blog


def test_classify_and_rank_deduplicates_by_url():
    results = [
        SearchResult(url="https://example.com/a", title="A", snippet=""),
        SearchResult(url="https://example.com/a", title="A duplicate", snippet=""),
        SearchResult(url="https://example.com/b", title="B", snippet=""),
    ]
    ranked = classify_and_rank(results)
    assert len(ranked) == 2


def test_classify_and_rank_skips_empty_urls():
    results = [
        SearchResult(url="", title="No URL", snippet=""),
        SearchResult(url="https://reuters.com/news", title="News", snippet=""),
    ]
    ranked = classify_and_rank(results)
    assert len(ranked) == 1


# --- company-domain resolution (Gap 1: official-site classification) -----------
def test_resolve_company_domain_matches_name_to_domain():
    results = [
        SearchResult(url="https://en.wikipedia.org/wiki/Salesforce", title="Wiki", snippet=""),
        SearchResult(url="https://www.salesforce.com/products", title="Salesforce", snippet=""),
    ]
    assert resolve_company_domain("Salesforce", results) == "salesforce.com"


def test_resolve_company_domain_avoids_unrelated_same_word_site():
    # "Occidental" appears in an unrelated restaurant domain — must NOT match it.
    results = [
        SearchResult(url="https://theoccidentaldc.com/", title="Restaurant", snippet=""),
        SearchResult(url="https://www.merriam-webster.com/x", title="Dict", snippet=""),
    ]
    assert resolve_company_domain("Occidental Petroleum", results) == ""


def test_resolved_domain_makes_official_site_classify_as_official():
    results = [SearchResult(url="https://www.salesforce.com/ai", title="Salesforce", snippet="")]
    domain = resolve_company_domain("Salesforce", results)
    ranked = classify_and_rank(results, company_domain=domain)
    assert ranked[0].source_type == SourceType.official
