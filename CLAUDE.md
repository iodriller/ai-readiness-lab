# CLAUDE.md — AI Readiness Lab

> **IMPORTANT — Session log rule:** At the end of every AI turn, update the
> "Session Log" section below with: what was done, gaps or bugs found, what
> remains in the current phase, and what the next step is. Most-recent entry
> goes at the top. Be specific — a future agent or developer should be able to
> pick up cold from this log.

---

## Session Log (most recent first)

### 2026-06-11 · Session 4 — Phase 2: Executive Shell

**Done:**
- Backend API (`app/api/`): `POST /projects` (create + persist), `GET /projects/{id}`,
  `GET /projects/{id}/research/stream` (SSE mock job emitting the 8 spec §4.3 steps,
  then flips status → ready), `GET /projects/{id}/brief` (illustrative sample brief).
  Request/response schemas in `app/api/schemas.py`; sample content in `app/api/sample.py`
  (clearly flagged `is_sample`, asserts no company facts — respects no-hallucination rule).
- Router wired into `main.py`; API schemas added to the TS type export.
- Frontend (proper React): `react-router-dom` routing — `IntakeScreen` (company/role/mode,
  no technical knobs) → `ProjectScreen` (subscribes to SSE, shows `ResearchProgress`, then
  `Brief` with `OpportunityCardView` grid + `ReportPreview` placeholder). Typed client
  extended with `createProject`, `getBrief`, `subscribeResearch` (EventSource). `index.css`
  for a clean executive surface.
- Tests: backend 22 pass (5 new API/SSE contract tests); frontend 5 pass (intake, brief,
  progress). Typecheck + lint + build green. Verified the whole flow against a live uvicorn
  server (create → stream → ready → brief with 4 opportunities).

**Gaps / bugs found:**
- In-memory SQLite gives each connection its own DB; TestClient runs sync endpoints in a
  threadpool, so tables were missing. Fixed with `StaticPool` (shared connection) in the
  API test fixture. Use that pattern for any future TestClient+SQLite tests.
- SSE completion and merge-conflict-style transitions aren't delivered as events; the client
  detects done via a `{"type":"done"}` sentinel then closes the EventSource to avoid the
  browser's auto-reconnect. Keep that sentinel when the real research job replaces the mock.
- React Router v6 prints v7 future-flag warnings in tests (harmless). Opt into the flags or
  upgrade to v7 when convenient.
- UI mode selector exposes 3 modes (matches the `Mode` enum); the spec §4.2 mock shows a 4th
  ("Compare against competitors"). Left at 3 to avoid inventing an enum value — reconcile in spec.
- `EventSource` isn't exercised in jsdom tests (SSE is covered by the backend contract test +
  the live smoke test). An integration test for `ProjectScreen` could mock `subscribeResearch`.

**What's left in Phase 2:** Nothing blocking — acceptance met (a non-developer can click the
whole journey on mock data; no technical settings are visible by default).

**Next step (Phase 3 — Research Orchestrator):** Replace the mock SSE job with real research —
query planner (spec §7.3), source collector + ranker (§7.4), company profiler and AI-signal
extractor producing a populated `CompanyIntelligenceProfile` with per-claim `source_refs` +
confidence. Decide the web-search provider first (open question in the plan). See
`docs/IMPLEMENTATION_PLAN.md` Phase 3.

---

### 2026-06-11 · Session 3 — Phase 1: Domain Contracts (Schemas First)

**Done:**
- Pydantic v2 domain models for spec §8 + §15 under `backend/app/models/`:
  `Project`, `CompanyResearchPlan`, `SourceRecord`, `CompanyIntelligenceProfile`
  (+ sub-models), `CompetitiveSignal`, `OpportunityCard`, `ReadinessScorecard`.
  Shared enums + `Confidence`/`Score` value types in `models/base.py`.
- Structured-output **repair loop** (`app/llm/repair.py`) with injected `repair_fn`
  so it is unit-testable offline; strips ``` fences, bounded retries, raises
  `StructuredOutputError` when unrepairable.
- SQLAlchemy layer (`app/db/`): `Base`, engine/session, `ProjectRow`/`SourceRow`
  (queryable columns + JSON payload). `init_db()` wired into FastAPI lifespan.
- Env-driven `app/config.py` (pydantic-settings).
- **TypeScript types generated from the Pydantic schemas**: `app/models/export.py`
  emits `backend/schema.json`; `npm run generate:types` → `frontend/src/api/types.ts`.
- Proper React wiring: typed API client (`src/api/client.ts`), `App.tsx` calls
  `/health` with loading/online/offline states, **Vitest + Testing Library** set up
  with 3 passing component tests.
- CI updated to run `npm test`. Backend: 17 tests pass, ruff clean. Frontend:
  typecheck + lint + 3 tests + build all pass.

**Gaps / bugs found:**
- `model_copy(update=...)` bypasses Pydantic validation — a test relied on it and
  gave a false pass; fixed to construct fresh. Worth remembering for future tests.
- Vitest 2.x pinned Vite 5 while the app uses Vite 6 (duplicate Vite, type clash);
  fixed by upgrading to Vitest 3. Keep Vitest and Vite majors aligned.
- `PeerType` and `Recommendation` are intentional supersets of the narrower enums
  in spec §8.2/§15.4 (added `supplier`/`customer` and `not_recommended`) to match
  the broader §3.3/§9.4 text. Reconcile the spec enums when convenient.
- No CI check yet that `types.ts` is in sync with the schemas (would need Python in
  the frontend job). Regeneration is a documented manual step for now.
- `json2ts` emits noisy per-field aliases (`ProjectId`, `CompanyName1`, …); harmless
  but ugly. Acceptable for a generated file.

**What's left in Phase 1:** Nothing blocking — acceptance met (every model has a typed
schema + round-trip test; invalid LLM JSON is repaired or rejected; TS types generated).

**Next step (Phase 2 — Executive Shell):** Build the intake screen (company/role/mode),
`POST /projects`, the SSE research-progress screen on mock data, the static sample
brief, opportunity cards list, and report-preview placeholder — all wired through the
typed API client. See `docs/IMPLEMENTATION_PLAN.md` Phase 2.

---

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

# Generate frontend types from backend schemas (run after changing app/models)
cd backend && python -m app.models.export   # writes backend/schema.json
cd ../frontend && npm run generate:types     # writes src/api/types.ts (do not hand-edit)

# Frontend
cd frontend
npm install                        # install deps
npm run dev                        # dev server at http://localhost:5173
npm run build                      # production build
npm run typecheck                  # tsc --noEmit
npm run lint                       # eslint
npm test                           # vitest run
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
