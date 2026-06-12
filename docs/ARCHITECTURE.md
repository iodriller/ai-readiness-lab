<!--
ROLE OF THIS DOCUMENT
Visual reference for how AI Readiness Lab flows end-to-end — both the technical
pipeline and what the executive actually sees. Keep these diagrams in sync with
the code as the system evolves. Companion docs: docs/IMPLEMENTATION_PLAN.md (how/when),
docs/PRODUCT_SPEC.md (what/why).
-->

# AI Readiness Lab — Architecture & Flow

**Last updated:** 2026-06-12

This document maps the complete, shipped system in four views:

1. **Technical pipeline** — intake → research → brief → pilot → export.
2. **User journey** — what a C-level user sees, screen by screen.
3. **Streaming "show your work"** — the SSE event contract in detail.
4. **Desktop app packaging** — how the app is bundled and delivered.

---

## Key design decisions

| Area | Decision | Rationale |
| --- | --- | --- |
| Frontend UI kit | **AI Elements (shadcn/ui)** — copy-paste React components owned in-repo | Maximum extensibility; native streaming/step/citation primitives; built on Radix + Tailwind. |
| Web search | **DuckDuckGo by default** (no API key). Tavily / Serper opt-in via env key. | Works out of the box; richer providers are a one-env-var swap. |
| Research budget | **≤ 100 sources · ≤ 10 minutes** (`RESEARCH_MAX_SOURCES`, `RESEARCH_TIMEOUT_SECONDS`) | Deep research must terminate; synthesizes from evidence gathered so far on budget hit. |
| Progress UX | **Streaming via SSE** — live step labels, interim findings, and source counter | Executives must see "what the agent is doing" — never a silent spinner. |
| Peer classification | **Rule-based curated dict → reason string** | Explicit, auditable; unknown companies defer to `adjacent_benchmark` rather than guessing. |
| Pilot scoring | **Deterministic rubric** — identical inputs always yield identical scores | Verifiable; no LLM needed; works offline; fast. |
| API key | **OS keychain** (`keyring`) with 0600-file fallback; only `…last4` hint returned to UI | Compliant with Anthropic's policy (BYOK, no OAuth); secure by default. |
| Desktop packaging | **PyInstaller + pywebview** — single `.app`/`.exe`, no Python install required | One double-click for a non-technical executive. |
| Reports | **fpdf2 + Liberation Sans TTF** — cover page, section numbering, native Unicode | Board-ready PDF; em-dashes, curly quotes, and arrows render natively. |
| LLM | **Claude `claude-opus-4-8`** for company profiling and brief generation | Best reasoning available; structured JSON output validated by Pydantic + repair loop. |

---

## 1. Complete technical pipeline

```mermaid
flowchart TD
    subgraph Input
        Intake["Intake screen\ncompany · role · mode"]
    end

    subgraph Backend["FastAPI backend (Python 3.11)"]
        direction TB
        Create["POST /projects\ncreate row + SQLite"]
        Stream["GET /:id/research/stream\nSSE orchestrator"]
        BriefEP["GET /:id/brief"]
        QA["POST /:id/qa\nQ&A endpoint"]
        PilotQ["GET /:id/pilot/questions"]
        PilotPost["POST /:id/pilot\npersist PilotPlan"]
        ReportMD["GET /:id/report.md"]
        ReportPDF["GET /:id/report.pdf"]
    end

    subgraph Orch["Research Orchestrator"]
        Plan["Query planner\n7 buckets + mode extras"]
        Search["Parallel DuckDuckGo\n(Tavily/Serper if keyed)"]
        Budget{"Budget guard\n≤100 src · ≤10 min"}
        Rank["Source ranker\nclassify · dedupe · confidence"]
        Evidence[("Evidence JSON\nSourceRecord list")]
        Profiler["Company profiler\nClaude + repair loop"]
        PeerClass["Peer classifier\ncurated dict → reason"]
        OppScore["Opportunity scorer\ncurated library · no-hallucination guard"]
        BriefGen["Brief generator\nClaude + repair loop"]
    end

    subgraph QAPkg["Q&A package"]
        QAClass["Question classifier\n5 rule-based types"]
        QARetriever["Context retriever\nprofile + signals + history"]
        QACompose["Answer composer\nClaude · 9-field StructuredAnswer"]
    end

    subgraph PilotPkg["Pilot package"]
        PilotQPkg["7 executive questions\n+ platform-aware checklist"]
        Scorer["Deterministic scorer\n8 dimensions · rubric-based"]
    end

    subgraph Report["Report generator"]
        MD["render_markdown()\nfull Unicode"]
        PDF["render_pdf()\ncover page · §sections\nLiberation Sans TTF"]
    end

    DB[("SQLite\nprojects · profile · brief\npilot · qa_history")]

    Intake -->|POST| Create --> DB
    Intake -->|open SSE| Stream --> Plan
    Plan --> Search --> Budget
    Budget -->|within budget| Search
    Budget -->|limit| Rank
    Search --> Rank --> Evidence
    Evidence --> Profiler --> PeerClass --> OppScore --> BriefGen
    BriefGen --> DB
    Stream -. "step + interim + source events (SSE)" .-> Intake
    BriefEP --> DB --> BriefEP
    QA --> QAClass --> QARetriever --> QACompose
    QARetriever --> DB
    QACompose --> DB
    PilotQ --> PilotQPkg
    PilotPost --> Scorer --> DB
    ReportMD --> MD
    ReportPDF --> PDF
    MD --> DB
    PDF --> DB
```

---

## 2. User journey

```mermaid
flowchart TD
    A["1 · Landing\nCompany name · role · intent\nSettings panel: live/sample badge\nRecent reviews list"]
    B["2 · Live research console\nAnimated steps\nInterim findings stream in\nSource counter grows live"]
    C{"Research complete\nbounded ≤ 10 min"}
    D["3 · Executive brief\nReadiness banner with gauge\n2-col opportunity cards\n(value / feasibility / risk badges)\nEvidence panel with citations"]
    E["4 · Pilot drill-down\n7 plain-English executive questions\nDeterministic readiness scorecard\nDimension bars · recommendation badge\nStrengths / blockers / next actions\nTechnical leader checklist"]
    F["5 · Strategy Q&A\nFree-form question on the brief\n9-field structured answer:\nwhy it matters · peer signals\npilot options · data needed\nrisks to control · technical questions"]
    G["6 · Export\nDownload PDF (cover page · §sections)\nDownload Markdown\nFull pilot scorecard + Q&A included"]
    H["7 · Return home\nBrief saved; recent reviews list\nResume any prior project from history"]

    A -->|Start review| B --> C -->|done event| D
    D -->|Plan this pilot| E
    D -->|Ask a question| F
    F -->|follow-up| F
    E --> G
    D --> G
    G --> H
    H -->|click prior review| D
```

**Principles**

- **Two facts to start:** company name + role. No model pickers, no infra config.
- **Never silent:** status + interim findings stream the whole time research runs.
- **Visual, not a wall of text:** cards, coloured badges, a circular readiness gauge, and a cited evidence panel.
- **Every screen has a next move:** drill into evidence, plan a pilot, ask a follow-up, or export.
- **Persistent:** every brief survives a window close; the landing screen links to all prior projects.

---

## 3. Streaming "show your work" sequence

```mermaid
sequenceDiagram
    actor U as C-level user
    participant UI as React UI (AI Elements)
    participant API as FastAPI /research/stream
    participant ORCH as Orchestrator
    participant DDG as DuckDuckGo
    participant LLM as Claude (claude-opus-4-8)

    U->>UI: company · role · mode
    UI->>API: POST /projects → project_id
    UI->>API: open SSE /projects/:id/research/stream
    API->>ORCH: run(project, company, mode)
    ORCH-->>UI: step "Identifying company profile" (1/8)
    ORCH->>DDG: parallel queries — 7 buckets
    DDG-->>ORCH: ranked results (budget guard active)
    ORCH-->>UI: source events (url · title · source_type · confidence)
    ORCH-->>UI: interim "Gathering financial & strategic signals"
    Note over ORCH: rank · dedupe · confidence → evidence JSON
    ORCH-->>UI: step "Classifying competitive landscape" (4/8)
    Note over ORCH: peer_classifier → PeerTaxonomy
    Note over ORCH: competitive_signals → filter_relevant()
    ORCH-->>UI: step "Mapping AI opportunities" (5/8)
    Note over ORCH: score_opportunities() → OpportunityCard list
    ORCH->>LLM: company profiler (schema + repair loop)
    LLM-->>ORCH: CompanyIntelligenceProfile JSON
    ORCH->>LLM: brief generator (schema + repair loop)
    LLM-->>ORCH: BriefResponse JSON
    ORCH->>API: persist brief + sources + profile
    ORCH-->>UI: done {}
    UI->>API: GET /projects/:id/brief
    API-->>UI: brief + cited sources
    UI-->>U: Brief screen — cards · gauge · evidence
```

**SSE event contract**

| Event | Payload | Status |
| --- | --- | --- |
| `step` | `{ index, total, label }` | implemented |
| `interim` | `{ label, detail }` | implemented |
| `source` | `{ url, title, source_type, confidence }` | implemented |
| `done` | `{}` — client closes SSE, fetches brief | implemented |
| `error` | `{ message }` | implemented (client-side) |

---

## 4. Desktop app packaging

```mermaid
flowchart LR
    subgraph Build["Build (GitHub Actions / local)"]
        FE["npm run build\nfrontend/dist/"]
        BE["pip install -r requirements.txt"]
        PyI["pyinstaller\ndesktop/AIReadinessLab.spec"]
        FE --> PyI
        BE --> PyI
    end

    subgraph Bundle["PyInstaller bundle (_internal/)"]
        RT["Python runtime"]
        APP["app/ package\n(backend)"]
        JSON["app/opportunity/data/library.json\n(collect_data_files)"]
        FONTS["app/fonts/*.ttf\n(collect_data_files)"]
        DIST["frontend_dist/\n(built SPA)"]
        Launcher["launcher.py entry point"]
    end

    subgraph Runtime["At launch"]
        Splash["Splash HTML in pywebview\n(while server starts)"]
        Health["wait_until_healthy()\npoll /health"]
        Window["Native window\n→ navigate to localhost:PORT"]
    end

    PyI --> Bundle
    Launcher -->|"start daemon thread"| Uvicorn["uvicorn\nloop=asyncio · http=h11"]
    Uvicorn --> FastAPI["FastAPI\nserves SPA + API"]
    Launcher --> Splash --> Health --> Window
    FastAPI -->|"static mount"| DIST
```

**Notes**

- `launcher.py` (not `app.py`) avoids shadowing the backend `app` package under PyInstaller.
- `ensure_writable_db()` moves SQLite to the user config dir when the app is frozen (macOS `.app` bundle is read-only).
- `_setup_logging()` writes `launch.log` to config dir; redirects `sys.stdout/stderr` (both are `None` in `console=False` builds).
- The browser fallback (`webbrowser.open`) ensures the app works even without pywebview.
- Release workflow: `.github/workflows/release.yml` matrix-builds Windows `.zip`, macOS `.dmg`, Linux `.tar.gz` on a `v*` tag.
