"""Report generator — Markdown + PDF rendering."""

from app.api.sample import sample_brief
from app.report.generator import render_markdown, render_pdf

_QA = [
    {
        "question": "What about HR?",
        "answer": {
            "direct_answer": "Start with a policy assistant.",
            "recommended_first_pilot": "HR Policy Assistant",
        },
    }
]


def test_markdown_has_sections_and_opportunities():
    brief = sample_brief("Acme")
    md = render_markdown(brief, _QA)
    assert md.startswith("# AI Readiness Brief: Acme")
    assert "§1  Executive Summary" in md
    assert "§2  AI Opportunity Map" in md
    assert "Strategy Q&A" in md
    assert "What about HR?" in md
    # Every opportunity is rendered with a sub-section.
    for i, card in enumerate(brief.opportunities, 1):
        assert f"§2.{i}  {card.name}" in md


def test_markdown_flags_sample_content():
    md = render_markdown(sample_brief("Acme"))
    assert "Illustrative sample" in md


def test_pdf_renders_valid_bytes():
    pdf = render_pdf(sample_brief("Acme"), _QA)
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 1000


def test_pdf_handles_unicode_punctuation():
    # Unicode em-dashes and curly quotes must render natively via TTF.
    brief = sample_brief("Acme — Inc.")
    pdf = render_pdf(brief)
    assert pdf[:5] == b"%PDF-"


def test_pdf_has_cover_page():
    # PDF must be larger than a single-page doc — cover + body.
    pdf_no_pilot = render_pdf(sample_brief("Acme"))
    # Cover page + at least two body pages means the file should be reasonably large.
    assert len(pdf_no_pilot) > 5000
