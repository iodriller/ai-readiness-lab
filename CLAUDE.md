# CLAUDE.md — AI Readiness Lab

> **IMPORTANT — Session log rule:** At the end of every AI turn, update the
> "Session Log" section below with: what was done, gaps or bugs found, what
> remains in the current phase, and what the next step is. Most-recent entry
> goes at the top. Be specific — a future agent or developer should be able to
> pick up cold from this log.

---

## Session Log (most recent first)

### 2026-06-11 · Session 2 — Phase 0: Repository Scaffold

**Done:**
- Phase 0 fully built: FastAPI `/health` skeleton, Vite + React + TypeScript
  frontend, `ruff`/`pytest` on the backend, `eslint`/`tsc` on the frontend.
- `.gitignore`, `.env.example`, `backend/pyproject.toml`, all test/config files.
- `CLAUDE.md` updated with live commands and this session-log rule.
- All backend tests passing (`pytest`); frontend build + typecheck + lint passing.
- Committed and pushed to `claude/claude-md-best-practices-b31l7x`.

**Gaps / bugs found:**
- No CI workflow yet (GitHub Actions file). Phase 0 acceptance requires CI;
  to be added in a follow-up commit once confirmed the environment supports it.
- `requirements.txt` pins versions that were current Jan 2026; verify they
  resolve cleanly in the target Python environment before cutting a release.
- Frontend uses plain CSS (no design system). That's fine for Phase 0 but will
  need a decision (Tailwind / shadcn / other) before Phase 2 UI work.

**What's left in Phase 0:**
- GitHub Actions CI workflow (lint + test on both sides from a clean clone).
- Confirm CI green before marking Phase 0 done per `docs/IMPLEMENTATION_PLAN.md`.

**Next step (Phase 1):**
- Translate `PRODUCT_SPEC.md` §8 and §15 data models into Pydantic v2 schemas
  (`Project`, `CompanyResearchPlan`, `SourceRecord`, `CompanyIntelligenceProfile`,
  `CompetitiveSignal`, `OpportunityCard`, `ReadinessScorecard`).
- Add the structured-output repair-loop utility.
- Add SQLAlchemy tables + DB session.
- Generate TypeScript types from the schemas via OpenAPI export.

---

### 2026-06-11 · Session 1 — Foundation docs

**Done:** Created `CLAUDE.md`, `docs/PRODUCT_SPEC.md` (original vision),
`docs/IMPLEMENTATION_PLAN.md` (12-phase build plan), `README.md`.

**Gaps:** No application code existed yet.

**Next step:** Phase 0 scaffold (this session).

---

## Project

AI Readiness Lab is a C-level AI readiness, competitive-intelligence, and pilot-planning
workbench. A user enters a company name and role; the app researches public company and
market signals, classifies competitors and peers, maps practical AI pilot opportunities,
scores readiness, and exports an executive-ready report (Markdown/PDF).

- **What/why (product spec):** `docs/PRODUCT_SPEC.md`
- **How/when (implementation plan):** `docs/IMPLEMENTATION_PLAN.md`
- **Audience:** CTOs, CIOs, COOs, CDOs, VPs, transformation leaders, executive AI sponsors.

## Tech stack (target)

- **Frontend:** React + Vite + TypeScript
- **Backend:** Python 3.11+, FastAPI, Pydantic v2
- **Persistence:** SQLite via SQLAlchemy (local project files)
- **Reports:** Jinja2 templates → Markdown → PDF (WeasyPrint or Playwright)
- **LLM:** Claude via the Anthropic SDK. Default to the latest capable model
  (`claude-opus-4-8`). Use structured JSON outputs validated by Pydantic schemas.
- **Research:** Web search API, source ranking, citation tracking.

## Commands

```bash
# Backend
cd backend
pip install -r requirements.txt   # install all backend deps (runtime + dev)
uvicorn app.main:app --reload      # dev server at http://localhost:8000
pytest                             # run all tests
pytest tests/test_health.py        # run a single test file
ruff check .                       # lint
ruff format .                      # format

# Frontend
cd frontend
npm install                        # install deps
npm run dev                        # dev server at http://localhost:5173
npm run build                      # production build
npm run typecheck                  # tsc --noEmit
npm run lint                       # eslint
```

## Working rules

- **IMPORTANT — Do not hallucinate.** This is a research product; fabricated facts destroy
  its credibility. Every factual or competitive claim must trace to a retrieved source with
  a confidence note. If a source does not support a claim, say so. Never invent revenue
  figures, AI outcomes, quotes, URLs, tickers, or citations. Prefer "not found in public
  sources" over a plausible guess.
- **YOU MUST write minimal code.** Implement exactly what the task needs and nothing more.
  No speculative abstractions, options, or "might need later" scaffolding. The smallest
  change that correctly solves the problem wins.
- **Do not write extra/nonsensical code.** No dead code, no unused parameters, no commented-out
  blocks, no filler comments restating the obvious. Delete code that is not used.
- **Test your work.** Add or update a focused test for any non-trivial change and run it
  before claiming done. Report real output; if something fails or is skipped, say so plainly.
- **Reuse before adding.** Search for an existing helper/pattern before writing a new one.
  Match the surrounding code's style, naming, and structure.
- **Validate at the boundary.** All LLM/research outputs cross a Pydantic schema with a
  repair loop. Never trust raw model JSON downstream.
- **Classify peers carefully.** Distinguish direct competitors, operator peers, service
  companies, technology vendors, suppliers, customers, and adjacent benchmarks. Label every
  competitive signal with its peer type. A wrong comparison is a correctness bug, not a style
  nit. See `docs/PRODUCT_SPEC.md` §3.3.
- **Keep the executive surface clean.** No model pickers, vector-DB choices, or infra
  questions in the default user UI. Technical depth lives behind drill-downs and the appendix.
- **Secrets:** never commit API keys or `.env`. Read config from environment variables.

## Repository etiquette

- Working branch: `claude/claude-md-best-practices-b31l7x`.
- Commit messages: imperative mood, no "Claude" branding — author as the repo owner.
- Do not create a pull request unless explicitly asked.
- Keep `docs/PRODUCT_SPEC.md` (vision) and `docs/IMPLEMENTATION_PLAN.md` (execution) in sync
  with real decisions as they are made.
