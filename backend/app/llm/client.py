"""Anthropic SDK wrapper with structured-output repair_fn factory."""

from __future__ import annotations

import anthropic

from app.llm.repair import RepairFn

_DEFAULT_MODEL = "claude-opus-4-8"


class AnthropicClient:
    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, max_tokens: int = 4096) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text  # type: ignore[union-attr]

    def as_repair_fn(self) -> RepairFn:
        def repair(text: str, error: str) -> str:
            return self.complete(
                f"The following JSON failed Pydantic validation:\n\n{text}\n\n"
                f"Validation error:\n{error}\n\n"
                "Return only the corrected JSON, no markdown or explanation."
            )

        return repair


def create_llm() -> AnthropicClient | None:
    """Build the LLM client from settings. Returns None if no key is configured,
    which signals every caller to use its offline/heuristic path."""
    from app.config import get_settings

    key = get_settings().anthropic_api_key
    return AnthropicClient(key) if key else None
