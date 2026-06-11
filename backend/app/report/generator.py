"""Executive report generator — Markdown + PDF (spec §4.4, §13).

Renders the AI Readiness Brief (narrative + opportunity cards + any Q&A) into two
shareable formats. Markdown keeps full Unicode; the PDF uses fpdf2 (pure-Python,
no native deps, bundles cleanly) with text sanitized to the core-font charset.
"""

from __future__ import annotations

from app.api.schemas import BriefResponse
from app.pilot.models import PilotPlan

_NARRATIVE = [
    ("What matters", "what_matters"),
    ("Competitive pressure", "competitive_pressure"),
    ("The opening", "the_opening"),
    ("Recommended next move", "recommended_next_move"),
]


def render_markdown(
    brief: BriefResponse,
    qa_history: list[dict] | None = None,
    pilot: PilotPlan | None = None,
) -> str:
    lines: list[str] = [f"# AI Readiness Brief: {brief.company_name}", ""]
    if brief.is_sample:
        lines += ["> _Illustrative sample — add an Anthropic API key for live research._", ""]

    for title, field in _NARRATIVE:
        lines += [f"## {title}", "", getattr(brief, field), ""]

    lines += ["## AI Opportunity Map", ""]
    for card in brief.opportunities:
        lines += [
            f"### {card.name}",
            f"_{card.category}_",
            "",
            card.executive_summary,
            "",
            f"- **Why now:** {card.why_now}",
            f"- **Competitive pressure:** {card.competitive_pressure}",
            f"- **Business value:** {card.business_value.value}  ·  "
            f"**Feasibility:** {card.pilot_feasibility.value}  ·  "
            f"**Risk:** {card.risk_level.value}",
            f"- **Time to pilot:** {card.time_to_pilot.value.replace('_', ' ')}",
            f"- **First step:** {card.recommended_first_step}",
            "",
        ]

    if pilot is not None:
        sc = pilot.scorecard
        lines += [
            "## Selected Pilot Recommendation",
            "",
            f"**{pilot.profile.opportunity_name}**",
            "",
            "## Readiness Scorecard",
            "",
            f"**Overall readiness:** {sc.overall_score}/100  ·  "
            f"**Recommendation:** {sc.recommendation.value.replace('_', ' ')}",
            "",
        ]
        for dim, value in sc.dimensions.model_dump().items():
            lines.append(f"- {dim.replace('_', ' ').title()}: {value}/100")
        lines.append("")
        if sc.strengths:
            lines += ["**Strengths:**", *[f"- {s}" for s in sc.strengths], ""]
        if sc.blockers:
            lines += ["**Blockers:**", *[f"- {b}" for b in sc.blockers], ""]
        if sc.next_actions:
            lines += ["**Next actions:**", *[f"- {a}" for a in sc.next_actions], ""]
        lines += ["## Technical Leader Questions", ""]
        for group in pilot.technical_checklist:
            lines += [f"### {group.category}", *[f"- {item}" for item in group.items], ""]

    if qa_history:
        lines += ["## Strategy Q&A", ""]
        for turn in qa_history:
            answer = turn.get("answer", {})
            lines += [f"### Q: {turn.get('question', '')}", "", answer.get("direct_answer", ""), ""]
            if answer.get("recommended_first_pilot"):
                lines += [f"**Recommended first pilot:** {answer['recommended_first_pilot']}", ""]

    if brief.sources:
        lines += ["## Sources & confidence", ""]
        for src in brief.sources:
            label = src.title or src.url
            lines += [f"- [{label}]({src.url}) — {src.source_type} ({src.confidence:.0%})"]
        lines += [""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "·": "-",
    "•": "-",
    "…": "...",
    "→": "->",
}


def _safe(text: str) -> str:
    """Core PDF fonts are latin-1; map common Unicode punctuation, drop the rest."""
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


def render_pdf(
    brief: BriefResponse,
    qa_history: list[dict] | None = None,
    pilot: PilotPlan | None = None,
) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def heading(text: str, size: int, gap: int = 2) -> None:
        pdf.set_font("Helvetica", "B", size)
        pdf.multi_cell(0, size * 0.6, _safe(text))
        pdf.ln(gap)

    def body(text: str) -> None:
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _safe(text))
        pdf.ln(1)

    heading(f"AI Readiness Brief: {brief.company_name}", 20, 3)
    if brief.is_sample:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 120, 0)
        pdf.multi_cell(
            0, 5, _safe("Illustrative sample - add an Anthropic API key for live research.")
        )
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    for title, field in _NARRATIVE:
        heading(title, 13)
        body(getattr(brief, field))

    heading("AI Opportunity Map", 16, 3)
    for card in brief.opportunities:
        heading(f"{card.name}  ({card.category})", 12)
        body(card.executive_summary)
        body(
            f"Why now: {card.why_now}\n"
            f"Competitive pressure: {card.competitive_pressure}\n"
            f"Value: {card.business_value.value} | Feasibility: {card.pilot_feasibility.value} | "
            f"Risk: {card.risk_level.value} | Time to pilot: "
            f"{card.time_to_pilot.value.replace('_', ' ')}\n"
            f"First step: {card.recommended_first_step}"
        )

    if pilot is not None:
        sc = pilot.scorecard
        heading("Selected Pilot Recommendation", 16, 3)
        body(pilot.profile.opportunity_name)
        heading("Readiness Scorecard", 16, 3)
        body(
            f"Overall readiness: {sc.overall_score}/100 | "
            f"Recommendation: {sc.recommendation.value.replace('_', ' ')}"
        )
        body(
            "\n".join(
                f"{dim.replace('_', ' ').title()}: {value}/100"
                for dim, value in sc.dimensions.model_dump().items()
            )
        )
        if sc.strengths:
            body("Strengths:\n" + "\n".join(f"- {s}" for s in sc.strengths))
        if sc.blockers:
            body("Blockers:\n" + "\n".join(f"- {b}" for b in sc.blockers))
        if sc.next_actions:
            body("Next actions:\n" + "\n".join(f"- {a}" for a in sc.next_actions))
        heading("Technical Leader Questions", 16, 3)
        for group in pilot.technical_checklist:
            heading(group.category, 12)
            body("\n".join(f"- {item}" for item in group.items))

    if qa_history:
        heading("Strategy Q&A", 16, 3)
        for turn in qa_history:
            answer = turn.get("answer", {})
            heading(f"Q: {turn.get('question', '')}", 12)
            body(answer.get("direct_answer", ""))

    if brief.sources:
        heading("Sources & confidence", 16, 3)
        for src in brief.sources:
            body(f"- {src.title or src.url} ({src.source_type}, {src.confidence:.0%})\n  {src.url}")

    out = pdf.output()
    return bytes(out)
