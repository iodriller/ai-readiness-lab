"""Search provider abstraction with Tavily, Serper, and DuckDuckGo implementations.

Provider priority: TAVILY_API_KEY → Tavily; SERPER_API_KEY → Serper; otherwise → DuckDuckGo
(free, open-source, no API key required).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

from app.models.base import SourceType

log = logging.getLogger(__name__)


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    source_type: SourceType = field(default=SourceType.blog)


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]: ...


class TavilyProvider:
    """Structured search via Tavily AI Search API (TAVILY_API_KEY required)."""

    def __init__(self, api_key: str) -> None:
        from tavily import TavilyClient  # type: ignore[import-untyped]

        self._client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            response = self._client.search(query, max_results=max_results)
            return [
                SearchResult(
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    snippet=r.get("content", ""),
                )
                for r in response.get("results", [])
            ]
        except Exception:
            log.warning("Tavily search failed for query=%r", query, exc_info=True)
            return []


class SerperProvider:
    """Google search results via Serper.dev API (SERPER_API_KEY required)."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        import httpx

        try:
            resp = httpx.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": max_results},
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                SearchResult(
                    url=r.get("link", ""),
                    title=r.get("title", ""),
                    snippet=r.get("snippet", ""),
                )
                for r in data.get("organic", [])[:max_results]
            ]
        except Exception:
            log.warning("Serper search failed for query=%r", query, exc_info=True)
            return []


class DuckDuckGoProvider:
    """Free open-source search via DuckDuckGo — no API key required."""

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        from duckduckgo_search import DDGS  # type: ignore[import-untyped]

        try:
            hits = list(DDGS().text(query, max_results=max_results))
            return [
                SearchResult(
                    url=r.get("href", ""),
                    title=r.get("title", ""),
                    snippet=r.get("body", ""),
                )
                for r in hits
            ]
        except Exception:
            log.warning("DuckDuckGo search failed for query=%r", query, exc_info=True)
            return []


def get_provider(tavily_api_key: str = "", serper_api_key: str = "") -> SearchProvider | None:
    """Return the highest-priority available provider; None if nothing is usable."""
    if tavily_api_key:
        return TavilyProvider(tavily_api_key)
    if serper_api_key:
        return SerperProvider(serper_api_key)
    try:
        from duckduckgo_search import DDGS  # type: ignore[import-untyped] # noqa: F401

        return DuckDuckGoProvider()
    except ImportError:
        return None
