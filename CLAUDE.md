# CLAUDE.md — AI Readiness Lab

Guidance for Claude Code (and any AI agent) working in this repository. Keep this
file short and load-bearing. If a rule here is no longer true, fix the rule.

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

The repo is in early scaffolding. Until a component exists, treat the stack above as the
agreed target, not as already-built. Do not invent files or commands that do not exist.

## Commands

> These activate as the codebase lands. Add the real command the moment a tool is wired up;
> do not leave a guessed command here.

- Backend deps: `pip install -r backend/requirements.txt` _(once backend exists)_
- Backend dev server: `uvicorn app.main:app --reload` _(from `backend/`)_
- Backend tests: `pytest` _(prefer running the single relevant test, not the full suite)_
- Frontend deps/dev: `npm install` / `npm run dev` _(from `frontend/`)_
- Frontend build/lint/typecheck: `npm run build` / `npm run lint` / `npm run typecheck`

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
  competitive signal with its peer type. A wrong comparison (e.g. a services firm shown as a
  direct operator competitor) is a correctness bug, not a style nit. See `docs/PRODUCT_SPEC.md` §3.3.
- **Keep the executive surface clean.** No model pickers, vector-DB choices, or infra
  questions in the default user UI. Technical depth lives behind drill-downs and the report appendix.
- **Secrets:** never commit API keys or `.env`. Read config from environment variables.

## Repository etiquette

- Branch for this workstream: `claude/claude-md-best-practices-b31l7x`. Never push to another
  branch without explicit permission.
- Commit messages: imperative mood, explain the "why" when non-obvious.
- Do not create a pull request unless explicitly asked.
- Keep `docs/PRODUCT_SPEC.md` (vision) and `docs/IMPLEMENTATION_PLAN.md` (execution) in sync
  with real decisions as they are made.
