"""Opportunity library loader (spec §6).

The library is versioned reference data (`data/library.json`) shipped with the
package. Each use case carries default value/feasibility/risk hints plus the
keywords used to match it to a company's profile and signals.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from app.models.base import Level, TimeToPilot

_DATA = Path(__file__).parent / "data" / "library.json"


class UseCase(BaseModel):
    name: str
    category: str
    executive_summary: str
    business_value: Level
    pilot_feasibility: Level
    risk_level: Level
    time_to_pilot: TimeToPilot
    technical_depth_required: Level
    why_now: str
    first_step: str
    keywords: list[str] = Field(default_factory=list)


@lru_cache
def load_library() -> list[UseCase]:
    raw = json.loads(_DATA.read_text())
    return [UseCase(**uc) for uc in raw["use_cases"]]
