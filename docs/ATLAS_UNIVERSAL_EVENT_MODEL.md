# ATLAS — Universal Event Model and Global Financial Event Foundation

**Canonical Stage:** Stage 135 of 150  
**Status:** Institutional Production Grade  
**Primary Modules:** `/intelligence`, `/news`, `/economics`, `/companies`, `/markets`, `/research`, `/maps`, `/data`

---

## 1. Executive Architecture Summary

The **Universal Event Model** establishes a single reliable, immutable, and strictly verified canonical representation (`AtlasUniversalEvent`) for significant real-world events across the ATLAS platform. It bridges financial disclosures, macroeconomic releases, central bank rate decisions, regulatory enforcements, international sanctions, corporate actions, geopolitical statements, and satellite/physical observations into a unified intelligence substrate.

### Core Architectural Invariants:
1. **Separation of Real-World Event vs. Source Document vs. Assertion Claim:**
   - A **Canonical Event** is the objective real-world occurrence, scheduled announcement, or formal policy action.
   - An **Event Source Record** is an external article, filing, release, feed, or bulletin from an authorized provider.
   - An **Event Evidence Link** binds a source record to an event with explicit roles (`PRIMARY_SOURCE`, `OFFICIAL_CONFIRMATION`, `CORROBORATING_SOURCE`, etc.).
   - An **Event Claim** is a granular factual predicate asserted by a source.
2. **Never Deduplicate Solely on Title or Headline Similarity:**
   - Deduplication evaluates type-specific deterministic canonical keys (`FINANCIAL.EARNINGS:AAPL:2026:3`, `ECONOMIC:US_NFP:US:2026-12:INITIAL`, `NATURAL_DISASTER.EARTHQUAKE:US7000M4WZ`).
   - Similar headlines for separate corporate actions (e.g. *Merger Announced* vs *Merger Completed*) or distinct geographic events (two separate earthquakes on the same day) remain strictly separate canonical events.
3. **Bitemporal History with Strictly Zero Look-Ahead Bias:**
   - Valid Time (when the event occurred/applied) is orthogonal to Knowledge Time (when ATLAS learned of it).
   - Historical queries evaluated `as_of(T)` reflect only information and revisions known to the platform at $T \le \text{as\_of\_time}$. Future benchmark restatements, seismologist adjustments, or wire retractions published after $T$ are invisible to the evaluation.
4. **Preservation of Source Discrepancies Without Synthetic Fabrication:**
   - If two authorized news wires or regulatory feeds report conflicting numbers (e.g., casualties, deal valuations, or initial estimates), both claims are preserved with attribution.
   - The platform flags `claim_conflict_status: CONFLICT_DETECTED` and never fabricates synthetic mathematical averages.
5. **Formal Retraction and Tombstoning:**
   - When a wire issues an official retraction of a false release or hoax, the canonical event is marked `is_retracted = True` and tombstoned with its retraction rationale. It is excluded from standard search queries while remaining historically auditable.

---

## 2. Universal Taxonomy & Classification

The ATLAS Universal Event Taxonomy enforces 12 top-level categories and dozens of versioned subtypes:

| Category | Primary Subtypes | Key Payload Schema |
| :--- | :--- | :--- |
| `FINANCIAL` | `FINANCIAL.EARNINGS_RELEASE`, `FINANCIAL.EARNINGS_GUIDANCE_CHANGE`, `FINANCIAL.DIVIDEND_ANNOUNCED`, `FINANCIAL.SHARE_REPURCHASE`, `FINANCIAL.DEBT_ISSUANCE`, `FINANCIAL.CREDIT_RATING_ACTION` | `EarningsEventPayload` (EPS, Revenue, surprises) |
| `CORPORATE` | `CORPORATE.M_AND_A.ANNOUNCED`, `CORPORATE.M_AND_A.APPROVED`, `CORPORATE.M_AND_A.COMPLETED`, `CORPORATE.DIVESTITURE`, `CORPORATE.EXECUTIVE_APPOINTMENT`, `CORPORATE.BANKRUPTCY_FILING` | `CorporateActionEventPayload` (issuer, target, deal value) |
| `ECONOMIC` | `ECONOMIC.CPI_RELEASE`, `ECONOMIC.PPI_RELEASE`, `ECONOMIC.GDP_RELEASE`, `ECONOMIC.EMPLOYMENT_REPORT`, `ECONOMIC.PMI_RELEASE`, `ECONOMIC.TRADE_BALANCE` | `EconomicReleasePayload` (indicator, reporting period, vintage) |
| `MONETARY_POLICY` | `MONETARY_POLICY.RATE_DECISION`, `MONETARY_POLICY.STATEMENT_RELEASE`, `MONETARY_POLICY.MINUTES_RELEASE`, `MONETARY_POLICY.BALANCE_SHEET_POLICY` | `CentralBankEventPayload` (rates, basis points math, target bounds) |
| `REGULATORY` | `REGULATORY.RULE_PROPOSAL`, `REGULATORY.RULE_ADOPTION`, `REGULATORY.RULE_EFFECTIVE`, `REGULATORY.ENFORCEMENT_ACTION`, `REGULATORY.INVESTIGATION` | `RegulatoryEventPayload` (agency, matter reference, deadlines) |
| `SANCTIONS` | `SANCTIONS.DESIGNATION`, `SANCTIONS.AMENDMENT`, `SANCTIONS.DELISTING`, `SANCTIONS.GENERAL_LICENSE` | `SanctionsEventPayload` (authority, program, legal subject ID) |
| `GEOPOLITICAL` | `GEOPOLITICAL.DIPLOMATIC_RELATIONS`, `GEOPOLITICAL.TREATY_RATIFICATION`, `GEOPOLITICAL.TRADE_RESTRICTION`, `GEOPOLITICAL.TERRITORIAL_DISPUTE` | `GeopoliticalEventPayload` (actor jurisdiction, target, accords) |
| `NEWS_REPORTED` | `NEWS.MEDIA_REPORT`, `NEWS.CANDIDATE_RUMOR`, `NEWS.LEAK_UNCONFIRMED` | Unverified candidates, preserved with wire attribution |
| `NATURAL_DISASTER` | `NATURAL_DISASTER.EARTHQUAKE`, `NATURAL_DISASTER.WILDFIRE`, `NATURAL_DISASTER.SEVERE_WEATHER`, `NATURAL_DISASTER.FLOOD`, `NATURAL_DISASTER.VOLCANO` | `PhysicalDisasterEventPayload` (hypocenter, magnitude, FRP MW) |
| `PHYSICAL_WORLD` | `PHYSICAL_WORLD.OBSERVATION`, `PHYSICAL_WORLD.FACILITY_ANOMALY` | Stage 134 observation bridge (`stage134_observation_id`) |
| `INFRASTRUCTURE` | `INFRASTRUCTURE.INCIDENT.EXPLOSION`, `INFRASTRUCTURE.GRID_OUTAGE`, `INFRASTRUCTURE.PIPELINE_SHUTDOWN` | Facility and network impact assertions |
| `OTHER_VERIFIED_EVENT` | Miscellaneous audited events | Flexible payload with cryptographic validation |

---

## 3. Orthogonal Lifecycle & Verification Dimensions

Events track two independent status dimensions:

### Lifecycle Status:
- `SCHEDULED`: Announced date in the future (e.g. FOMC meeting, upcoming earnings).
- `PROPOSED`: Regulatory or legislative rulemaking proposal.
- `ANNOUNCED`: Formal public announcement of a future action.
- `REPORTED`: Initially surfaced by a news wire or agency feed.
- `OCCURRED`: Physical or market event that took place.
- `CONFIRMED`: Corroborated and validated by official records.
- `POSTPONED`: Rescheduled to a future timestamp.
- `CANCELLED`: Calling off of an anticipated event.
- `SUPERSEDED`: Replaced by a newer formal event.
- `RETRACTED`: Formally withdrawn or debunked as false.
- `DISPUTED`: Contested by credible parties.

### Verification Status:
- `OFFICIALLY_CONFIRMED`: Verified via statutory filings (SEC EDGAR, Federal Register, OFAC).
- `INDEPENDENTLY_CORROBORATED`: Verified by two or more independent major news services.
- `SOURCE_REPORTED`: Asserted by a single recognized provider.
- `UNVERIFIED`: Anonymous report, leaked memo, or unconfirmed market rumor.
- `CONFLICTED`: Material contradictions detected across sources.
- `REJECTED`: Disproven fraudulent or fabricated claim.

---

## 4. Multi-Clock Temporal Architecture & As-Of Queries

Every `AtlasUniversalEvent` supports multiple chronological perspectives:
1. `occurred_at`: When the real-world action or physical disaster happened.
2. `source_published_at`: When the external provider broadcast the item.
3. `announced_at`: When an entity announced the future or present action.
4. `scheduled_for`: Scheduled execution time for planned events.
5. `effective_at`: When regulatory orders, tariffs, or interest rates take legal effect.
6. `first_ingested_at`: When ATLAS first ingested and processed the record.
7. `updated_at`: When the latest in-place revision was audited.

### Date Precision Tiers:
- `EXACT_TIMESTAMP`: Second/millisecond timestamp.
- `DATE_ONLY`: Year-Month-Day (e.g., shareholder meeting day).
- `MONTH_ONLY`: Fiscal or macroeconomic release month.
- `YEAR_ONLY`: Multi-year accord.
- `TIME_UNKNOWN`: Confirmed date with uncertain time of day.

---

## 5. Reference Seed Fixtures A through R

| Fixture | Scenario | Implementation & Invariant Verified |
| :--- | :--- | :--- |
| **A** | Duplicate earnings reports | 3 sources (PR Newswire, SEC EDGAR, Reuters) attach to 1 canonical event `FINANCIAL.EARNINGS:AAPL:2026:3`. |
| **B** | Scheduled vs reported earnings | Scheduled release for MSFT Q4 is updated in-place when results arrive; no duplicate event. |
| **C** | Economic indicator revisions | US Nonfarm Payrolls: Initial 250k on Jan 5 revised to 230k on Feb 2. Full revision history recorded. |
| **D** | Monetary policy basis points math | ECB policy rate hike: 3.75% to 4.00% automatically evaluates change as `+25.0 bps`. |
| **E** | Central bank target ranges | FOMC Fed Funds 5.25%–5.50% target range preserves both bounds in title and payload. |
| **F** | Sanctions exact legal match | SOVZVEZDA AVIATION LLC designated by OFAC; unrelated SOVZVEZDA LOGISTICS CJSC is not falsely matched. |
| **G** | Sanctions amendment | Updating existing SDN identifiers classified as `AMENDMENT` without duplicate initial designation. |
| **H** | Corporate merger milestones | Acme acquiring Beta: `MERGER_ANNOUNCED` vs `MERGER_COMPLETED` tracked as distinct events. |
| **I** | Earthquake in-place revision | USGS earthquake `us7000m4wz` revised from M5.2 to M5.4 in-place; revision 2 recorded. |
| **J** | Separate distinct earthquakes | Two quakes on same day with different USGS IDs (`us7000m4wz` vs `us7000m4x1`) remain separate. |
| **K** | News rumors qualified as candidates | Market rumors remain `UNVERIFIED` candidates and are never auto-confirmed as official events. |
| **L** | Date-only event precision | Amazon shareholder meeting stored with `DatePrecision.DATE_ONLY`. |
| **M** | Historical as-of query | Querying as-of Jan 10 yields Nonfarm Payrolls at 250k; Feb 2 revision is strictly excluded. |
| **N** | Conflicting source claims | Port of Rotterdam explosion casualty reports (12 vs 25 injuries) preserved; no synthetic average. |
| **O** | Retraction and tombstoning | Hoax acquisition press release tombstoned with `is_retracted=True`; excluded from standard search. |
| **P** | Source licensing enforcement | Licensed sources (EDGAR) permitted for permanent archive; restricted scraping feeds blocked. |
| **Q** | Multi-tenant isolation | Tenant-private portfolio rebalance events isolated from unauthorized tenants. |
| **R** | Stage 134 physical observation bridge | Bridged NASA FIRMS thermal anomaly `obs-fire-20260904-098` without duplicate entity generation. |

---

## 6. REST API Endpoints

All endpoints are hosted under `/api/v1/events`:

- `GET /capabilities`: Return supported clocks, precisions, taxonomy versions, and adapter registry.
- `GET /types`: Category-to-subtype taxonomy hierarchy.
- `GET /sources`: Authorized data providers, retention rules, and licensing tiers.
- `GET /search`: Search and filter canonical events via GET query parameters.
- `POST /query`: Structured parameter search.
- `GET /timeline`: Multi-clock sorted event feed with date buckets.
- `GET /upcoming`: Scheduled future earnings, economic releases, and central bank decisions.
- `GET /recent`: Recently verified historical events.
- `POST /as-of`: Point-in-time historical evaluation enforcing zero look-ahead bias.
- `POST /deduplicate`: Dry-run deduplication and match confidence analysis for candidate payloads.
- `POST /merge`: Non-destructive merge of duplicate canonical events with complete audit receipt.
- `POST /split`: Safe splitting of mistakenly merged events into distinct canonical entities.
- `POST /retract`: Formal retraction and tombstoning of erroneous or fraudulent events.
- `GET /review-queue`: Candidate events with ambiguous match scores awaiting human analyst review.
- `POST /review-queue/{review_id}/resolve`: Resolve review queue item (`CONFIRMED_MERGE` or `CONFIRMED_SEPARATE`).
- `GET /{event_id}`: Canonical event summary.
- `GET /{event_id}/evidence`: Supporting evidence links and snippets.
- `GET /{event_id}/claims`: Granular source claims and conflict evaluations.
- `GET /{event_id}/revisions`: Immutable revision audit history.
- `GET /{event_id}/sources`: Linked external source records.
