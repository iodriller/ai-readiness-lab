"""Tests for the structured-output repair loop."""

import pytest

from app.llm.repair import StructuredOutputError, parse_with_repair
from app.models import SourceRecord

_VALID = '{"url": "https://x.com", "title": "T", "source_type": "news", "confidence": 0.5}'


def test_valid_text_parses_without_repair():
    calls = []

    def repair_fn(text, error):  # noqa: ARG001
        calls.append(1)
        return text

    result = parse_with_repair(_VALID, SourceRecord, repair_fn)
    assert result.url == "https://x.com"
    assert calls == []  # repair never invoked


def test_fenced_json_is_unwrapped():
    fenced = f"```json\n{_VALID}\n```"
    result = parse_with_repair(fenced, SourceRecord, lambda t, e: t)
    assert result.confidence == 0.5


def test_malformed_text_is_repaired_then_validated():
    broken = '{"url": "https://x.com", "title": "T", "source_type": "news"}'  # missing confidence

    def repair_fn(text, error):  # noqa: ARG001
        return _VALID

    result = parse_with_repair(broken, SourceRecord, repair_fn, max_repairs=1)
    assert result.confidence == 0.5


def test_unrepairable_text_raises_after_max_repairs():
    attempts = []

    def repair_fn(text, error):  # noqa: ARG001
        attempts.append(1)
        return "{not json"

    with pytest.raises(StructuredOutputError):
        parse_with_repair("{not json", SourceRecord, repair_fn, max_repairs=2)
    assert len(attempts) == 2  # called once per allowed repair
