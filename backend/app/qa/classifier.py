"""Question type classifier (spec §10).

Rule-based: faster and more predictable than an LLM for this 5-class problem.
Each type maps to a different emphasis in the structured answer (see composer.py).
"""

from __future__ import annotations

from enum import Enum

_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "comparison",
        [
            "compare",
            "versus",
            "vs ",
            "benchmark",
            "how do we stack",
            "how are we doing",
            "how do others",
            "what do competitors",
            "what are peers",
            "against others",
            "relative to",
            "compared to",
            "competitor",
            "industry average",
        ],
    ),
    (
        "risk",
        [
            "risk",
            "concern",
            "danger",
            "threat",
            "failure",
            "what could go wrong",
            "downside",
            "pitfall",
            "challenge",
            "issue",
            "problem",
            "obstacle",
            "liability",
            "compliance",
            "regulatory",
            "legal",
        ],
    ),
    (
        "sequencing",
        [
            "where to start",
            "where should we start",
            "where do we start",
            "what first",
            "roadmap",
            "timeline",
            "sequence",
            "order",
            "priority",
            "prioritize",
            "phase",
            "next step",
            "step by step",
            "how do we begin",
            "how do we start",
            "plan",
            "rollout",
        ],
    ),
    (
        "technical",
        [
            "architecture",
            "integration",
            "system",
            "infrastructure",
            "api",
            "data pipeline",
            "model",
            "deployment",
            "cloud",
            "security",
            "access",
            "permission",
            "sso",
            "auth",
            "implementation detail",
            "how does it work",
            "technical",
            "technology",
            "platform",
            "stack",
        ],
    ),
    (
        "opportunity_seeking",
        [
            "what can we",
            "what should we",
            "pilot",
            "opportunity",
            "use case",
            "application",
            "workflow",
            "department",
            "team",
            "function",
            "where can ai",
            "how can ai",
            "what ai",
            "ideas for",
            "options for",
            "possibilities",
            "potential",
        ],
    ),
]


class QuestionType(str, Enum):
    opportunity_seeking = "opportunity_seeking"
    comparison = "comparison"
    risk = "risk"
    sequencing = "sequencing"
    technical = "technical"


def classify(question: str) -> QuestionType:
    """Classify an executive question into one of the five answer archetypes."""
    lower = question.lower()
    for type_name, keywords in _PATTERNS:
        if any(kw in lower for kw in keywords):
            return QuestionType(type_name)
    # Default: opportunity-seeking — most questions from execs are opportunity questions.
    return QuestionType.opportunity_seeking
