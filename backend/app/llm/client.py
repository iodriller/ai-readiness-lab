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


def resolve_api_key() -> str | None:
    """The Anthropic key, preferring the one the user pasted in-app (stored in the
    OS keychain) over an environment/.env value. Returns None if none is set."""
    from app.config import get_settings
    from app.settings_store import get_api_key

    return get_api_key() or get_settings().anthropic_api_key


def create_llm() -> AnthropicClient | None:
    """Build the LLM client. Returns None if no key is configured, which signals
    every caller to use its offline/heuristic path."""
    key = resolve_api_key()
    return AnthropicClient(key) if key else None
