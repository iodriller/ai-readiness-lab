<!--
ROLE OF THIS DOCUMENT
Visual reference for how AI Readiness Lab flows end-to-end — both the technical
pipeline and what the executive actually sees. Keep these diagrams in sync with
the code as the system evolves. Companion docs: docs/IMPLEMENTATION_PLAN.md (how/when),
docs/PRODUCT_SPEC.md (what/why).
-->

# AI Readiness Lab — Architecture & Flow

**Last updated:** 2026-06-11

This document maps the complete flow in two views, as requested for onboarding and
design review:

1. **Technical flow** — the request/streaming pipeline from intake to a cited brief.
2. **User journey** — what a C-level user sees and does, screen by screen.

A third **streaming sequence** diagram details the live "show your work" protocol.

---

## Key design decisions captured here

| Area | Decision | Rationale |
| --- | --- | --- |
| Frontend UI kit | **AI Elements (shadcn/ui)** — copy-paste React components we own in-repo (Conversation, Message, Reasoning, Tool, Task, Sources) | Don't reinvent the wheel; maximum extensibility since the code lives in our repo; first-class streaming + tool/step + citation primitives. Built on Radix + Tailwind, works with Vite. |
| Web search | **DuckDuckGo by default** (free, open-source, no API key). Tavily / Serper are opt-in upgrades when a key is set. | Research works out of the box with zero secrets; richer providers are a one-env-var swap. |
| Research budget | Every run is **bounded: ≤ 100 sources and ≤ 10 minutes** (`RESEARCH_MAX_SOURCES`, `RESEARCH_TIMEOUT_SECONDS`). | Deep research must terminate; on a budget hit we synthesize from evidence gathered so far rather than hanging. |
| Progress UX | **Streaming** via SSE — the UI shows live status and interim findings; it never sits silent while work runs. | Executives must see "what the agent is doing" — gathering financials, scanning competitors, etc. |
| Evidence | Ranked sources accumulate into a **JSON evidence set** (`SourceRecord`s with `source_type` + `confidence`) before any synthesis. | Every claim must trace to a cited source; synthesis reads only validated evidence. |

---

## 1. Technical flow

```mermaid
flowchart TD
    subgraph Client["Browser — React + Vite + AI Elements (shadcn/ui)"]
        Intake["Intake screen<br/>company · role · mode"]
        Console["Streaming research console<br/>live status · interim findings · source counter"]
        Brief["Executive brief<br/>opportunity cards · readiness gauge · citations"]
    end

    subgraph API["FastAPI backend"]
        Create["POST /projects<br/>create + persist"]
        Stream["GET /projects/:id/research/stream<br/>SSE"]
        BriefEP["GET /projects/:id/brief"]
    end

    subgraph Orch["Research Orchestrator (async)"]
        Plan["Query planner<br/>7 buckets + mode-specific extras"]
        Search["Parallel web search"]
        Budget{"Budget guard<br/>≤ 100 sources · ≤ 10 min"}
        Rank["Source ranker<br/>classify · dedupe · confidence"]
        Evidence[("Evidence set<br/>ranked SourceRecords as JSON")]
        Profile["Company profiler — Claude<br/>schema + repair loop"]
        Gen["Brief generator — Claude<br/>schema + repair loop"]
    end

    subgraph Ext["External services"]
        DDG["DuckDuckGo (default)<br/>Tavily / Serper if key set"]
        Claude["Claude claude-opus-4-8"]
    end

    DB[("SQLite<br/>projects · sources · profile · brief")]

    Intake -->|submit| Create --> DB
    Intake -->|navigate| Console
    Console -->|open SSE| Stream --> Plan
    Plan --> Search --> Budget
    Budget -->|within budget| DDG
    DDG --> Rank
    Budget -->|limit hit| Rank
    Rank --> Evidence --> Profile --> Claude
    Profile --> Gen --> Claude
    Gen --> DB
    Stream -. "step + interim findings (SSE)" .-> Console
    Console -->|on done| BriefEP --> DB
    BriefEP --> Brief

    Claude -. "no ANTHROPIC_API_KEY ⇒ graceful sample brief" .-> Gen
```

**Notes**

- **Graceful degradation.** No `ANTHROPIC_API_KEY` → search still runs (DuckDuckGo), but
  synthesis is skipped and a clearly-flagged `is_sample` brief is returned. No keys at all
  and DuckDuckGo unavailable → the mock path fires the same paced steps so the demo always works.
- **Validate at the boundary.** Both Claude calls pass through the Pydantic schema + repair loop;
  raw model JSON never reaches the UI or DB.

---

## 2. User journey (what the executive sees)

```mermaid
flowchart TD
    A["1 · Landing<br/>'Tell us your company and role'<br/>company name · role · what do you want to do"]
    B["2 · Start review<br/>one click — no model / infra settings"]
    C["3 · Live research console<br/>animated steps: 'Gathering financials…'<br/>source counter · interim findings stream in"]
    D{"Research complete<br/>bounded ≤ 10 min"}
    E["4 · Executive brief<br/>VISUALS: opportunity cards with value / feasibility / risk badges<br/>readiness gauge · competitive-pressure view · cited sources"]
    F["5 · Drill down<br/>open a card → why now · first step · evidence + confidence"]
    G["6 · Ask a follow-up<br/>chat: 'What about our supply chain?'<br/>streamed, source-grounded answer"]
    H["7 · Export<br/>source-cited PDF / Markdown report"]

    A --> B --> C --> D
    D -->|streamed done| E
    E --> F
    E --> G
    G -->|refine / new angle| C
    F --> H
    E --> H
```

**Principles**

- The user gives **two facts** (company, role) plus an intent, and never touches a technical knob.
- The console is **never silent** — status and interim findings stream the whole time.
- The payoff is **visual, not a wall of text** — cards, badges, a readiness gauge, and citations.
- Every screen offers a **next move**: drill into evidence, ask a follow-up, or export.

---

## 3. Streaming "show your work" sequence

```mermaid
sequenceDiagram
    actor U as C-level user
    participant UI as React UI (AI Elements)
    participant API as FastAPI /research/stream
    participant ORCH as Orchestrator
    participant DDG as DuckDuckGo
    participant LLM as Claude

    U->>UI: company · role · mode
    UI->>API: open SSE
    API->>ORCH: run(project, company, mode)
    ORCH-->>UI: step "Identifying company profile"
    ORCH->>DDG: parallel queries (budget ≤100 src / ≤10 min)
    DDG-->>ORCH: results
    ORCH-->>UI: interim "Gathering financial & strategic signals"
    Note over ORCH: rank · dedupe · confidence → evidence JSON
    ORCH->>LLM: profile from ranked evidence (schema + repair)
    LLM-->>ORCH: CompanyIntelligenceProfile JSON
    ORCH-->>UI: step "Building AI opportunity map"
    ORCH->>LLM: generate executive brief
    LLM-->>ORCH: BriefResponse JSON
    ORCH->>API: persist brief
    ORCH-->>UI: done
    UI->>API: GET /brief
    API-->>UI: brief + cited sources
    UI-->>U: visuals — cards · gauge · citations
```

**SSE event contract** (current + planned)

| Event | Payload | Status |
| --- | --- | --- |
| `step` | `{ index, total, label }` — coarse progress | implemented |
| `interim` | `{ label, detail }` — "gathering X", partial finding | planned (Phase 4 console) |
| `source` | `{ url, source_type, confidence }` — live source counter | planned (Phase 4 console) |
| `done` | `{}` — sentinel; client closes SSE, fetches brief | implemented |
| `error` | `{ message }` — terminal failure | implemented (client-side) |
