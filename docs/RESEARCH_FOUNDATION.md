# Canonical Financial Research Platform Foundation (Stage 104)

## Master Architectural Documentation

**Project:** ATLAS — AI-Native Financial Intelligence and Quantitative Research Operating System  
**Canonical Roadmap Position:** Stage 104 of 150  
**Module:** Research  
**Primary Route:** `/research`  
**Quality Standard:** Production-oriented, institutional-grade, source-verified, auditable, and secure

---

## 1. Executive Summary & Purpose

Stage 104 establishes the foundational **ATLAS Financial Research Platform**, introducing research as an authentic, first-class, persistent, and evidence-driven domain within the financial intelligence operating system.

The platform provides a dedicated environment for analysts, institutional investors, and researchers to:
- Investigate canonical public companies, financial instruments, industries, and macroeconomic environments.
- Formulate structured research questions and hypotheses.
- Maintain structured, revision-tracked research notes and thesis documents.
- Anchor claims with verified supporting and contradicting evidence linked directly to official regulatory filings, fundamental financial statements, verified financial news, and economic releases.
- Maintain persistent citations with source locations (pages, sections, tables, paragraphs) and license-bounded quotations.
- Track source revisions, restatements, vintages, and handling of broken or withdrawn documents.
- Review auditable activity timelines.

### Strict Non-Autonomous & Non-Trading Boundaries
Stage 104 strictly defines the foundational domain, models, APIs, and analyst workspace:
- **No autonomous AI research agents** fabricating conclusions or investment ratings.
- **No automated price target generation** or hallucinated consensus forecasts.
- **No trading orders, broker execution, or portfolio mutations**. Research is an analytical and observational workspace.
- **No duplicate document or entity systems**; Stage 104 strictly reuses canonical Companies (Stage 18), Filings (Stage 86), Fundamentals (Stage 82), News (Stages 99–103), and Economics (Stages 89–93).

---

## 2. Research Domain Architecture & Data Flow

```
ATLAS AUTHENTICATED APPSHELL (/research)
                   |
                   v
         RESEARCH WORKSPACE
                   |
     +-------------+-------------+
     |                           |
     v                           v
INVESTIGATIONS             SOURCE DISCOVERY
     |                           |
     v                           v
RESEARCH QUESTIONS         CANONICAL DOCUMENTS
     |                     - SEC Filings (10-K, 10-Q)
     v                     - Financial Statement Facts
RESEARCH HYPOTHESES        - News Articles & Events
     |                     - Economic Releases & CPI
     v                     - Market Instruments
STRUCTURED NOTES                 |
     |                           v
RESEARCH CLAIMS <=======> RESEARCH EVIDENCE
(Fact vs Interpretation)  (Granular Locations & Excerpts)
                                 |
                                 v
                       CITATION & PROVENANCE
                                 |
                                 v
                       AUDITABLE ACTIVITY LOG
```

---

## 3. Canonical Domain Entities & Data Contracts

### 3.1 Research Investigation (`ResearchInvestigation`)
- **`investigation_id`**: Immutable stable identifier (`inv-{uuid10}`).
- **`owner_user_id`**: Authenticated principal owner. Enforces strict cross-user RLS isolation.
- **`title`**: User-authored sanitized title (max 500 chars).
- **`research_type`**: Controlled taxonomy:
  - `COMPANY_RESEARCH`
  - `SECURITY_RESEARCH`
  - `INDUSTRY_RESEARCH`
  - `MACROECONOMIC_RESEARCH`
  - `MARKET_RESEARCH`
  - `FINANCIAL_EVENT_RESEARCH`
  - `GENERAL_FINANCIAL_RESEARCH`
- **`primary_subject_entity_id`**: Canonical entity ID or ticker (`AAPL`, `MSFT`, `NVDA`, `US_CPI`, `FED`).
- **`primary_subject_type`**: Scope category (`COMPANY`, `INSTRUMENT`, `INDUSTRY`, `MACROECONOMIC`, `GEOGRAPHY`).
- **`secondary_entity_ids`**: Multi-entity scope list.
- **`research_objective`**: Primary thesis statement or inquiry.
- **`status`**: Lifecycle state (`DRAFT`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `ARCHIVED`).
- **`revision`**: Integer counter incremented on every mutation, enforcing optimistic concurrency.

### 3.2 Research Question (`ResearchQuestion`)
- Specific inquiries formulated by the analyst.
- Status: `OPEN`, `UNDER_REVIEW`, `ADDRESSED`, `DROPPED`.
- Zero automatic truth inference: linking evidence to a question never automatically marks it closed.

### 3.3 Research Hypothesis (`ResearchHypothesis`)
- **Hypothesis is not fact**: A proposition to test.
- Status: `PROPOSED`, `UNDER_TEST`, `SUPPORTED_BY_AVAILABLE_EVIDENCE`, `CONTRADICTED_BY_AVAILABLE_EVIDENCE`, `INCONCLUSIVE`, `RETIRED`.
- Prevents algorithmic bias: contradictory evidence is first-class, and lack of evidence explicitly defaults to `INCONCLUSIVE` rather than fake probabilities.

### 3.4 Structured Research Notes (`ResearchNote`) & Revisions
- Analyst-authored structured rich text and markdown documents.
- Note types: `OBSERVATION`, `QUESTION`, `HYPOTHESIS`, `ASSUMPTION`, `ANALYSIS`, `CONCLUSION`, `GENERAL_NOTE`.
- Status: `DRAFT`, `IN_PROGRESS`, `REVIEWED`, `ARCHIVED`.
- Revision tracking: Every edit creates an immutable point-in-time snapshot (`ResearchNoteRevision`) with revision number, author, and timestamp.
- Concurrency protection: Stale writes (`expected_revision != current_revision`) return typed 409 Conflict.
- Security: Rich text is sanitized to neutralize dangerous HTML elements (`<script>`, `<iframe>`, `javascript:` schemes, and event handlers).

### 3.5 Research Claims & Fact-versus-Interpretation Distinction (`ResearchClaim`)
- **Claim Categories**:
  - `SOURCE_REPORTED_FACT`: Verified reporting by an identified source (e.g. "Apple Form 10-K reported FY2024 Total Net Sales of $391,035M USD").
  - `ANALYST_INTERPRETATION`: Analyst-derived synthesis or opinion.
  - `ASSUMPTION`: Operating assumption adopted for modeling.
  - `ESTIMATE`: Forward projections, distinctly separated from actual historical numbers.
  - `OPEN_QUESTION`: Unresolved question.
- **Evidence Status**:
  - `SUPPORTED_BY_CITED_SOURCE`
  - `PARTIALLY_SUPPORTED`
  - `CONTRADICTED`
  - `INSUFFICIENT_EVIDENCE`
  - `NOT_REVIEWED`
  - `SOURCE_UNAVAILABLE`
  - `SOURCE_WITHDRAWN`

### 3.6 Canonical Research Source References (`ResearchSourceReference`)
- Source reference pointers reusing canonical ATLAS records rather than duplicating files:
  - Official SEC EDGAR Filings (Stage 86): Apple 10-K FY24, Apple 10-Q Q3 2024, Microsoft 10-K, Nvidia 10-K.
  - Fundamental Financial Statement Facts (Stage 82): Reporting period, unit, currency, and revision tags.
  - Financial News Articles (Stage 99–103): Bloomberg, Reuters, Financial Times, WSJ with publication timestamps.
  - Economic Datasets (Stage 89–93): BLS CPI, Nonfarm Payrolls, Fed Interest Rate Decisions with observation vintages.
- Deduplication: Ingestion deduplicates by exact canonical document ID or normalized URL.
- URL Security: External URLs are validated against SSRF, blocking loopback addresses (`127.0.0.1`), private subnets (`192.168.0.0/16`, `10.0.0.0/8`), and cloud metadata endpoints (`169.254.169.254`).

### 3.7 Research Evidence & Citation Infrastructure (`ResearchEvidence`, `ResearchCitation`)
- **Granular Locations**: Cites exact document structure (`PAGE`, `SECTION`, `PARAGRAPH`, `TABLE`, `ROW`, `DATA_POINT`). Zero fabricated page numbers or nonexistent filing sections.
- **Bounded Excerpts**: Quotations bounded to permissible licensed lengths (max 5,000 characters).
- **Citations**: Stable identifiers (`cit-{uuid8}`) rendering human-readable labels:
  - e.g. `[SEC Form 10-K FY2024, Item 1A, p. 6]`
  - e.g. `[Apple FY2024 Operating Income: $123,216M USD]`
- **Integrity & Broken Handling**: Citations whose underlying evidence or source is withdrawn or deleted are visibly marked as `[Broken Citation]` with explanatory reason.

### 3.8 Auditable Activity Timeline (`ResearchActivity`)
- Chronological append-only audit trail logging all mutations (`INVESTIGATION_CREATED`, `NOTE_CREATED`, `NOTE_UPDATED`, `QUESTION_ADDED`, `EVIDENCE_ATTACHED`, etc.).

---

## 4. REST API Endpoint Catalog

All research endpoints are mounted under `/api/v1/research`:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/research/overview` | Dashboard summary metrics, counts, and recent activity |
| GET | `/api/v1/research/investigations` | Filterable list of user-owned investigations |
| POST | `/api/v1/research/investigations` | Create new research investigation |
| GET | `/api/v1/research/investigations/{id}` | Read investigation details and enriched artifact counts |
| PATCH | `/api/v1/research/investigations/{id}` | Revision-safe update with optimistic concurrency |
| POST | `/api/v1/research/investigations/{id}/archive` | Archive an investigation |
| DELETE | `/api/v1/research/investigations/{id}` | Delete investigation and associated links |
| GET | `/api/v1/research/investigations/{id}/activity` | Chronological activity audit log for investigation |
| GET | `/api/v1/research/investigations/{id}/questions` | List research questions for investigation |
| POST | `/api/v1/research/investigations/{id}/questions` | Add research question |
| PATCH | `/api/v1/research/questions/{id}` | Update question text, status, or entity links |
| DELETE | `/api/v1/research/questions/{id}` | Remove research question |
| GET | `/api/v1/research/investigations/{id}/hypotheses` | List hypotheses for investigation |
| POST | `/api/v1/research/investigations/{id}/hypotheses` | Propose research hypothesis |
| PATCH | `/api/v1/research/hypotheses/{id}` | Update hypothesis status and claim links |
| DELETE | `/api/v1/research/hypotheses/{id}` | Delete hypothesis |
| GET | `/api/v1/research/investigations/{id}/notes` | List structured research notes |
| POST | `/api/v1/research/investigations/{id}/notes` | Author new structured note |
| GET | `/api/v1/research/notes/{id}` | Read structured note details |
| PATCH | `/api/v1/research/notes/{id}` | Update note with concurrency protection and revision snapshot |
| DELETE | `/api/v1/research/notes/{id}` | Delete research note |
| GET | `/api/v1/research/notes/{id}/revisions` | View point-in-time edit history for a note |
| GET | `/api/v1/research/investigations/{id}/claims` | List claims with fact-vs-interpretation breakdown |
| POST | `/api/v1/research/investigations/{id}/claims` | Record new claim or finding |
| PATCH | `/api/v1/research/claims/{id}` | Update claim statement, category, or evidence status |
| DELETE | `/api/v1/research/claims/{id}` | Delete claim |
| GET | `/api/v1/research/sources` | Search canonical research sources catalog |
| GET | `/api/v1/research/investigations/{id}/sources` | List sources linked to investigation |
| POST | `/api/v1/research/investigations/{id}/sources` | Link existing canonical source or register external reference |
| DELETE | `/api/v1/research/investigations/{id}/sources/{src_id}` | Unlink source from investigation |
| GET | `/api/v1/research/investigations/{id}/evidence` | List verified evidence attached to investigation |
| POST | `/api/v1/research/investigations/{id}/evidence` | Attach evidence with location reference and excerpt |
| DELETE | `/api/v1/research/evidence/{id}` | Remove evidence record (marks citation broken) |
| GET | `/api/v1/research/investigations/{id}/citations` | List formatted citations for investigation |
| GET | `/api/v1/research-documents/{entity_id}` | Legacy Stage 36 research document specialization row |

---

## 5. Frontend Workspace UI (`/research`)

The research user interface adheres strictly to Bloomberg-inspired institutional density:
1. **Research Overview**: Real user metrics (Active, Drafts, Completed, Notes authored, Sources linked, Evidence verified), Ongoing Investigations quick-launch table, and Recent Activity feed.
2. **Investigations Directory**: Filterable by Entity, Status, and Research Type with text search, revision badges, and quick-open actions.
3. **Investigation Workspace Console (3-Pane)**:
   - **Header**: Navigation breadcrumb, investigation title, status selector, entity tags, revision badge.
   - **Left Navigator**: Fast switching between `Notes`, `Questions`, `Hypotheses`, `Claims`, `Sources`, `Evidence`, `Activity`.
   - **Center Work Area**:
     - Note List + Markdown Note Editor with word counter, save/autosave indicators, and revision conflict warnings.
     - Question manager with status badges (`OPEN`, `UNDER_REVIEW`, `ADDRESSED`).
     - Hypothesis manager with evidence-testing statuses.
     - Claims panel clearly separating Source Facts from Analyst Interpretations.
     - Evidence manager with location reference linking.
   - **Right Inspector**: Detailed source & evidence inspector showing citable location reference, publication timestamp, reporting period, excerpt, and "Open Original Source ↗" button.
4. **Source Library**: Searchable catalog of official filings, financial statement facts, news articles, and economic releases with provenance inspector.
5. **Activity Timeline**: Full chronological audit log of all analyst activities.

---

## 6. Verification and Quality Gates

- **Backend Pytest**: 18 unit, integration, concurrency, RLS isolation, SSRF security, and activity audit tests pass with 100% success (`tests/test_research_foundation_v1.py`).
- **Regression Pytest**: 62 tests across Research, Filings (Stage 86), and News (Stages 99–103) pass cleanly.
- **Ruff Linter**: 0 errors across `atlas.research`, router, and test files.
- **Frontend Unit Tests**: 71 tests pass cleanly (`npx tsx --test src/lib/**/__tests__/*.test.ts`).
- **TypeScript Typecheck**: `npx tsc --noEmit` exits with 0 errors across the Next.js/React codebase.
- **Production Build**: `pnpm --filter web build` compiles cleanly with static generation of `/research`.

---

## 7. Roadmap Boundaries

- **Stage 104 Complete**: Research domain foundations, canonical investigations, structured notes, questions, hypotheses, claims, source integration, evidence, citations, activity logging, and professional analyst console.
- **Deferred to Stage 105+**: Advanced research workflows, qualitative and quantitative research pipelines, collaborative research review, and subsequent Research stages (105–109).
- **Stage 110+**: Portfolios begin at Stage 110.
- **Stage 120**: Global cross-module workspaces.
- **Stage 124–128**: Autonomous AI Assistant and agents.
