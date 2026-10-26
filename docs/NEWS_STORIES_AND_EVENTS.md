# ATLAS Financial News Story Intelligence and Event Classification System (Stage 101)

## Executive Summary

Stage 101 introduces institutional-grade news story clustering, multi-source narrative grouping, and evidence-grounded financial event classification to the ATLAS News platform (`/news`). Building directly on Stage 99 (Canonical News Foundation) and Stage 100 (News Discovery, Search & Timelines), Stage 101 elevates unstructured financial journalism into structured, traceable intelligence records without ever fabricating events, guessing unverified valuations, or confusing journalistic speculation with verified corporate execution.

---

## 1. Frozen Roadmap Verification & Scope

### Canonical Sequence
- **Stage 99:** Canonical News Foundation (articles, publishers, providers, revisions, provenance, licensing).
- **Stage 100:** News Discovery, Advanced Search, Facets & Chronological Timelines.
- **Stage 101 (Current):** News Story Grouping, Evidence-Based Financial Event Classification, and Cross-Publisher Coverage Intelligence.
- **Stage 102:** Advanced News Intelligence and Sentiment/Impact Quantification (deferred).
- **Stage 103:** News Module Completion (deferred).
- **Stage 104:** Research Module Kickoff (deferred).

### Guardrails
1. **Primary Route:** Operates strictly within `/news`. All 20 canonical ATLAS top-level routes remain intact.
2. **No Second Master Store:** Strictly reuses canonical Stage 99 `NewsArticle` records as the immutable basis.
3. **Zero Generative Hallucinations:** Stories use source-grounded headlines; no LLM-generated narrative theses or unverified claims.
4. **Zero Impact or Sentiment Speculation:** No predicted price movement, abnormal return forecasts, or trading signals.
5. **No Trading Side Effects:** Zero order execution, brokerage routing, or portfolio mutation.

---

## 2. Conceptual Separation: Article vs. Story Thread vs. Financial Event

ATLAS maintains strict conceptual and operational boundaries between three distinct objects:

```
+-----------------------------------------------------------------------------------+
| 1. CANONICAL NEWS ARTICLE (Stage 99)                                              |
| A source-specific, published text record with immutable provenance and licensing. |
+-----------------------------------------------------------------------------------+
                                         |
                                         | (Member of)
                                         v
+-----------------------------------------------------------------------------------+
| 2. CANONICAL STORY THREAD (Stage 101)                                             |
| An evolving coverage cluster of multiple articles tracking a developing           |
| journalistic narrative across time and independent newsrooms.                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         | (Evidences / Contains)
                                         v
+-----------------------------------------------------------------------------------+
| 3. CANONICAL FINANCIAL EVENT (Stage 101)                                          |
| An auditable, structured assertion of an identifiable corporate action, economic   |
| policy shift, or market development supported by explicit source evidence citations.|
+-----------------------------------------------------------------------------------+
```

- **One Story Thread may contain multiple Events:** E.g., an acquisition narrative progressing from initial rumors to formal agreement, antitrust regulatory review, and final closing.
- **One Article may report multiple Events:** E.g., a quarterly corporate report announcing earnings results, revised annual guidance, a new dividend declaration, and an executive board retirement.
- **One Event may have multiple Supporting Articles:** E.g., an official central bank policy rate decision reported and analyzed across Reuters, Bloomberg, and Financial Times.

---

## 3. Canonical Story Threads & Conservative Clustering

### Data Model
- **Identifier:** Deterministic, stable ID `story-<sha256(lead_article_id)[:16]>`.
- **Display Title:** Sourced directly from the qualified lead representative article.
- **Entities:** Bound to verified canonical Company Entities (`entity_id`) and Instruments.
- **Timestamps:** Preserves `first_source_published_at`, `latest_source_published_at`, and `first_seen_at`.
- **Operational Status:** Tracks `ACTIVE`, `QUIET`, `ARCHIVED`, `MERGED`, and `WITHDRAWN_FROM_DISPLAY`.

### Candidate Blocking & Matching Rules
To prevent costly all-to-all comparisons across millions of historical records, clustering applies candidate blocking:
1. **Entity Blocking:** Must share at least one verified canonical entity.
2. **Temporal Window:** Restricts candidate retrieval to bounded windows (7 days for earnings, 30 days for corporate transactions, 3 days for macro releases).
3. **Event Context Validation:** Articles are only clustered if they share specific event context or narrative keywords (e.g. `acquisition`, `merger`, `earnings`, `dividend`, `rate decision`). Entity overlap alone is strictly insufficient to merge articles into a story.
4. **False-Positive Guard:** Distinct transactions by the same company on different dates or with different transaction values are kept in separate story threads.

### Syndication vs. Independent Newsroom Reporting
- Republishing a single wire release (e.g., PR Newswire or BusinessWire) across multiple aggregator sites constitutes a syndicated copy, not independent verification.
- `independent_publisher_count` calculates the count of distinct, non-syndicated publishing organizations, providing traders and researchers with true cross-newsroom breadth metrics.

### Administrative Merges and Splits
- **Controlled Merge:** When two developing threads are verified to represent the same underlying story, an administrative merge points member articles to the target story, preserving redirection aliases and audit records.
- **Controlled Split:** Erroneously grouped articles can be split into a new story thread without loss of underlying evidence or article relationships.

---

## 4. Canonical Financial Event Taxonomy & Classification

ATLAS Stage 101 implements a versioned 20-category Event Taxonomy cataloging corporate announcements, capital transactions, governance updates, and macroeconomic actions:

| Event Type ID | Family | Description |
|---|---|---|
| `EARNINGS_RELEASE` | Corporate Earnings | Periodic quarterly/annual financial results disclosure |
| `EARNINGS_GUIDANCE` | Corporate Earnings | Forward-looking management estimates for revenue/profit |
| `DIVIDEND_DECLARATION` | Corporate Actions | Cash or stock dividend declaration, record & pay dates |
| `SHARE_BUYBACK_AUTHORIZATION`| Corporate Actions | Board authorization for common share repurchase programs |
| `MERGER_ACQUISITION_PROPOSAL`| M&A / Corporate Transactions | Preliminary offer, expression of interest, or bid |
| `MERGER_ACQUISITION_AGREEMENT`| M&A / Corporate Transactions | Definitive, executed transaction agreement |
| `MERGER_ACQUISITION_COMPLETION`| M&A / Corporate Transactions | Formal closing and completion of acquisition |
| `MERGER_ACQUISITION_TERMINATION`| M&A / Corporate Transactions | Cancellation or mutual termination of deal |
| `EQUITY_FINANCING_ANNOUNCEMENT`| Capital Markets | Common/preferred stock offering, IPO, or private placement |
| `DEBT_FINANCING_ANNOUNCEMENT`| Capital Markets | Bond issuance, syndicated loan facility, or note offering |
| `EXECUTIVE_APPOINTMENT` | Governance & Leadership | Appointment of CEO, CFO, COO, or Board Director |
| `EXECUTIVE_DEPARTURE` | Governance & Leadership | Resignation, retirement, or departure of senior executive |
| `REGULATORY_INVESTIGATION_ANNOUNCEMENT` | Regulatory & Legal | Formal inquiry or investigation by regulatory body |
| `REGULATORY_ENFORCEMENT_ACTION` | Regulatory & Legal | Imposition of fines, sanctions, injunctions, or penalties |
| `LITIGATION_FILING` | Regulatory & Legal | Material lawsuit or court complaint initiated |
| `BANKRUPTCY_RESTRUCTURING_FILING` | Restructuring | Chapter 11/7, insolvency, or debt workout proceeding |
| `PRODUCT_LAUNCH_ANNOUNCEMENT` | Commercial & Operations | Commercial release of significant new product or service |
| `FACILITY_EXPANSION_ANNOUNCEMENT` | Commercial & Operations | Capital expenditure for factory, data center, or plant |
| `CENTRAL_BANK_POLICY_DECISION` | Macroeconomic Policy | Interest rate change/hold, asset purchases, reserve ratio |
| `ECONOMIC_RELEASE_ANNOUNCEMENT` | Macroeconomic Policy | Scheduled release of GDP, CPI, nonfarm payrolls, PMI |

---

## 5. Event Qualification: Assertion vs. Lifecycle

ATLAS strictly separates the journalistic assertion state from the real-world deal lifecycle:

### Assertion Status
- `OFFICIALLY_REPORTED`: Explicit company disclosure, regulatory filing, or official press statement.
- `THIRD_PARTY_REPORTED`: Reputable journalistic reporting citing confirmed records.
- `RUMORED`: Reports citing unnamed persons, anonymous sources, or early preliminary discussions.
- `ALLEGED`: Claims, civil complaints, or accusations not yet adjudicated.
- `DENIED`: Sourced corporate denial of rumors or claims.
- `DISPUTED`: Conflicting claims between credible parties.
- `CORRECTED`: Prior erroneous claims corrected by the publisher.

### Lifecycle Status
- `PROPOSED`: Proposed transaction or non-binding offer.
- `ANNOUNCED`: Formally announced definitive transaction or action.
- `PENDING`: Transaction pending shareholder or regulatory approval.
- `APPROVED`: Received formal regulatory or shareholder clearance.
- `COMPLETED`: Fully executed, closed, or effective.
- `CANCELLED`: Abandoned, terminated, or withdrawn.

### Financial Rigor Rules
1. **Rumors are NEVER Completed:** A headline "Company X rumored to acquire Company Y" is classified as `MERGER_ACQUISITION_PROPOSAL` with assertion `RUMORED` and lifecycle `PROPOSED`.
2. **Investigations are NOT Findings:** An antitrust inquiry announcement is classified as `REGULATORY_INVESTIGATION_ANNOUNCEMENT` with lifecycle `PENDING`. It is never labeled a violation.
3. **Guidance is NOT Actuals:** Management forward estimates are classified as `EARNINGS_GUIDANCE`, strictly separate from reported actuals in `EARNINGS_RELEASE`.

---

## 6. Financial Magnitude & Participant Resolution

### Structured Monetary Extraction
`EventAmount` captures quantitative figures directly from source text without speculative extrapolation:
- **Amount Types:** `TRANSACTION_VALUE`, `DIVIDEND_PER_SHARE`, `BUYBACK_TOTAL_VALUE`, `FINANCING_AMOUNT`, `REVENUE_REPORTED`, `NET_INCOME_REPORTED`, `POLICY_RATE_TARGET`.
- **Approximations:** `EXACT`, `APPROXIMATE`, `RANGE_MIN`, `RANGE_MAX`, `ESTIMATED`.
- **Currency & Scale:** Handles standard international currencies (`USD`, `EUR`, `GBP`, `JPY`, `INR`) and indigenous numbering scales (`crore`, `lakh`).
- **No Guessed Valuations:** If an acquisition article does not disclose the purchase price, the value remains `None`; ATLAS never guesses from market capitalization.

### Participant Roles
Participants link to canonical Entity IDs with verified transactional roles:
- `PRIMARY_SUBJECT`: Main reporting target.
- `ACQUIRER` vs. `TARGET`: Bidder and acquisition subject.
- `REGULATOR`: Governing body (SEC, FTC, DOJ, RBI, ECB, Fed).
- `ISSUER`, `LENDER`, `UNDERWRITER`: Debt/equity financing parties.
- `EXECUTIVE`: Appointed or departing corporate officer.

---

## 7. Temporal Precision & Evidence Lineage

### Four Independent Time Dimensions
1. `event_date`: Alleged calendar occurrence date (supports exact, day, or month precision).
2. `announcement_time`: Timestamp of formal public announcement.
3. `published_at`: Timestamp when the specific news article was published.
4. `first_seen_at`: Timestamp when ATLAS first ingested the evidence.

### Point-in-Time Integrity
Timelines and historical queries do not exhibit look-ahead bias: subsequent corrections or post-dated disclosures are never back-dated into earlier queries as if known at the time.

### Structured Source Citations
Every event record is linked to one or more `NewsEventEvidence` citations containing:
- Canonical Article ID & Revision ID.
- Source Provider ID & Publisher ID.
- Evidence Type (`OFFICIAL_PRESS_RELEASE`, `REGULATORY_FILING`, `COMPANY_DISCLOSURE`, `CENTRAL_BANK_RELEASE`, `WIRE_REPORT`, `PUBLISHER_REPORT`).
- Permitted quotation excerpt and assertion role.

---

## 8. REST API Reference

All endpoints reside under `/api/v1/news` and enforce authentication and entitlement boundaries:

### Story Threads
- `GET /api/v1/news/stories` — Filterable feed of Story Threads with pagination and entity filters.
- `GET /api/v1/news/stories/{story_id}` — Detailed Story Thread record.
- `GET /api/v1/news/stories/{story_id}/articles` — Chronological member articles with newsroom attribution.
- `GET /api/v1/news/stories/{story_id}/events` — Linked financial event records.

### Financial Events
- `GET /api/v1/news/events` — Structured financial event feed with type, status, and entity filters.
- `GET /api/v1/news/events/{event_id}` — Detailed event record with participants and amounts.
- `GET /api/v1/news/events/{event_id}/evidence` — Authorized source evidence citations and quotes.
- `GET /api/v1/news/events/types` — Canonical 20-type Financial Event taxonomy catalog.
- `GET /api/v1/news/entities/{entity_id}/events` — Entity-specific corporate and macro event timeline.

---

## 9. Verification & Automated Test Suite

Stage 101 features comprehensive automated testing across backend, frontend, and build systems:

1. **Backend Test Suite (`uv run pytest tests/test_news_story_intelligence_v1.py tests/test_news_discovery_v1.py tests/test_news_v1.py`):**
   - **74 passing tests** in 8.00 seconds.
   - Verified candidate blocking, false-positive protection, syndication vs independent newsroom counts, rate holds, rumors vs official statements, amount parsing, and REST endpoints.
2. **Backend Ruff Lint (`uv run ruff check python/atlas/src/atlas/news/ apps/api/src/atlas_api/routers/news.py`):**
   - **0 errors** (All checks passed cleanly).
3. **Frontend Test Suite (`cmd /c pnpm --filter web test`):**
   - **46 passing tests** covering Stage 99, 100, and 101 types, contracts, and logic.
4. **TypeScript Verification (`cmd /c npx tsc --noEmit`):**
   - **0 errors** across entire `apps/web`.
5. **Next.js Production Build (`cmd /c pnpm --filter web build`):**
   - Turbopack compilation and page data collection passed in 3.2s with **0 errors**.

---

## 10. Next Canonical Stage

Stage 101 is complete. Following the canonical 150-stage roadmap, the next sequential phase is **Stage 102: Advanced Financial News Intelligence, Sentiment Quantification & Cross-Asset Market Impact Analysis**. No Stage 102 implementation has been started during Stage 101.
