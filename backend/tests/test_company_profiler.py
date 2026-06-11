"""Unit tests for the company profiler (no LLM API calls)."""

from app.models.company import CompanyIdentity, CompanyIntelligenceProfile
from app.research.company_profiler import profile_company
from app.research.providers import SearchResult


def _mock_llm(response: str):
    """Minimal stub that returns a fixed string from complete()."""

    class _LLM:
        def complete(self, prompt, max_tokens=4096):
            return response

        def as_repair_fn(self):
            return lambda text, error: response

    return _LLM()


def test_empty_sources_returns_minimal_profile():
    llm = _mock_llm("{}")
    profile = profile_company("Acme", [], llm)
    assert profile.company_identity.name == "Acme"
    assert profile.company_identity.confidence == 0.0


def test_valid_json_is_parsed():
    valid_profile = CompanyIntelligenceProfile(
        company_identity=CompanyIdentity(name="Acme Corp", confidence=0.85)
    ).model_dump_json()
    llm = _mock_llm(valid_profile)
    sources = [
        SearchResult(url="https://acme.com", title="About Acme", snippet="Acme Corp is a leader")
    ]
    profile = profile_company("Acme Corp", sources, llm)
    assert profile.company_identity.name == "Acme Corp"
    assert profile.company_identity.confidence == 0.85


def test_bad_json_falls_back_to_minimal_profile():
    llm = _mock_llm("this is not json at all !!!")
    sources = [SearchResult(url="https://acme.com", title="Acme", snippet="...")]
    profile = profile_company("Acme", sources, llm)
    assert profile.company_identity.name == "Acme"
    assert profile.company_identity.confidence == 0.1


def test_sources_capped_at_20():
    """LLM is called with at most 20 sources to avoid token overflow."""
    calls = []

    class _LLM:
        def complete(self, prompt, max_tokens=4096):
            calls.append(prompt)
            return CompanyIntelligenceProfile(
                company_identity=CompanyIdentity(name="Co", confidence=0.5)
            ).model_dump_json()

        def as_repair_fn(self):
            return lambda text, error: text

    sources = [
        SearchResult(url=f"https://example.com/{i}", title=f"Page {i}", snippet="")
        for i in range(30)
    ]
    profile_company("Co", sources, _LLM())
    assert len(calls) == 1
    # Prompt should reference [20] but not [21].
    assert "[20]" in calls[0]
    assert "[21]" not in calls[0]
