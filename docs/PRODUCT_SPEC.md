<!--
ROLE OF THIS DOCUMENT
This is the canonical PRODUCT SPEC (the "what" and "why"): vision, positioning,
product modes, research design, data models, and report structure.
For the "how" and "when" — phases, implementation steps, acceptance criteria,
sequencing, and risks — see docs/IMPLEMENTATION_PLAN.md.
Keep the two in sync as decisions are made.
-->

# AI Readiness Lab — Product Spec (Vision & Product Design)

**Recommended repo name:** `ai-readiness-lab`  
**Product name:** **AI Readiness Lab**  
**Project type:** C-level AI readiness, competitive intelligence, and pilot planning workbench  
**Primary audience:** CTOs, CIOs, COOs, CDOs, VPs, transformation leaders, and executive AI sponsors  
**Core output:** Executive-ready AI readiness and pilot recommendation report  
**Core promise:** Tell us your company. We research your market, show where AI pressure is building, identify practical AI pilots, score readiness, and turn one selected idea into a scoped, risk-aware, technically grounded plan.

---

## 1. Executive Summary

AI Readiness Lab is a C-level-friendly application that helps enterprise leaders answer a blunt question:

> Are we actually ready for AI, and what should we pilot next?

The product is not a generic chatbot, not a developer tool, and not a static maturity quiz.

It is an executive-facing workbench that starts with public company and market research, creates a concise competitive AI landscape, identifies practical AI opportunities, guides the user through a short structured conversation, scores pilot readiness, and generates a polished PDF report.

The intended user experience is almost zero-step:

```text
Open app
  -> enter company name and role
  -> app researches public company and market signals
  -> app creates a concise AI readiness and competitive pressure brief
  -> user selects or asks about an opportunity
  -> app guides a short structured conversation
  -> app creates readiness score, pilot plan, risk controls, data needs, and technical leadership questions
  -> app exports a polished PDF report
```

The differentiator is **structure**.

Executives can already ask a general-purpose chatbot broad questions. AI Readiness Lab must be better because it provides:

- structured company research,
- source-backed competitive signals,
- careful peer classification,
- industry-specific opportunity mapping,
- readiness scoring,
- risk and evaluation planning,
- technical-leader follow-up questions,
- and polished reports.

---

## 2. Product Positioning

### 2.1 One-Sentence Description

**AI Readiness Lab is a C-level AI readiness workbench that researches company and competitor AI signals, identifies practical enterprise AI pilots, scores readiness, and generates executive-ready reports.**

### 2.2 GitHub Description

```text
C-level AI readiness workbench that researches company and competitor AI signals, identifies practical enterprise AI pilots, scores readiness, and generates executive-ready reports.
```

### 2.3 Tagline Options

Recommended:

```text
Know where your company stands on AI, where competitors are moving, and what pilot is worth launching next.
```

Shorter:

```text
Find the AI pilots your company should actually run.
```

Readiness-focused:

```text
See if your company is AI-ready — and what to do next.
```

### 2.4 Product Personality

AI Readiness Lab should feel like:

```text
AI strategy associate
  + competitive intelligence analyst
  + enterprise solution architect
  + readiness evaluator
  + risk and evaluation planner
  + executive report writer
```

It should not feel like:

```text
generic chatbot
developer console
survey form
static checklist
governance spreadsheet
consulting buzzword machine
```

---

## 3. Core Product Philosophy

## 3.1 Start Executive, Then Drill Down

The product starts with high-level executive concerns:

```text
Where are we?
Where is the market moving?
Where are competitors investing?
Where is AI pressure building?
What opportunities are realistic?
What should we pilot first?
```

Only after the user selects an opportunity should the app go deeper:

```text
Who are the users?
What workflow?
What data?
What systems?
What tools?
What risks?
What evaluation?
What should technical leaders answer?
```

The app should move from executive strategy to technical planning, but only when useful.

## 3.2 Create Useful FOMO, Not Fake Hype

The app should create constructive urgency.

It should say things like:

```text
Public signals suggest your industry is moving AI into operational workflows, technical decision support, maintenance intelligence, digital twins, automation, and enterprise knowledge work.

There may be practical opportunities to launch targeted pilots before competitors build more mature capabilities.
```

But it must not make unsupported claims.

Bad:

```text
Competitor X increased net revenue by 10% from AI.
```

Unless a credible source says exactly that.

Good:

```text
Public reporting and company disclosures suggest peers are investing in AI-enabled drilling, digital operations, maintenance intelligence, digital twins, and decision support. The exact financial contribution is often not isolated publicly, but the strategic direction is visible.
```

## 3.3 Avoid Bad Competitive Analysis

Peer classification is critical.

A bad comparison destroys credibility.

Example in oil and gas:

- Occidental Petroleum is primarily an **operator / energy producer**.
- SLB is primarily an **oilfield services and technology company**.
- Chevron, ExxonMobil, ConocoPhillips, EOG, Devon, Shell, BP, and TotalEnergies may be more appropriate operator peers depending on context.
- SLB, Halliburton, Baker Hughes, NOV, and Weatherford are service/technology benchmarks, suppliers, or ecosystem signals — not direct operator competitors.

The app must distinguish:

```text
direct competitors
same-industry peers
operator peers
service companies
technology vendors
suppliers
customers
partners
adjacent benchmarks
```

A service-company AI initiative may still matter, but the app must label it correctly.

Example:

```text
SLB is not a direct operator competitor to Oxy. It is an oilfield services and technology benchmark. Its AI activity is relevant because it signals where the oilfield technology ecosystem is moving.
```

This structure is one of the reasons the tool is more useful than a normal chatbot.

---

## 4. Primary UX

## 4.1 Zero-Step Launch Expectation

The executive-facing version should not require terminal usage.

Acceptable launch paths:

### Hosted App

```text
https://ai-readiness-lab.app
```

### Desktop App

```text
AI Readiness Lab.exe
AI Readiness Lab.dmg
```

Double-click opens the app.

### Internal Enterprise Deployment

```text
Company IT deploys internally.
Executive opens a URL.
```

The GitHub repo can contain developer instructions, but that is not the primary user journey.

---

## 4.2 First Screen

The first screen should be simple.

```text
AI Readiness Lab

See where your company stands on AI, where competitors are moving, and which pilot is worth launching next.

Company name
[________________________________]

Your role
[ CTO / CIO / CEO / COO / VP / Director / Transformation Lead / Consultant ]

What do you want to do?
[ Find AI opportunities ]
[ Evaluate a specific AI idea ]
[ Compare against competitors ]
[ Prepare an executive AI brief ]

[Start Review]
```

No technical settings.  
No model picker.  
No vector database choices.  
No infrastructure questions.

---

## 4.3 Research Progress Screen

After the user enters the company, the app shows a polished progress screen:

```text
Building AI readiness context...

✓ Identifying company profile
✓ Classifying company type and business segments
✓ Finding public financial and strategic signals
✓ Identifying direct competitors and adjacent peers
✓ Searching competitor AI and digital initiatives
✓ Searching industry AI patterns
✓ Building AI opportunity map
✓ Preparing executive brief
```

Behind the scenes, the app does exhaustive structured research.

The executive sees only calm progress and a concise result.

---

## 4.4 First Result Screen

Example for an energy company:

```text
AI Readiness Brief: Occidental Petroleum

What matters:
Oxy appears to operate across oil and gas, chemicals, and carbon management. The most relevant AI opportunity surfaces are likely operations, field engineering, maintenance, production workflows, carbon management, supply chain, and enterprise knowledge access.

Competitive pressure:
Direct operator peers and adjacent energy technology providers are publicly signaling AI investment in areas such as drilling efficiency, digital twins, equipment optimization, maintenance intelligence, and engineering decision support.

The opening:
Oxy does not need to start with a broad enterprise chatbot. The stronger starting point is a targeted, high-value workflow where data already exists, users feel pain, and human approval can remain in control.

Recommended next move:
Select one practical pilot and scope it with data requirements, tool boundaries, risk controls, and evaluation criteria.
```

Buttons:

```text
[Explore Recommended Opportunities]
[Evaluate My Own Idea]
[Ask a Strategy Question]
[Generate Landscape Brief]
```

---

## 5. Product Modes

## 5.1 Mode 1 — Discover Opportunities

For executives who do not know where to start.

Flow:

```text
Company name
  -> company research
  -> peer classification
  -> competitive AI signals
  -> industry opportunity map
  -> ranked AI pilot opportunities
  -> selected opportunity
  -> readiness report
```

Output:

```text
Here are the top AI opportunities for your company, ranked by likely value, feasibility, risk, and readiness.
```

## 5.2 Mode 2 — Evaluate My AI Idea

For users who already have an idea.

Example:

```text
We already have a drilling chatbot. What should we do next?
```

The app researches the company and industry, then pressure-tests the idea across:

```text
business value
workflow clarity
data readiness
user adoption
risk
evaluation path
integration complexity
competitive differentiation
technical feasibility
```

## 5.3 Mode 3 — Ask Strategy Questions

For open-ended executive questions.

Examples:

```text
What can AI do for drilling engineers?
What is the lowest-risk AI pilot for operations?
Where can AI help maintenance without creating safety risk?
How are competitors using AI?
What should we pilot in 90 days?
What should I ask my technical leaders?
What should we do if we already have several chatbots?
Where could agents help without touching control systems?
```

The app answers using:

```text
company profile
peer research
industry AI patterns
technical opportunity library
structured readiness framework
previous user answers
```

---

## 6. Enterprise AI Opportunity Library

The app should include a structured opportunity library.

## 6.1 Knowledge and Decision Support

```text
Enterprise search / RAG assistant
Technical document assistant
Field engineer troubleshooting assistant
Maintenance procedure assistant
Engineering standards assistant
Policy and compliance assistant
Research and competitive intelligence assistant
```

## 6.2 Agentic / Tool-Using Assistants

```text
Agent with tools
Work-order drafting assistant
Alarm investigation assistant
Inspection report assistant
Supplier inquiry assistant
Project controls assistant
Engineering workflow agent
Ticket triage agent
```

## 6.3 Workflow Automation

```text
Invoice exception handling
Procurement request routing
Maintenance planning workflow
Document review workflow
Regulatory submission workflow
Approval-routing assistant
Service ticket routing
```

## 6.4 Analytics and Decision Intelligence

```text
Analytics copilot
Dashboard copilot
Operations performance assistant
Production variance explanation
Cost anomaly assistant
Forecast explanation assistant
Executive KPI copilot
```

## 6.5 Document and Reporting

```text
Document summarizer
Executive report generator
Regulatory filing support
HSE incident summarizer
Meeting-to-action assistant
Contract summary assistant
Board deck assistant
```

## 6.6 Industrial / Technical AI

```text
Predictive maintenance assistant
Failure mode analysis assistant
Equipment reliability copilot
Process optimization advisor
Digital twin assistant
Subsurface knowledge assistant
Drilling engineering copilot
Well planning assistant
Production optimization advisor
```

## 6.7 Corporate Functions

```text
HR policy assistant
Finance close assistant
Legal contract assistant
IT service desk copilot
Cybersecurity incident assistant
Training and onboarding assistant
```

---

## 7. Deep Research System

The research system is the heart of the product.

It must be structured, multi-step, source-aware, and confidence-scored.

## 7.1 Research Goals

For each company, identify:

```text
company identity
company type
business segments
industry and subindustry
financial snapshot
strategic priorities
recent earnings themes
public AI/digital initiatives
direct competitors
adjacent peers
service/technology benchmarks
competitor AI signals
industry AI patterns
technical opportunity areas
```

## 7.2 Research Categories

The app should search across:

```text
official company website
investor relations
annual report / 10-K
recent earnings call summaries
recent press releases
recent AI/digital transformation news
competitor AI initiatives
industry AI use cases
analyst summaries
vendor partnership announcements
job postings for AI/data/digital roles
technical papers
industry articles
```

## 7.3 Search Query Templates

Company-level queries:

```text
{company} official business segments
{company} annual report AI digital transformation
{company} investor presentation digital AI automation
{company} earnings call AI automation digital
{company} press release AI digital transformation
{company} generative AI
{company} data science machine learning
{company} automation operations AI
```

Competitor/peer queries:

```text
{peer} AI drilling
{peer} generative AI operations
{peer} digital twin AI
{peer} predictive maintenance AI
{peer} automation machine learning operations
{peer} AI copilot engineering
```

Industry queries:

```text
oil and gas AI drilling optimization
oil and gas generative AI field operations
oil and gas AI predictive maintenance
energy AI digital twin operations
chemical industry generative AI operations
industrial AI agent maintenance workflows
```

## 7.4 Source Quality Hierarchy

High confidence:

```text
official annual reports
official investor presentations
official press releases
SEC filings
earnings call transcripts
credible news sources
recognized analyst or industry reports
academic or technical papers
```

Medium confidence:

```text
vendor case studies
conference presentations
job postings
industry blogs
company blogs
```

Low confidence:

```text
unsourced blogs
marketing aggregators
social media posts
SEO content
```

Reports should include source and confidence notes in an appendix.

---

## 8. Structured Research Outputs

## 8.1 Company Intelligence Profile

```json
{
  "company_identity": {
    "name": "",
    "ticker": "",
    "website": "",
    "headquarters": "",
    "company_type": "",
    "industry": "",
    "subindustries": [],
    "business_segments": [],
    "operating_regions": [],
    "confidence": 0.0
  },
  "financial_snapshot": {
    "revenue_latest": null,
    "net_income_latest": null,
    "market_cap": null,
    "capex_latest": null,
    "financial_trend_summary": "",
    "source_refs": []
  },
  "strategic_priorities": {
    "themes": [],
    "earnings_call_signals": [],
    "investor_presentation_signals": [],
    "source_refs": []
  },
  "ai_and_digital_signals": {
    "company_ai_initiatives": [],
    "digital_transformation_signals": [],
    "automation_signals": [],
    "data_platform_signals": [],
    "job_posting_signals": [],
    "partnership_signals": [],
    "source_refs": []
  },
  "peer_taxonomy": {
    "direct_competitors": [],
    "operator_peers": [],
    "service_company_benchmarks": [],
    "technology_vendor_benchmarks": [],
    "adjacent_industry_benchmarks": []
  },
  "competitive_ai_signals": [],
  "industry_ai_patterns": [],
  "opportunity_hypotheses": [],
  "confidence": {
    "overall": 0.0,
    "company_identity": 0.0,
    "financials": 0.0,
    "peer_taxonomy": 0.0,
    "ai_signals": 0.0,
    "opportunity_hypotheses": 0.0
  },
  "sources": []
}
```

## 8.2 Competitive Signal

```json
{
  "company": "",
  "peer_type": "direct_competitor|operator_peer|service_company|technology_vendor|adjacent_benchmark",
  "signal": "",
  "ai_area": "",
  "business_relevance": "",
  "fomo_strength": "low|medium|high",
  "source_ids": [],
  "confidence": 0.0
}
```

## 8.3 Opportunity Card

```json
{
  "name": "",
  "category": "",
  "executive_summary": "",
  "why_now": "",
  "competitive_pressure": "",
  "business_value": "low|medium|high",
  "pilot_feasibility": "low|medium|high",
  "risk_level": "low|medium|high",
  "time_to_pilot": "30_days|60_days|90_days|longer",
  "recommended_first_step": "",
  "technical_depth_required": "low|medium|high"
}
```

---

## 9. AI Readiness Scoring

## 9.1 Company-Level Readiness Dimensions

```text
AI signal maturity
data foundation signals
digital transformation signals
operational complexity
competitive pressure
leadership urgency
opportunity surface size
public evidence strength
```

## 9.2 Pilot-Level Readiness Dimensions

```text
business value
workflow clarity
data availability
data quality
user adoption potential
agent/tool scope clarity
risk/control readiness
evaluation readiness
integration feasibility
operational ownership
time-to-pilot
```

## 9.3 Example Score

```text
Overall Pilot Readiness: 71 / 100

Recommendation:
Proceed with limited internal pilot.

Why:
The use case has clear business value and can start with read-only access. Main gaps are data freshness, evaluation set preparation, and human approval controls.
```

## 9.4 Readiness Recommendation Types

```text
Proceed
Proceed with limited pilot
Needs discovery
Defer until prerequisites are addressed
Not recommended
```

---

## 10. Open-Ended Strategy Answering

The app must support open-ended executive questions.

It should not answer like a generic model. It should use a structured answer format.

For a question like:

```text
What can we do for drilling engineers?
```

The answer should include:

```text
1. Direct answer
2. Why this matters for the company
3. Peer/industry signals
4. Practical pilot options
5. Recommended first pilot
6. What data is needed
7. What risks to control
8. What to ask technical leaders
9. Report/export option
```

Example:

```text
For drilling engineers, I would not start with a generic chatbot. I would start with a read-only drilling decision-support copilot grounded in internal knowledge and historical wells.

Best pilot options:
1. Offset Well Intelligence Assistant
2. Drilling Procedure and Lessons-Learned Assistant
3. NPT / Trouble Event Summarizer
4. Mud Program and BHA Knowledge Assistant
5. Real-Time Drilling Advisory Copilot, later-stage only

Recommended first pilot:
Offset Well Intelligence Assistant.

Why:
High-value workflow, lower safety risk, mostly read-only, clear evaluation path, useful before real-time integration.

Ask technical leaders:
- Where are end-of-well reports stored?
- Are daily drilling reports searchable?
- Do we have NPT classification history?
- Can we access offset-well metadata?
- Which systems hold mud, BHA, and drilling parameter records?
- What cloud/data platform is approved for this pilot?
```

---

## 11. Guided Drill-Down After Opportunity Selection

After the executive picks an opportunity, the app asks short, plain-English questions.

## 11.1 Executive Questions

```text
Who would use this?
What decision or workflow should improve?
What should the AI never do?
What data sources likely exist?
What outcome would make this worth it?
What risk would make this unacceptable?
Who would approve the pilot?
```

## 11.2 Technical Leader Questions

The app generates a technical discovery checklist.

```text
Data and systems:
- Where are the relevant documents stored?
- Are they in SharePoint, Box, S3, data lake, network drive, or document management system?
- Are database exports available?
- Are APIs available?
- Are access controls already defined?
- Is the data on AWS, Azure, GCP, Snowflake, Databricks, or on-prem?
- Are there existing vector search, RAG, or AI platform capabilities?

Architecture:
- Should the pilot run in AWS, Azure, GCP, or internal infrastructure?
- Is there an approved LLM provider?
- Is local model deployment required?
- Is data allowed to leave the enterprise environment?
- What observability/evaluation tooling is approved?
- Is there an existing API gateway or tool-integration layer?

Risk and operations:
- Who owns the assistant?
- Who approves high-risk outputs?
- What is the escalation path?
- What logs must be retained?
- What evaluation threshold is required before rollout?
```

This bridges C-level intent and technical execution.

---

## 12. Report Generation

The final PDF is the main artifact.

## 12.1 Report Types

```text
Executive AI Readiness Brief
Competitive AI Landscape Brief
AI Pilot Recommendation Report
Technical Discovery Appendix
Board/Leadership Summary
```

## 12.2 PDF Structure

```text
1. Executive Summary
2. Company Context
3. Competitive and Peer AI Signals
4. AI Opportunity Map
5. Selected Pilot Recommendation
6. Readiness Scorecard
7. Data Requirements
8. Tool and Agent Boundaries
9. Risk Register
10. Evaluation Plan
11. 30/60/90-Day Roadmap
12. Technical Leader Questions
13. Sources and Confidence Notes
```

## 12.3 Executive Summary Tone

The summary should be concise, optimistic, and credible.

Example:

```text
Public signals suggest the energy sector is moving quickly from generic AI experimentation toward operational AI: drilling support, equipment performance, digital twins, field decision support, and engineering knowledge assistants.

For this company, the strongest near-term opportunity is not a broad enterprise chatbot. It is a targeted pilot in a high-value workflow where data already exists, users feel pain, and human oversight can remain in place.

Recommended first pilot:
Field Engineer Troubleshooting Assistant

Why this pilot:
- High-frequency operational need
- Clear value path
- Existing manuals, SOPs, work orders, and alarm context can support it
- Risk can be controlled with read-only access and human approval
- Evaluation can be built from historical cases
```

---

## 13. Application Architecture

## 13.1 High-Level Modules

```text
Executive UI
  -> company intake
  -> opportunity cards
  -> guided Q&A
  -> report preview

Research Orchestrator
  -> web search planner
  -> source collector
  -> source ranker
  -> company profiler
  -> peer classifier
  -> AI signal extractor

Opportunity Engine
  -> industry use-case library
  -> company fit scorer
  -> competitive pressure scorer
  -> opportunity ranker

Readiness Engine
  -> question planner
  -> structured intake
  -> scoring model
  -> blocker detector
  -> recommendation generator

Technical Bridge
  -> data requirement generator
  -> architecture question generator
  -> tool boundary generator
  -> evaluation plan generator

Report Generator
  -> markdown
  -> PDF
  -> JSON project package
```

---

## 14. Suggested Stack

## 14.1 Executive App

```text
React
Vite
TypeScript
FastAPI backend
SQLite or local project files
PDF export
```

## 14.2 Desktop Packaging

```text
Tauri
or Electron
or PyInstaller + local FastAPI + browser launch
```

Recommended path:

```text
Hosted web app first for demo.
Tauri desktop later for one-click local app.
```

## 14.3 Backend

```text
Python 3.11+
FastAPI
Pydantic v2
SQLAlchemy / SQLite
Jinja2 for report templates
WeasyPrint or Playwright/Puppeteer for PDF export
```

## 14.4 Research

```text
Web search API
company website scraping
SEC / annual report retrieval where possible
news search
source ranking
structured extraction
citation tracking
```

## 14.5 LLM

```text
OpenAI-compatible client
LocalDeploy-compatible option for private/internal mode
structured JSON outputs
schema validation
repair loop
```

---

## 15. Core Data Models

## 15.1 Project

```json
{
  "project_id": "",
  "company_name": "",
  "user_role": "",
  "mode": "discover_opportunities|evaluate_idea|strategy_question",
  "created_at": "",
  "status": "researching|ready|report_generated"
}
```

## 15.2 CompanyResearchPlan

```json
{
  "company_name": "",
  "known_ticker": "",
  "research_tasks": [
    "resolve_company_identity",
    "identify_company_type",
    "find_business_segments",
    "find_financial_snapshot",
    "find_ai_initiatives",
    "identify_direct_competitors",
    "classify_peer_groups",
    "find_competitor_ai_signals",
    "find_industry_ai_patterns"
  ],
  "search_queries": [],
  "source_requirements": {
    "min_official_sources": 2,
    "min_competitor_sources": 3,
    "min_industry_sources": 3
  }
}
```

## 15.3 SourceRecord

```json
{
  "source_id": "",
  "url": "",
  "title": "",
  "publisher": "",
  "published_date": "",
  "source_type": "official|filing|news|analyst|vendor|blog|academic|job_posting",
  "confidence": 0.0,
  "claims_extracted": []
}
```

## 15.4 ReadinessScorecard

```json
{
  "overall_score": 0,
  "recommendation": "proceed|limited_pilot|defer|needs_discovery",
  "dimensions": {
    "business_value": 0,
    "workflow_clarity": 0,
    "data_readiness": 0,
    "risk_controls": 0,
    "evaluation_readiness": 0,
    "integration_feasibility": 0,
    "operational_ownership": 0,
    "user_adoption": 0
  },
  "blockers": [],
  "strengths": [],
  "next_actions": []
}
```

---

## 16. Implementation Phases

## Phase 0 — Product Identity and UX Prototype

Goal: create the executive-level product shell.

Tasks:

- finalize name as AI Readiness Lab,
- design landing screen,
- design company intake screen,
- design research progress screen,
- design opportunity cards,
- design report preview.

Acceptance:

- clickable UI mockup exists,
- no technical settings are visible by default,
- user understands the product in 30 seconds.

## Phase 1 — Executive Shell

Goal: build the first runnable executive experience.

Tasks:

- React/Vite UI,
- FastAPI backend,
- project creation flow,
- company/role/mode intake,
- mock research progress,
- static sample opportunity brief,
- report preview placeholder.

Acceptance:

- user can open app and walk through a polished fake experience.

## Phase 2 — Company Research Orchestrator

Goal: build the structured web research engine.

Tasks:

- create search query planner,
- resolve company identity,
- find official website,
- identify ticker if public,
- identify company type,
- extract segments,
- collect sources,
- rank source quality,
- store source records.

Acceptance:

- given company name, app creates structured `CompanyIntelligenceProfile`.

## Phase 3 — Peer Taxonomy and Competitive Intelligence

Goal: prevent bad comparisons.

Tasks:

- classify direct competitors vs adjacent peers,
- classify operators vs service companies vs vendors,
- search peer AI signals,
- extract competitive signals,
- score signal relevance and confidence.

Acceptance:

- app can explain why a company is a direct competitor, peer, vendor, or benchmark.

## Phase 4 — AI Opportunity Map

Goal: turn research into opportunity cards.

Tasks:

- create industry opportunity library,
- map company context to opportunity categories,
- rank opportunities by value/feasibility/risk,
- generate FOMO-aware but credible summaries.

Acceptance:

- app produces 5-10 opportunity cards for a company.

## Phase 5 — Open-Ended Strategy Q&A

Goal: support executive questions.

Tasks:

- implement question classifier,
- retrieve relevant company/peer/industry context,
- answer using structured format,
- suggest practical pilots,
- include technical leader questions when needed.

Acceptance:

- user can ask “What can we do for drilling engineers?” and receive specific, structured, company-aware suggestions.

## Phase 6 — Guided Pilot Intake

Goal: narrow one opportunity into a real pilot.

Tasks:

- create question templates by opportunity type,
- collect workflow/users/data/actions/risk/value,
- infer missing fields,
- keep language executive-friendly.

Acceptance:

- user can answer 8-12 guided questions and generate a complete pilot profile.

## Phase 7 — Readiness Scoring Engine

Goal: score readiness and explain blockers.

Tasks:

- implement scoring dimensions,
- define scoring rubrics,
- compute readiness score,
- generate strengths/blockers/actions,
- allow manual adjustment.

Acceptance:

- app produces a credible readiness scorecard.

## Phase 8 — Technical Bridge Generator

Goal: prepare technical follow-up without overwhelming the executive.

Tasks:

- generate data requirements,
- generate system/platform questions,
- generate cloud/security questions,
- generate tool/agent boundaries,
- generate evaluation plan,
- generate technical leader checklist.

Acceptance:

- report includes a useful technical appendix.

## Phase 9 — Report Generator

Goal: produce polished executive reports.

Tasks:

- markdown report template,
- PDF generation,
- source/citation appendix,
- company context section,
- opportunity map section,
- selected pilot section,
- readiness scorecard,
- roadmap,
- technical appendix.

Acceptance:

- user can export a professional PDF report.

## Phase 10 — Packaging and Distribution

Goal: make the app usable by non-developers.

Tasks:

- hosted demo,
- desktop packaging,
- one-click local launcher,
- example reports,
- sample companies,
- no-code user flow.

Acceptance:

- non-technical user can launch and generate a report without terminal usage.

---

## 17. Exact Build Order

1. Finalize product identity.
2. Create executive UX wireframe.
3. Build landing/company intake screen.
4. Build research progress screen.
5. Create company research schema.
6. Create source record schema.
7. Build search query planner.
8. Build company identity resolver.
9. Build company profile extractor.
10. Build peer taxonomy module.
11. Build competitive signal extractor.
12. Create opportunity card schema.
13. Build industry opportunity library.
14. Build opportunity map generator.
15. Build open-ended strategy Q&A.
16. Build guided pilot intake.
17. Build readiness scoring engine.
18. Build technical bridge generator.
19. Build report template.
20. Build PDF export.
21. Build hosted demo and/or desktop packaging.
22. Add example reports and documentation.

---

## 18. MVP Definition of Done

The MVP is complete when:

1. A user can open the app without developer setup.
2. A user can enter a company name and role.
3. The app can research public company context.
4. The app can classify company type and peer groups.
5. The app can identify relevant AI/digital signals.
6. The app can create credible opportunity cards.
7. The app can answer open-ended executive strategy questions.
8. The app can guide a selected opportunity into a pilot plan.
9. The app can generate a readiness score.
10. The app can generate technical leader questions.
11. The app can export a polished PDF report.
12. The app hides technical configuration by default.
13. The app shows sources and confidence in an appendix.

---

## 19. Final Product Summary

AI Readiness Lab should be:

```text
C-level friendly at the front
deep research-driven underneath
structured enough to be better than generic ChatGPT
FOMO-aware but not cheesy
positive but credible
able to go from market pressure to pilot plan
able to speak to both executives and technical leaders
```

The core product message:

> AI Readiness Lab helps enterprise leaders understand where they stand on AI, where competitors are moving, and which practical AI pilot they should launch next.

The core report message:

> You may not need a massive AI transformation program to start. You need the right first pilot, scoped with the right data, risk controls, evaluation plan, and executive ownership.

