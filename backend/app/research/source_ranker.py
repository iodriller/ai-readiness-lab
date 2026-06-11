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


_NAME_SUFFIXES = {
    "inc",
    "corp",
    "corporation",
    "co",
    "company",
    "ltd",
    "limited",
    "plc",
    "llc",
    "group",
    "holdings",
    "the",
}


def _name_tokens(company_name: str) -> set[str]:
    raw = re.split(r"[^a-z0-9]+", company_name.lower())
    return {t for t in raw if t and t not in _NAME_SUFFIXES and len(t) >= 3}


def _domain_label(url: str) -> str:
    netloc = urlparse(url).netloc.lower().removeprefix("www.")
    parts = netloc.split(".")
    return parts[-2] if len(parts) >= 2 else netloc


def resolve_company_domain(company_name: str, results: list[SearchResult]) -> str:
    """Best-effort official-domain resolution.

    Matches the company's name tokens against each result's second-level domain
    label and returns the netloc (e.g. ``salesforce.com``) on a confident match,
    else ``""``. Conservative on purpose — a wrong match would mislabel a source as
    official, so we require an exact or prefix token match (avoids e.g. a same-word
    unrelated site). Names that don't echo their domain (a ticker-style site) stay
    unresolved until the profiler supplies ``company_identity.website``.
    """
    tokens = _name_tokens(company_name)
    for r in results:
        label = _domain_label(r.url)
        if not label:
            continue
        for token in tokens:
            if label == token or (
                len(label) >= 5 and (label.startswith(token) or token.startswith(label))
            ):
                return urlparse(r.url).netloc.lower().removeprefix("www.")
    return ""


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
