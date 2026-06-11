"""Structured-output repair loop.

Enforces the "validate at the boundary" rule: raw model text is parsed against a
Pydantic schema; on a validation error the supplied `repair_fn` is asked to fix
the text using the error message, then it is re-validated. Raw JSON never reaches
the rest of the system unvalidated.

`repair_fn` is injected (not bound to any LLM client) so the loop is unit-testable
offline and reusable by whichever client produced the text.
"""

import re
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

# repair_fn(previous_text, validation_error) -> corrected_text
RepairFn = Callable[[str, str], str]

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


class StructuredOutputError(Exception):
    """Raised when text cannot be validated even after the allowed repairs."""


def _strip_fence(text: str) -> str:
    match = _FENCE.search(text)
    return match.group(1) if match else text.strip()


def parse_with_repair(
    raw: str,
    model: type[T],
    repair_fn: RepairFn,
    max_repairs: int = 2,
) -> T:
    """Validate `raw` into `model`, repairing up to `max_repairs` times."""
    text = raw
    last_error: ValidationError | None = None
    for attempt in range(max_repairs + 1):
        try:
            return model.model_validate_json(_strip_fence(text))
        except ValidationError as error:
            last_error = error
            if attempt == max_repairs:
                break
            text = repair_fn(text, str(error))
    raise StructuredOutputError(
        f"Failed to validate into {model.__name__} after {max_repairs} repair(s)"
    ) from last_error
