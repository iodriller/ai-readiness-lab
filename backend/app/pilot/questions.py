"""The guided drill-down questions (spec §11.1) and the technical discovery
checklist (§11.2).

Both are plain-English and deterministic. The technical checklist is the verbatim
spec list, lightly tailored: when an executive's data-source answer names a known
platform we promote it to the top of the data/systems group so the technical
leader sees the concrete starting point first. No facts are invented.
"""

from __future__ import annotations

from app.pilot.models import PilotQuestion, TechnicalChecklistGroup

QUESTIONS: list[PilotQuestion] = [
    PilotQuestion(id="users", prompt="Who would use this?"),
    PilotQuestion(id="workflow", prompt="What decision or workflow should improve?"),
    PilotQuestion(id="never_do", prompt="What should the AI never do?"),
    PilotQuestion(id="data_sources", prompt="What data sources likely exist?"),
    PilotQuestion(id="success_outcome", prompt="What outcome would make this worth it?"),
    PilotQuestion(id="unacceptable_risk", prompt="What risk would make this unacceptable?"),
    PilotQuestion(id="approver", prompt="Who would approve the pilot?"),
]

QUESTION_IDS = {q.id for q in QUESTIONS}

_KNOWN_PLATFORMS = [
    "SharePoint",
    "Box",
    "S3",
    "data lake",
    "network drive",
    "AWS",
    "Azure",
    "GCP",
    "Snowflake",
    "Databricks",
    "on-prem",
]

_DATA_SYSTEMS = [
    "Where are the relevant documents stored?",
    "Are they in SharePoint, Box, S3, data lake, network drive, or a document management system?",
    "Are database exports available?",
    "Are APIs available?",
    "Are access controls already defined?",
    "Is the data on AWS, Azure, GCP, Snowflake, Databricks, or on-prem?",
    "Are there existing vector search, RAG, or AI platform capabilities?",
]

_ARCHITECTURE = [
    "Should the pilot run in AWS, Azure, GCP, or internal infrastructure?",
    "Is there an approved LLM provider?",
    "Is local model deployment required?",
    "Is data allowed to leave the enterprise environment?",
    "What observability/evaluation tooling is approved?",
    "Is there an existing API gateway or tool-integration layer?",
]

_RISK_OPS = [
    "Who owns the assistant?",
    "Who approves high-risk outputs?",
    "What is the escalation path?",
    "What logs must be retained?",
    "What evaluation threshold is required before rollout?",
]


def technical_checklist(answers: dict[str, str] | None = None) -> list[TechnicalChecklistGroup]:
    """The §11.2 checklist, with any named data platform surfaced first."""
    data_items = list(_DATA_SYSTEMS)
    data_answer = (answers or {}).get("data_sources", "")
    named = [p for p in _KNOWN_PLATFORMS if p.lower() in data_answer.lower()]
    if named:
        data_items.insert(0, f"Confirm access to the named source(s): {', '.join(named)}.")
    return [
        TechnicalChecklistGroup(category="Data and systems", items=data_items),
        TechnicalChecklistGroup(category="Architecture", items=list(_ARCHITECTURE)),
        TechnicalChecklistGroup(category="Risk and operations", items=list(_RISK_OPS)),
    ]
