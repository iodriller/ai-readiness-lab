"""Source type classification and confidence ranking (spec §7.4).

Confidence hierarchy: filing > official > analyst > news > academic > job_posting > vendor > blog
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from app.models.base import SourceType
from app.research.providers import SearchResult

_DOMAIN_PATTERNS: list[tuple[re.Pattern[str], SourceType]] = [
    (re.compile(r"sec\.gov|edgar\.sec\.gov"), SourceType.filing),
    (
        re.compile(
            r"reuters\.com|bloomberg\.com|wsj\.com|ft\.com|nytimes\.com"
            r"|cnbc\.com|businessinsider\.com|techcrunch\.com|wired\.com"
            r"|theguardian\.com|bbc\.co|apnews\.com|axios\.com|forbes\.com"
            r"|fortune\.com|businesswire\.com|prnewswire\.com|globenewswire\.com"
        ),
        SourceType.news,
    ),
    (
        re.compile(
            r"mckinsey\.com|gartner\.com|forrester\.com|idc\.com"
            r"|deloitte\.com|accenture\.com|pwc\.com|kpmg\.com|bcg\.com"
            r"|hbr\.org|mit\.edu|stanford\.edu|ey\.com|bain\.com"
        ),
        SourceType.analyst,
    ),
    (
        re.compile(r"linkedin\.com/jobs|jobs\.[a-z]+\.com|lever\.co|greenhouse\.io"),
        SourceType.job_posting,
    ),
    (
        re.compile(r"arxiv\.org|nature\.com|ieee\.org|acm\.org|science\.org"),
        SourceType.academic,
    ),
]

_SOURCE_CONFIDENCE: dict[SourceType, float] = {
    SourceType.filing: 0.95,
    SourceType.official: 0.90,
    SourceType.analyst: 0.80,
    SourceType.news: 0.70,
    SourceType.academic: 0.65,
    SourceType.job_posting: 0.60,
    SourceType.vendor: 0.50,
    SourceType.blog: 0.40,
}


def classify_source_type(url: str, company_domain: str = "") -> SourceType:
    """Classify a URL into a SourceType using domain patterns."""
    domain = urlparse(url).netloc.lower()
    if company_domain and company_domain in domain:
        return SourceType.official
    for pattern, stype in _DOMAIN_PATTERNS:
        if pattern.search(domain):
            return stype
    return SourceType.blog


def confidence_for(source_type: SourceType) -> float:
    return _SOURCE_CONFIDENCE.get(source_type, 0.40)


def classify_and_rank(results: list[SearchResult], company_domain: str = "") -> list[SearchResult]:
    """Classify source types, deduplicate by URL, and sort by confidence descending."""
    seen: set[str] = set()
    unique: list[SearchResult] = []
    for r in results:
        if r.url and r.url not in seen:
            seen.add(r.url)
            r.source_type = classify_source_type(r.url, company_domain)
            unique.append(r)
    return sorted(unique, key=lambda r: confidence_for(r.source_type), reverse=True)
