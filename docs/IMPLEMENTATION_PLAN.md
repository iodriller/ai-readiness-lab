<!--
ROLE OF THIS DOCUMENT
This is the canonical IMPLEMENTATION PLAN (the "how" and "when"): execution context,
guiding principles, architecture, a phase-by-phase build with concrete steps,
deliverables, acceptance criteria, tests, risks, and sequencing.
For the "what" and "why" — product vision, modes, and design — see docs/PRODUCT_SPEC.md.
-->

# AI Readiness Lab — Implementation Plan

**Status:** Phase 0 (scaffold) and Phase 1 (domain contracts) complete; Phase 2 next
**Last updated:** 2026-06-11
**Owner branch:** `claude/claude-md-best-practices-b31l7x`
**Companion docs:** `docs/PRODUCT_SPEC.md` (vision), `CLAUDE.md` (agent working rules)

---

## 1. Context — Where We Are Today (2026-06-11)

This repository currently contains **documentation only**: this plan, the product spec, and
`CLAUDE.md`. No application code, tests, or CI exist yet. We are at the very start of the
build.

The goal of this document is to turn the product vision in `docs/PRODUCT_SPEC.md` into an
**executable, sequenced plan**: concrete phases, the steps inside each phase, what "done"
means for each, how we verify it, and the order we build in so that every phase produces
something demonstrable.

**What we are trying to do, in one paragraph:** Build an executive-facing workbench that, from
just a company name and a role, performs structured public research, classifies competitors and
peers correctly, surfaces credible AI pilot opportunities, scores readiness, bridges executive
intent to technical discovery, and exports a polished, source-cited report — while hiding all
technical configuration behind a calm, near-zero-step UI.

**Why it must be more than a chatbot:** the differentiator is *structure* — structured research,
peer taxonomy, source-confidence scoring, opportunity ranking, readiness rubrics, and repeatable
report generation. Every phase below should protect that structure.

### 1.1 Guiding constraints (non-negotiable)

These come from `CLAUDE.md` and the product spec and apply to every phase:

1. **No hallucination.** Claims trace to retrieved sources with confidence notes. "Not found"
   beats a plausible guess.
2. **Minimal, tested code.** Smallest correct change; a focused test for anything non-trivial.
3. **Correct peer classification.** Mislabeling a peer is a correctness bug.
4. **Clean executive surface.** No infra/model/vector knobs in the default UI.
5. **Schema-validated boundaries.** All LLM/research output passes Pydantic validation + repair.

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│ Executive UI (React + Vite + TS)                                    │
│   intake → research progress → brief → opportunities → Q&A →        │
│   guided intake → scorecard → report preview/export                 │
└───────────────▲──────────────────────────────────┬─────────────────┘
                │ REST / SSE (progress)             │
┌───────────────┴──────────────────────────────────▼─────────────────┐
│ FastAPI Backend (Python 3.11+, Pydantic v2)                         │
│                                                                     │
│  Research Orchestrator   Opportunity Engine    Readiness Engine     │
│   - query planner         - use-case library    - question planner  │
│   - source collector      - company-fit scorer  - scoring rubrics   │
│   - source ranker         - pressure scorer      - blocker detector │
│   - company profiler      - opportunity ranker   - recommendation   │
│   - peer classifier                                                 │
│   - AI signal extractor   Technical Bridge      Report Generator    │
│                            - data reqs           - Jinja2 → MD       │
│                            - arch questions      - MD → PDF          │
│                            - tool boundaries     - source appendix   │
│                            - eval plan                               │
└───────────────┬──────────────────────────────────┬─────────────────┘
                │                                   │
        ┌───────▼────────┐               ┌──────────▼──────────┐
        │ LLM (Claude)   │               │ Web Search + Fetch  │
        │ structured JSON│               │ + citation tracking │
        │ schema+repair  │               └─────────────────────┘
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ SQLite (SQLAlchemy): projects, sources, profiles, reports │
        └──────────────────────────────────────────────────────────┘
```

### 2.1 Proposed repository layout

```
ai-readiness-lab/
├── CLAUDE.md
├── README.md
├── docs/
│   ├── PRODUCT_SPEC.md
│   └── IMPLEMENTATION_PLAN.md
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + routes
│   │   ├── config.py           # env-driven settings
│   │   ├── models/             # Pydantic schemas (domain contracts)
│   │   ├── db/                 # SQLAlchemy models + session
│   │   ├── research/           # orchestrator, search, ranking, extraction
│   │   ├── opportunity/        # use-case library + scoring
│   │   ├── readiness/          # rubrics + scoring + recommendation
│   │   ├── bridge/             # technical discovery generation
│   │   ├── report/             # templates + PDF export
│   │   └── llm/                # Claude client, structured-output, repair loop
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── routes/             # intake, progress, brief, opportunities, report
│   │   ├── components/
│   │   └── api/                # typed backend client
│   └── package.json
└── data/
    └── opportunity_library/    # versioned industry use-case definitions
```

### 2.2 Key technical decisions (and rationale)

| Decision | Choice | Why |
| --- | --- | --- |
| LLM | Claude (`claude-opus-4-8` default) via Anthropic SDK | Strongest reasoning for structured synthesis; latest capable model. |
| Structured output | Pydantic v2 schema + repair loop | Enforces the "validate at the boundary" rule; no raw JSON downstream. |
| Progress UX | Server-Sent Events from a job runner | Calm step-by-step progress without polling complexity. |
| Storage | SQLite + local project files | Zero-config for demo and single-tenant internal deploys. |
| PDF | Jinja2 → HTML → WeasyPrint (Playwright fallback) | Deterministic, templatable, no heavy runtime for the common case. |
| Packaging | Hosted web app first; Tauri desktop later | Fastest path to a demo; one-click local app is a follow-on. |

---

## 3. Cross-Cutting Concerns (apply to every phase)

- **Testing strategy.** Unit tests for schemas, scorers, ranking, and parsers (deterministic,
  no network). Contract tests for each LLM/research call using **recorded fixtures** (golden
  files) so the suite runs offline and fast. A small set of integration "smoke" tests behind a
  flag that hit live APIs. Target: every scorer/classifier has table-driven tests; every schema
  has a round-trip + repair test.
- **Evaluation harness.** Maintain a `tests/eval/` set of labeled companies (e.g. an oil & gas
  operator, a SaaS firm, a bank) with expected peer classifications and opportunity categories.
  Use it to catch regressions in research quality, not just code correctness.
- **Hallucination guardrails.** No claim is rendered without a `source_id` + confidence. A
  post-generation check rejects reports containing competitive/financial claims that lack a
  citation. Surface "insufficient public evidence" explicitly.
- **Observability.** Structured logs for every research step and LLM call (prompt hash, tokens,
  latency, validation pass/fail, repair count). Persist source records for auditability.
- **Security & secrets.** All keys via env vars; never committed. Enforce per-deploy data
  boundaries (a "private mode" flag that disables external calls beyond approved providers).
- **Cost control.** Cache search + fetch results per URL; cache company profiles; reuse research
  across modes within a project.
- **Definition of "done" per phase.** Code + focused tests passing + acceptance criteria met +
  docs/data updated. No phase is done on the strength of a demo alone.

---

## 4. Phased Build Plan

Each phase lists: **Objective**, **Implementation steps**, **Deliverables**, **Tests**,
**Acceptance criteria**, **Risks/mitigations**, **Depends on**. Phases are ordered so each one
leaves something runnable. Effort sizes are relative (S/M/L), not calendar commitments.

---

### Phase 0 — Repository Scaffold & Guardrails  · _Size: S_

**Objective.** Make the repo buildable and safe to work in before any product logic lands.

**Implementation steps.**
1. Create `backend/` (FastAPI app skeleton with `/health`) and `frontend/` (Vite + TS app).
2. Add `requirements.txt` / `package.json` with pinned core deps.
3. Add formatters/linters: `ruff` + `black` (Python), `eslint` + `prettier` (TS); add
   `pytest` and a single passing smoke test on each side.
4. Add `.gitignore` (`.env`, `__pycache__`, `node_modules`, `*.db`, build dirs).
5. Add `.env.example` documenting required vars (LLM key, search key) — no real secrets.
6. Add a **SessionStart hook** / CI workflow that installs deps and runs lint + tests.
7. Update `CLAUDE.md` Commands section with the now-real commands.

**Deliverables.** Running `/health` endpoint; Vite dev server; green lint+test on both sides; CI.
**Tests.** Backend health test; frontend renders root route; CI runs them.
**Acceptance.** `pytest` and `npm run build && npm run lint` pass locally and in CI from a clean clone.
**Risks.** Dependency drift → pin versions. **Depends on.** Nothing.

---

### Phase 1 — Domain Contracts (Schemas First)  · _Size: M_

**Objective.** Encode the spec's data models as the system's source of truth before behavior.

**Implementation steps.**
1. Translate `PRODUCT_SPEC.md` §8 and §15 into Pydantic v2 models: `Project`,
   `CompanyResearchPlan`, `SourceRecord`, `CompanyIntelligenceProfile`, `CompetitiveSignal`,
   `OpportunityCard`, `ReadinessScorecard`, and `PeerType` / enums.
2. Add a generic `Confidence` type and a `Citation`/`source_refs` convention used everywhere.
3. Add a **structured-output repair loop** utility: given a schema + raw model text, parse →
   validate → on failure, ask the model to fix against the validation errors (bounded retries).
4. Define SQLAlchemy tables mirroring the persisted models and a session/migration setup.
5. Generate TypeScript types from the Pydantic schemas (e.g. via OpenAPI) for the frontend client.

**Deliverables.** `backend/app/models/*`, `backend/app/db/*`, repair-loop util, generated TS types.
**Tests.** Round-trip serialization for every model; repair loop fixes a deliberately malformed
payload; DB create/read for each table.
**Acceptance.** Every spec model has a typed schema + a passing round-trip test; invalid LLM JSON
is repaired or rejected, never silently passed through.
**Risks.** Over-modeling → keep fields to what phases 2–9 actually consume; extend later.
**Depends on.** Phase 0.

---

### Phase 2 — Executive Shell (End-to-End Walking Skeleton)  · _Size: M_

**Objective.** A clickable, polished experience wired end-to-end on **mock** data — proves the UX
and the API contract before real research exists.

**Implementation steps.**
1. Intake screen: company name, role selector, mode selector (Discover / Evaluate / Compare /
   Brief) — no technical settings. Matches `PRODUCT_SPEC.md` §4.2.
2. `POST /projects` creates a project; backend returns a `project_id` and status.
3. Research progress screen driven by **SSE** emitting the spec's step list (§4.3), backed by a
   mock job that sleeps between steps.
4. First-result "AI Readiness Brief" screen rendered from a static sample profile (§4.4).
5. Opportunity cards list + report-preview placeholder.
6. Typed API client on the frontend using the generated types from Phase 1.

**Deliverables.** Navigable flow: intake → progress → brief → opportunities → report placeholder.
**Tests.** Frontend route/render tests; backend project-creation + SSE contract test.
**Acceptance.** A non-developer can click through the whole journey with mock data; no technical
knobs are visible by default.
**Risks.** UX scope creep → ship the flow, defer polish. **Depends on.** Phases 0–1.

---

### Phase 3 — Research Orchestrator  · _Size: L_

**Objective.** Replace mock research with real, structured, source-aware company research.

**Implementation steps.**
1. **Query planner.** From a company name + mode, generate the query set from `PRODUCT_SPEC.md`
   §7.3 (company / competitor / industry templates).
2. **Source collector.** Wrap the web search + fetch APIs; dedupe by URL; capture title,
   publisher, date, snippet.
3. **Source ranker.** Implement the confidence hierarchy (§7.4: official/filing/news/analyst →
   vendor/blog → unsourced). Store `SourceRecord`s with `source_type` + `confidence`.
4. **Company profiler.** Resolve identity (name, ticker, website, HQ), company type, segments,
   financial snapshot, strategic priorities — each field carrying `source_refs` + confidence.
5. **AI-signal extractor.** Pull company AI/digital/automation/data/partnership/job-posting
   signals into the profile.
6. Wire the orchestrator into the SSE progress steps so the UI reflects real work.
7. Cache results per URL and per company to control cost.

**Deliverables.** `given a company name → CompanyIntelligenceProfile` populated from live sources.
**Tests.** Query planner is deterministic (table-driven). Ranker classifies known URLs correctly.
Profiler/extractor tested against **recorded** search/LLM fixtures (golden profiles for 2–3
companies). One flagged live smoke test.
**Acceptance.** For a real public company, the app produces a structured profile where every
non-trivial claim has at least one `source_ref` and a confidence value; the appendix can list them.
**Risks.** Flaky/low-quality sources → enforce min-source requirements (§15.2) and downgrade
confidence; never fabricate to fill a field. **Depends on.** Phases 1–2.

---

### Phase 4 — Peer Taxonomy & Competitive Intelligence  · _Size: M_

**Objective.** Prevent bad comparisons — the credibility differentiator (`PRODUCT_SPEC.md` §3.3).

**Implementation steps.**
1. Peer **classifier**: given the subject company + candidate companies, assign `peer_type`
   (direct_competitor / operator_peer / service_company / technology_vendor / supplier /
   customer / adjacent_benchmark) **with a stated reason**.
2. Competitive **signal extractor**: for each peer, extract AI/digital signals as
   `CompetitiveSignal` with `peer_type`, `ai_area`, `business_relevance`, `fomo_strength`,
   `source_ids`, `confidence`.
3. Relevance/confidence scoring per signal; suppress low-confidence, unsourced signals.
4. Expose an explanation API: "why is X a vendor/benchmark vs a direct competitor?"

**Deliverables.** Peer taxonomy + labeled competitive signals attached to the profile.
**Tests.** **Eval set** asserting the spec's oil & gas example (Oxy = operator; SLB/Halliburton/
Baker Hughes/NOV/Weatherford = service/technology benchmarks, not direct operator competitors);
similar fixtures for one SaaS and one bank.
**Acceptance.** The app correctly labels and *explains* each peer relationship; a service company
is never surfaced as a direct operator competitor.
**Risks.** Industry edge cases → keep the reason field and let it be reviewable; expand eval set.
**Depends on.** Phase 3.

---

### Phase 5 — AI Opportunity Map  · _Size: M_

**Objective.** Turn research into 5–10 ranked, credible opportunity cards.

**Implementation steps.**
1. Encode the **opportunity library** (`PRODUCT_SPEC.md` §6) as versioned data in
   `data/opportunity_library/` (category → use cases, with default risk/feasibility hints).
2. **Company-fit scorer**: map profile (segments, signals, pain areas) to library categories.
3. **Competitive-pressure scorer**: fold in peer signals (§4) per category.
4. **Opportunity ranker**: combine value / feasibility / risk / readiness into a ranking.
5. Generate `OpportunityCard`s with FOMO-aware-but-credible summaries (constructive urgency,
   no unsupported claims — §3.2).

**Deliverables.** Ranked opportunity cards rendered in the UI from real research.
**Tests.** Scorers are deterministic table tests; ranker ordering tests; a guard test that
rejects any card whose competitive_pressure text lacks a backing signal/source.
**Acceptance.** For a researched company, the app emits 5–10 cards with credible "why now" text
tied to evidence. **Risks.** Generic cards → require company-specific hooks in each summary.
**Depends on.** Phases 3–4.

---

### Phase 6 — Open-Ended Strategy Q&A  · _Size: M_

**Objective.** Answer executive questions in the spec's **structured** format (§10), not as a
generic chatbot.

**Implementation steps.**
1. Question classifier (opportunity-seeking / comparison / risk / sequencing / technical).
2. Context retriever pulling profile + peer signals + industry patterns + opportunity library +
   prior answers in the project.
3. Structured answer composer producing: direct answer → why it matters → peer/industry signals →
   practical pilot options → recommended first pilot → data needed → risks to control →
   questions for technical leaders → export option.
4. Wire into a chat surface within a project.

**Deliverables.** A Q&A surface that returns structured, company-aware, sourced answers.
**Tests.** Classifier table tests; composer output-shape tests; a fixture replicating the spec's
"What can we do for drilling engineers?" example shape (§10).
**Acceptance.** Asking a drilling-engineer question yields specific, structured, company-aware
pilots and technical-leader questions — not generic prose. **Depends on.** Phases 3–5.

---

### Phase 7 — Guided Pilot Intake  · _Size: M_

**Objective.** Narrow one selected opportunity into a concrete pilot profile via short,
plain-English questions (`PRODUCT_SPEC.md` §11.1).

**Implementation steps.**
1. Question templates per opportunity category (users / workflow / "never do" / data sources /
   success outcome / unacceptable risk / approver).
2. Intake flow (8–12 questions) with sensible inference of unanswered fields.
3. Assemble a `PilotProfile` consumed by scoring (Phase 8) and the report (Phase 10).

**Deliverables.** Guided intake producing a complete pilot profile from a selected card.
**Tests.** Template selection per category; inference fills gaps without inventing facts; profile
completeness check. **Acceptance.** A user answers 8–12 questions and gets a complete pilot
profile in executive language. **Depends on.** Phase 5.

---

### Phase 8 — Readiness Scoring Engine  · _Size: M_

**Objective.** Produce a credible `ReadinessScorecard` with strengths, blockers, and next actions
(`PRODUCT_SPEC.md` §9).

**Implementation steps.**
1. Implement pilot-level dimensions (business value, workflow clarity, data readiness, risk
   controls, evaluation readiness, integration feasibility, operational ownership, user adoption).
2. Define **explicit rubrics** per dimension (what a low/medium/high looks like) so scores are
   explainable and reproducible.
3. Compute overall score + map to recommendation type (proceed / limited pilot / needs discovery
   / defer / not recommended).
4. Blocker detector + strengths + next-actions generator. Allow manual override of any dimension.

**Deliverables.** Scorecard rendered in UI and embedded in the report.
**Tests.** Rubric → score mapping is deterministic; same inputs always yield the same score;
recommendation thresholds tested; override path tested.
**Acceptance.** The scorecard explains *why* each dimension scored as it did and is stable across
runs for identical inputs. **Risks.** Score hand-waving → rubrics must be code, not vibes.
**Depends on.** Phase 7.

---

### Phase 9 — Technical Bridge Generator  · _Size: S–M_

**Objective.** Translate executive intent into a technical discovery checklist without cluttering
the executive surface (`PRODUCT_SPEC.md` §11.2).

**Implementation steps.**
1. Data-requirements generator (where docs live, exports/APIs, access controls, platform).
2. Architecture-question generator (cloud target, approved LLM provider, local-model need, data
   egress policy, observability/eval tooling, gateway/integration layer).
3. Tool/agent **boundary** generator (what the assistant may/may not do).
4. Evaluation-plan generator (eval set source, thresholds before rollout).
5. Compose a "questions for technical leaders" checklist.

**Deliverables.** A technical appendix payload attached to the pilot.
**Tests.** Generators produce category-appropriate, non-empty checklists; boundaries reflect the
opportunity's risk level. **Acceptance.** The report's technical appendix is specific and useful
to a technical leader. **Depends on.** Phases 7–8.

---

### Phase 10 — Report Generator (the Core Artifact)  · _Size: L_

**Objective.** Produce the polished, source-cited executive report (`PRODUCT_SPEC.md` §12) — the
product's main deliverable.

**Implementation steps.**
1. Jinja2 Markdown templates for the 13-section structure (§12.2): exec summary → company context
   → competitive/peer signals → opportunity map → selected pilot → readiness scorecard → data
   requirements → tool/agent boundaries → risk register → evaluation plan → 30/60/90 roadmap →
   technical-leader questions → **sources & confidence appendix**.
2. MD → PDF export (WeasyPrint; Playwright fallback) with clean executive styling.
3. **Citation enforcement pass**: fail/flag any competitive or financial claim lacking a
   `source_id`; render confidence notes in the appendix.
4. Report-type variants (Exec Brief / Competitive Landscape / Pilot Recommendation / Board Summary).
5. Report preview in UI + download.

**Deliverables.** Downloadable, professional PDF + Markdown for a real company.
**Tests.** Template renders for a fixture project; PDF generates without error; citation-enforcement
test rejects a planted uncited claim; snapshot test on the Markdown.
**Acceptance.** A user exports a polished PDF whose every competitive/financial claim is cited and
whose appendix lists sources + confidence. **Risks.** PDF rendering quirks → keep HTML/CSS simple
and tested. **Depends on.** Phases 3–9.

---

### Phase 11 — Packaging, Demo & Hardening  · _Size: M_

**Objective.** Make it usable by non-developers and trustworthy enough to demo.

**Implementation steps.**
1. Hosted demo deployment (single command / container) with env-based config.
2. Seed **sample companies** and **example reports** for instant demos.
3. End-to-end happy-path test (intake → report) behind a live-API flag.
4. Error/empty-state handling (research found little → say so honestly, don't fabricate).
5. Optional: Tauri desktop packaging for one-click local launch.
6. README quick-start for both users and developers.

**Deliverables.** A shareable demo, sample artifacts, and a clean first-run experience.
**Tests.** E2E smoke test; sample-company reports generate successfully in CI (recorded fixtures).
**Acceptance.** A non-technical user launches the app and generates a report without touching a
terminal. **Depends on.** Phases 2–10.

---

## 5. Build Order (Critical Path)

```
P0 Scaffold ─▶ P1 Schemas ─▶ P2 Shell(mock) ─▶ P3 Research ─▶ P4 Peers ─▶ P5 Opportunities
                                                   │                          │
                                                   └────────▶ P6 Q&A ◀────────┘
P5 ─▶ P7 Pilot Intake ─▶ P8 Scoring ─▶ P9 Tech Bridge ─▶ P10 Report ─▶ P11 Package/Demo
```

P6 (Q&A) can proceed in parallel with P7–P8 once P5 lands. P10 depends on P3–P9 being available.

---

## 6. Milestones (Demonstrable Increments)

| Milestone | Phases | What you can show |
| --- | --- | --- |
| **M1 — Clickable shell** | P0–P2 | Full UX on mock data; the product story in 30 seconds. |
| **M2 — Real research brief** | P3–P4 | A live, sourced company + peer brief with correct peer labels. |
| **M3 — Opportunities & Q&A** | P5–P6 | Ranked opportunity cards and structured strategy answers. |
| **M4 — Pilot to scorecard** | P7–P9 | Guided intake → readiness scorecard → technical appendix. |
| **M5 — Exportable report (MVP)** | P10 | Polished, cited PDF for a real company. |
| **M6 — Demo-ready** | P11 | One-click launch, sample companies, example reports. |

**MVP = M5**, matching `PRODUCT_SPEC.md` §18 Definition of Done.

---

## 7. MVP Definition of Done (traceable to spec §18)

The MVP ships when a user can, with **no developer setup**:
1. Enter a company name and role.  2. Get real public-company research.
3. See correct company-type and peer classification.  4. See relevant AI/digital signals.
5. Get credible opportunity cards.  6. Ask open-ended strategy questions and get structured answers.
7. Turn one opportunity into a guided pilot plan.  8. Get a readiness score with reasons.
9. Get technical-leader questions.  10. Export a polished, **source-cited** PDF.
11. Never see technical configuration by default.  12. See sources + confidence in an appendix.
13. Trust that no claim is fabricated (citation-enforcement passes).

---

## 8. Risks & Mitigations (program-level)

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hallucinated facts | Destroys credibility | Citation enforcement; "not found" over guessing; eval set. |
| Bad peer comparisons | Destroys credibility | Dedicated classifier + reasons + eval fixtures (Phase 4). |
| Flaky external APIs | Slow/broken research | Caching, retries, recorded fixtures for tests, min-source rules. |
| Scope creep / over-build | Slips MVP | Minimal-code rule; ship walking skeleton early; phase gates. |
| LLM output drift | Silent breakage | Schema validation + repair loop; golden-file contract tests. |
| Cost blow-up | Unsustainable demo | Cache search/fetch/profiles; reuse research across modes. |
| PDF rendering fragility | Broken core artifact | Simple, tested HTML/CSS; Playwright fallback path. |

---

## 9. Open Questions (decide before the dependent phase)

1. **Web search + fetch provider** — which API(s)? (Blocks Phase 3.)
2. **SEC/filings retrieval** — in MVP or post-MVP? (Affects Phase 3 financial snapshot depth.)
3. **Private/internal mode** — required for first customers? (Affects Phase 3/9 LLM + egress.)
4. **Auth & multi-tenant** — single-tenant demo first, or auth from the start? (Affects Phase 0/11.)
5. **Desktop packaging timing** — Tauri in MVP or as a fast follow? (Affects Phase 11.)

These are the user-facing/strategic decisions; everything else has a sensible default chosen above.

---

## 10. How to Use This Plan with Claude Code

- Work **one phase at a time**; finish its acceptance criteria before starting the next.
- Stay on branch `claude/claude-md-best-practices-b31l7x` unless told otherwise.
- Follow `CLAUDE.md`: minimal code, tests for non-trivial changes, no hallucinated facts,
  schema-validated boundaries, correct peer labels.
- When a phase changes a real command or decision, update `CLAUDE.md` (Commands) and the relevant
  section here so the docs never lie about the code.
