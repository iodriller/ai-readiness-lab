"""Structured answer composer (spec §10).

Produces a `StructuredAnswer` — a nine-field structured response that is far
richer than a generic chatbot would give. When no LLM is available the heuristic
fallback assembles a reasonable answer directly from the context so the UI is
always useful.

No-hallucination rule: peer names only appear when a real CompetitiveSignal backs
them; pilot options only come from the resolved opportunity cards, not invented.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel

from app.llm.repair import parse_with_repair
from app.qa.classifier import QuestionType
from app.qa.retriever import QAContext

log = logging.getLogger(__name__)


class StructuredAnswer(BaseModel):
    question: str
    question_type: str
    direct_answer: str
    why_it_matters: str
    peer_signals: list[str]
    pilot_options: list[str]
    recommended_first_pilot: str
    data_needed: list[str]
    risks_to_control: list[str]
    technical_questions: list[str]


# ---------------------------------------------------------------------------
# Heuristic fallback (no LLM)
# ---------------------------------------------------------------------------


def _heuristic_answer(
    question: str, question_type: QuestionType, ctx: QAContext
) -> StructuredAnswer:
    """Assemble a reasonable answer from the stored context without an LLM call."""
    top_cards = ctx.opportunity_cards[:5]
    pilot_options = [f"{c.name}: {c.executive_summary}" for c in top_cards]
    first = top_cards[0].name if top_cards else "No opportunities identified yet"
    first_card = top_cards[0] if top_cards else None

    peer_signals = [
        f"{s.company} ({s.peer_type.value.replace('_', ' ')}): {s.signal}" for s in ctx.signals[:5]
    ]

    data_needed = (
        [first_card.recommended_first_step]
        if first_card and first_card.recommended_first_step
        else ["Internal data inventory required"]
    )

    risks = [
        f"{c.name}: risk level {c.risk_level.value}"
        for c in top_cards
        if c.risk_level.value in ("medium", "high")
    ][:3] or ["Evaluate change management and data privacy risks before launch"]

    technical_questions = [
        "What data sources are available and in what format?",
        "Which cloud/data platform is approved for AI workloads?",
        "Who owns the data pipeline and integration work?",
        "What security and access controls are required?",
        "What evaluation criteria will define success?",
    ]

    return StructuredAnswer(
        question=question,
        question_type=question_type.value,
        direct_answer=(
            f"Based on publicly available signals for {ctx.company_name}, "
            f"the most practical starting point is: {first}."
        ),
        why_it_matters=(
            "Enterprises that move early on practical, low-risk AI pilots build"
            " the institutional muscle needed for larger initiatives — and reduce"
            " the risk of being displaced by competitors who do."
        ),
        peer_signals=peer_signals or ["No specific peer signals found in public sources."],
        pilot_options=pilot_options,
        recommended_first_pilot=first,
        data_needed=data_needed,
        risks_to_control=risks,
        technical_questions=technical_questions,
    )


# ---------------------------------------------------------------------------
# LLM-based composer
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are an executive AI strategy advisor. A client has asked a question about \
their company's AI readiness and opportunities.

COMPANY: {company_name}
QUESTION TYPE: {question_type}
QUESTION: {question}

COMPANY CONTEXT:
{context_block}

PEER AND COMPETITIVE SIGNALS (from public sources only — do not invent):
{signals_block}

AVAILABLE PILOT OPTIONS (from curated library — only name these, do not invent new ones):
{pilots_block}

PRIOR Q&A IN THIS SESSION (for continuity — do not repeat verbatim):
{history_block}

Return a JSON object exactly matching this schema (no markdown fences):
{{
  "question": "<the original question>",
  "question_type": "<question_type value>",
  "direct_answer": "<2-4 sentence direct answer — specific, executive tone>",
  "why_it_matters": "<1-2 sentences on strategic importance for this company>",
  "peer_signals": ["<signal sentence with company name and peer type>", ...],
  "pilot_options": ["<PilotName: one-line description>", ...],
  "recommended_first_pilot": "<name of the single best first pilot>",
  "data_needed": ["<specific data asset or system needed>", ...],
  "risks_to_control": ["<specific risk with mitigation direction>", ...],
  "technical_questions": ["<question for the technical leader>", ...]
}}

Rules:
- peer_signals: only include signals backed by the provided list above; \
if none are relevant, use an empty list.
- pilot_options: only name pilots from the AVAILABLE PILOT OPTIONS list above.
- recommended_first_pilot: must be a name from pilot_options.
- Be specific. Do not hedge with "may", "could", "might" without context.
- Do not invent revenue figures, outcomes, quotes, or company facts.
"""


def _context_block(ctx: QAContext) -> str:
    if ctx.profile is None:
        return f"Company name: {ctx.company_name}. No research profile available yet."
    p = ctx.profile
    ident = p.company_identity
    ai = p.ai_and_digital_signals
    parts = [
        f"Industry: {ident.industry or 'unknown'}",
        f"Segments: {', '.join(ident.business_segments) or 'unknown'}",
        f"Strategic priorities: {', '.join(p.strategic_priorities.themes)}",
        f"Company AI initiatives: {', '.join(ai.company_ai_initiatives)}",
        f"Digital transformation signals: {', '.join(ai.digital_transformation_signals)}",
    ]
    return "\n".join(parts)


def _signals_block(ctx: QAContext) -> str:
    if not ctx.signals:
        return "No competitive signals found in public sources."
    return "\n".join(
        f"- {s.company} ({s.peer_type.value.replace('_', ' ')}): {s.signal} [{s.ai_area}]"
        for s in ctx.signals[:10]
    )


def _pilots_block(ctx: QAContext) -> str:
    return "\n".join(f"- {c.name}: {c.executive_summary}" for c in ctx.opportunity_cards[:8])


def _history_block(ctx: QAContext) -> str:
    if not ctx.prior_answers:
        return "None — this is the first question."
    lines: list[str] = []
    for turn in ctx.prior_answers[-3:]:
        question = turn.get("question", "")
        answer = turn.get("answer", {})
        direct = answer.get("direct_answer", "") if isinstance(answer, dict) else ""
        lines.append(f"- Q: {question}\n  A: {direct}")
    return "\n".join(lines)


def compose_answer(
    question: str,
    question_type: QuestionType,
    ctx: QAContext,
    llm=None,
) -> StructuredAnswer:
    """Produce a StructuredAnswer. Falls back to heuristics if LLM is None."""
    if llm is None:
        return _heuristic_answer(question, question_type, ctx)

    prompt = _PROMPT_TEMPLATE.format(
        company_name=ctx.company_name,
        question_type=question_type.value,
        question=question,
        context_block=_context_block(ctx),
        signals_block=_signals_block(ctx),
        pilots_block=_pilots_block(ctx),
        history_block=_history_block(ctx),
    )

    try:
        raw = llm.complete(prompt, max_tokens=2048)
        return parse_with_repair(raw, StructuredAnswer, llm.as_repair_fn())
    except Exception:
        log.warning("LLM answer generation failed; using heuristic fallback", exc_info=True)
        return _heuristic_answer(question, question_type, ctx)
