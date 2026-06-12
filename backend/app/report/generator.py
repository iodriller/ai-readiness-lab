"""Executive report generator — Markdown + PDF (spec §4.4, §13).

Renders the AI Readiness Brief (narrative + opportunity cards + any Q&A) into two
shareable formats.

Markdown keeps full Unicode. The PDF uses fpdf2 (pure-Python, no native deps, bundles
cleanly) with Liberation Sans TTF so em-dashes, curly quotes, and other Unicode characters
render natively. The font files live at app/fonts/ and are bundled by PyInstaller via the
collect_data_files("app") hook in the spec.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from app.api.schemas import BriefResponse
from app.pilot.models import PilotPlan

_NARRATIVE = [
    ("What matters", "what_matters"),
    ("Competitive pressure", "competitive_pressure"),
    ("The opening", "the_opening"),
    ("Recommended next move", "recommended_next_move"),
]

# ---------------------------------------------------------------------------
# Font resolution
# ---------------------------------------------------------------------------


def _fonts_dir() -> Path:
    """Return the fonts directory whether running live or frozen under PyInstaller."""
    import sys

    if getattr(sys, "frozen", False):
        # PyInstaller unpacks app/fonts/ into _MEIPASS/app/fonts
        return Path(sys._MEIPASS) / "app" / "fonts"  # type: ignore[attr-defined]
    return Path(__file__).parent.parent / "fonts"


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def render_markdown(
    brief: BriefResponse,
    qa_history: list[dict] | None = None,
    pilot: PilotPlan | None = None,
) -> str:
    today = datetime.date.today().strftime("%B %Y")
    lines: list[str] = [
        f"# AI Readiness Brief: {brief.company_name}",
        "",
        f"_Generated {today}_",
        "",
    ]
    if brief.is_sample:
        lines += ["> _Illustrative sample — add an Anthropic API key for live research._", ""]

    lines += ["## §1  Executive Summary", ""]
    for title, field in _NARRATIVE:
        lines += [f"### {title}", "", getattr(brief, field), ""]

    lines += ["## §2  AI Opportunity Map", ""]
    for i, card in enumerate(brief.opportunities, 1):
        lines += [
            f"### §2.{i}  {card.name}",
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

    section = 3
    if pilot is not None:
        sc = pilot.scorecard
        lines += [
            f"## §{section}  Selected Pilot Recommendation",
            "",
            f"**{pilot.profile.opportunity_name}**",
            "",
        ]
        section += 1
        lines += [
            f"## §{section}  Readiness Scorecard",
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
        section += 1
        lines += [f"## §{section}  Technical Leader Questions", ""]
        for group in pilot.technical_checklist:
            lines += [f"### {group.category}", *[f"- {item}" for item in group.items], ""]
        section += 1

    if qa_history:
        lines += [f"## §{section}  Strategy Q&A", ""]
        for turn in qa_history:
            answer = turn.get("answer", {})
            lines += [f"### Q: {turn.get('question', '')}", "", answer.get("direct_answer", ""), ""]
            if answer.get("recommended_first_pilot"):
                lines += [f"**Recommended first pilot:** {answer['recommended_first_pilot']}", ""]
        section += 1

    if brief.sources:
        lines += [f"## §{section}  Sources & Confidence", ""]
        for src in brief.sources:
            label = src.title or src.url
            lines += [f"- [{label}]({src.url}) — {src.source_type} ({src.confidence:.0%})"]
        lines += [""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------


def render_pdf(
    brief: BriefResponse,
    qa_history: list[dict] | None = None,
    pilot: PilotPlan | None = None,
) -> bytes:
    from fpdf import FPDF

    fonts = _fonts_dir()
    use_ttf = (fonts / "LiberationSans-Regular.ttf").exists()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    if use_ttf:
        pdf.add_font("Sans", "", str(fonts / "LiberationSans-Regular.ttf"))
        pdf.add_font("Sans", "B", str(fonts / "LiberationSans-Bold.ttf"))
        pdf.add_font("Sans", "I", str(fonts / "LiberationSans-Italic.ttf"))
        sans = "Sans"
    else:
        sans = "Helvetica"

    today = datetime.date.today().strftime("%B %Y")

    # ------------------------------------------------------------------
    # Cover page
    # ------------------------------------------------------------------
    pdf.add_page()

    # Dark background
    pdf.set_fill_color(15, 30, 60)
    pdf.rect(0, 0, 210, 297, "F")

    # Accent bar at top
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 0, 210, 6, "F")

    # Labels
    pdf.set_text_color(100, 160, 255)
    pdf.set_font(sans, "B", 9)
    pdf.set_xy(20, 30)
    pdf.cell(0, 6, "AI READINESS BRIEF")

    # Company name
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(sans, "B", 30)
    pdf.set_xy(20, 45)
    pdf.multi_cell(170, 13, brief.company_name)

    # Date + recommendation badge
    y = pdf.get_y() + 6
    rec_label = ""
    if pilot is not None:
        rec_label = f"  ·  {pilot.scorecard.recommendation.value.replace('_', ' ').title()}"
    pdf.set_text_color(200, 220, 255)
    pdf.set_font(sans, "", 13)
    pdf.set_xy(20, y)
    pdf.multi_cell(170, 7, f"{today}{rec_label}")

    # Readiness score if available
    if pilot is not None:
        score = pilot.scorecard.overall_score
        y = pdf.get_y() + 10
        pdf.set_fill_color(30, 50, 90)
        pdf.set_draw_color(59, 130, 246)
        pdf.rect(20, y, 80, 28, "FD")
        pdf.set_text_color(100, 160, 255)
        pdf.set_font(sans, "B", 9)
        pdf.set_xy(24, y + 4)
        pdf.cell(0, 5, "PILOT READINESS")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(sans, "B", 22)
        pdf.set_xy(24, y + 11)
        pdf.cell(0, 10, f"{score}/100")

    # Sample notice
    if brief.is_sample:
        pdf.set_text_color(255, 200, 60)
        pdf.set_font(sans, "I", 9)
        pdf.set_xy(20, 250)
        pdf.multi_cell(170, 5, "Illustrative sample — add an Anthropic API key for live research.")

    # Footer
    pdf.set_text_color(60, 90, 140)
    pdf.set_font(sans, "", 8)
    pdf.set_xy(20, 275)
    pdf.cell(0, 5, "Generated by AI Readiness Lab")

    # Accent bar at bottom
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 291, 210, 6, "F")

    # ------------------------------------------------------------------
    # Body pages
    # ------------------------------------------------------------------
    pdf.add_page()

    def h1(text: str) -> None:
        pdf.set_font(sans, "B", 18)
        pdf.set_text_color(15, 30, 60)
        pdf.multi_cell(0, 9, text)
        pdf.ln(2)
        # Underline rule
        pdf.set_draw_color(59, 130, 246)
        pdf.set_line_width(0.5)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.line(x, y, x + 170, y)
        pdf.ln(5)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.2)

    def h2(text: str) -> None:
        pdf.set_font(sans, "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.multi_cell(0, 7, text)
        pdf.ln(2)

    def body(text: str) -> None:
        pdf.set_font(sans, "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 6, text)
        pdf.ln(2)

    def label_value(label: str, value: str) -> None:
        pdf.set_font(sans, "B", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, f"{label}:")
        pdf.set_x(pdf.l_margin + 6)
        pdf.set_font(sans, "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5, value)
        pdf.ln(1)

    # §1 Executive Summary
    h1("§1  Executive Summary")
    for title, field in _NARRATIVE:
        h2(title)
        body(getattr(brief, field))

    # §2 AI Opportunity Map
    pdf.add_page()
    h1("§2  AI Opportunity Map")
    for i, card in enumerate(brief.opportunities, 1):
        h2(f"§2.{i}  {card.name}")
        pdf.set_font(sans, "I", 10)
        pdf.set_text_color(100, 100, 140)
        pdf.multi_cell(0, 5, card.category)
        pdf.ln(1)
        body(card.executive_summary)
        label_value("Why now", card.why_now)
        label_value("Competitive pressure", card.competitive_pressure)
        vfr = (
            f"{card.business_value.value} / {card.pilot_feasibility.value}"
            f" / {card.risk_level.value}"
            f"  —  Time to pilot: {card.time_to_pilot.value.replace('_', ' ')}"
        )
        label_value("Value / Feasibility / Risk", vfr)
        label_value("First step", card.recommended_first_step)
        pdf.ln(4)

    section = 3
    if pilot is not None:
        sc = pilot.scorecard
        pdf.add_page()
        h1(f"§{section}  Selected Pilot Recommendation")
        h2(pilot.profile.opportunity_name)
        body(pilot.profile.company_name or "")
        section += 1

        h1(f"§{section}  Readiness Scorecard")
        pdf.set_font(sans, "B", 14)
        pdf.set_text_color(15, 30, 60)
        pdf.cell(0, 8, f"Overall readiness: {sc.overall_score}/100")
        pdf.ln(2)
        rec_text = sc.recommendation.value.replace("_", " ").title()
        pdf.set_font(sans, "B", 11)
        pdf.set_text_color(59, 130, 246)
        pdf.multi_cell(0, 6, f"Recommendation: {rec_text}")
        pdf.ln(4)

        for dim, value in sc.dimensions.model_dump().items():
            dim_label = dim.replace("_", " ").title()
            bar_w = int(value * 1.4)  # max 140 pt for 100
            pdf.set_font(sans, "", 9)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(55, 5, dim_label)
            if value >= 80:
                bar_color = (34, 197, 94)
            elif value >= 50:
                bar_color = (245, 158, 11)
            else:
                bar_color = (239, 68, 68)
            pdf.set_fill_color(230, 235, 245)
            pdf.rect(pdf.get_x(), pdf.get_y(), 140, 4, "F")
            pdf.set_fill_color(*bar_color)
            pdf.rect(pdf.get_x(), pdf.get_y(), bar_w, 4, "F")
            pdf.set_text_color(40, 40, 40)
            pdf.set_font(sans, "B", 9)
            pdf.cell(140, 5, "", ln=0)
            pdf.cell(15, 5, str(value), align="R")
            pdf.ln(6)

        pdf.ln(3)
        if sc.strengths:
            h2("Strengths")
            for s in sc.strengths:
                body(f"+ {s}")
        if sc.blockers:
            h2("Blockers")
            for b in sc.blockers:
                body(f"- {b}")
        if sc.next_actions:
            h2("Next Actions")
            for a in sc.next_actions:
                body(f"→ {a}")
        section += 1

        pdf.add_page()
        h1(f"§{section}  Technical Leader Questions")
        for group in pilot.technical_checklist:
            h2(group.category)
            for item in group.items:
                body(f"□  {item}")
            pdf.ln(2)
        section += 1

    if qa_history:
        pdf.add_page()
        h1(f"§{section}  Strategy Q&A")
        for turn in qa_history:
            answer = turn.get("answer", {})
            h2(f"Q: {turn.get('question', '')}")
            body(answer.get("direct_answer", ""))
            if answer.get("recommended_first_pilot"):
                label_value("Recommended first pilot", answer["recommended_first_pilot"])
            pdf.ln(3)
        section += 1

    if brief.sources:
        pdf.add_page()
        h1(f"§{section}  Sources & Confidence")
        for src in brief.sources:
            pdf.set_font(sans, "B", 9)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5, src.title or src.url)
            pdf.set_font(sans, "", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 4, f"{src.url}  —  {src.source_type} ({src.confidence:.0%})")
            pdf.ln(2)

    out = pdf.output()
    return bytes(out)
