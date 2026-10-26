# Global Economic Calendar & Macroeconomic Release Intelligence (Stage 92)

## 1. Overview & Vision
The **ATLAS Global Economic Calendar** is an institutional-grade macroeconomic release and central bank event tracking system embedded within the `/economics` module. It serves as ATLAS's authoritative user-facing interface for scheduled economic publications, officially published macroeconomic statistics, and verified central-bank decisions.

The Economic Calendar is built with the analytical rigor, temporal accuracy, and dense information architecture required of institutional macroeconomic research and quantitative trading desks. Every event, timestamp, statistical observation, consensus forecast, and surprise metric is anchored in an authorized official source.

---

## 2. Core Architecture & Entity Model

```
ATLAS Authenticated AppShell
            │
            ▼
    Economics Module (/economics)
  (Stages 89, 90, 91, 92)
            │
            ▼
  Economic Calendar Workspace (Stage 92)
            │
 ┌──────────┴──────────────┬────────────────────────┐
 │                         │                        │
 ▼                         ▼                        ▼
Canonical Event Registry  Release Occurrences     User Event Alerts
- Stable Event ID         - Actual Observations   - Reminder Offset
- Release Family          - Consensus Snapshots   - Trigger Intents
- Geographic Entity (19)  - Statistical Surprises - Stage 49 Delivery
- Central Bank Ref (91)   - Revision History      - Quotas & Isolation
```

### 2.1 The Economic Event as a Distinct Domain Object
An economic calendar event represents a scheduled or historically documented official publication or central-bank action. It is fundamentally distinct from the statistical observations published within it.

A single release event (such as the *U.S. Consumer Price Index* or the *U.S. Employment Situation*) may publish multiple distinct macroeconomic series:
- **Event**: U.S. Consumer Price Index (October 2024 Release)
- **Observations Published**: Headline CPI YoY, Headline CPI MoM, Core CPI YoY, Core CPI MoM, Index Level

**Anti-Pattern Avoided**: Never create multiple duplicate calendar events simply because one official statistical publication releases several series observations simultaneously.

### 2.2 Release Families
A `ReleaseFamily` groups recurring macroeconomic series under a canonical official agency grouping:
- `fam-us-cpi`: Consumer Price Index (U.S. Bureau of Labor Statistics)
- `fam-us-nfp`: Employment Situation (U.S. Bureau of Labor Statistics)
- `fam-us-gdp`: Gross Domestic Product (U.S. Bureau of Economic Analysis)
- `fam-us-fomc`: FOMC Policy Decision (Federal Reserve)
- `fam-eu-hicp`: Harmonised Index of Consumer Prices (Eurostat)
- `fam-eu-ecb`: ECB Governing Council Rate Decision (European Central Bank)
- `fam-gb-cpi`: UK Consumer Price Index (Office for National Statistics)
- `fam-gb-boe`: Bank of England MPC Bank Rate Decision (Bank of England)
- `fam-jp-cpi`: National Consumer Price Index (Statistics Bureau of Japan)
- `fam-jp-boj`: Bank of Japan Monetary Policy Decision (Bank of Japan)
- `fam-in-cpi`: India All-India Consumer Price Index Combined (MoSPI)
- `fam-in-rbi`: RBI Monetary Policy Committee Policy Repo Rate Decision (RBI)
- `fam-cn-cpi`: China Consumer Price Index (National Bureau of Statistics)
- `fam-cn-pboc`: People's Bank of China Loan Prime Rate (PBoC / CFETS)

---

## 3. Temporal Semantics & Timezone Correctness

### 3.1 UTC Canonical Storage & IANA Civil Conversions
- **Storage**: All exact release instants are stored as timezone-aware UTC timestamps (`scheduled_start`, `published_at`).
- **Source Timezones**: The jurisdiction's native IANA timezone name is preserved (`source_timezone`), such as `America/New_York`, `Europe/London`, `Europe/Frankfurt`, `Asia/Tokyo`, `Asia/Kolkata`, or `Asia/Shanghai`.
- **User Display Timezones**: Events are converted dynamically to the user's selected civil timezone (`display_timezone`) for day-grouping, filtering, and table rendering.

### 3.2 Daylight Saving Time (DST) Correctness
UTC normalization prevents clock-skew errors across international daylight saving boundary transitions. Fall-back and spring-forward transitions are handled explicitly via Python's native `zoneinfo` database.

### 3.3 Schedule Precision & Date-Only Events
Releases adhere to source certainty via `SchedulePrecision`:
- `EXACT_INSTANT`: Exact verified minute/hour (e.g. 08:30:00 ET).
- `LOCAL_DATE_TIME`: Scheduled within a local operational window.
- `DATE_ONLY`: Source announces publication date without specifying a release hour.
- `UNKNOWN`: Unscheduled or time-unspecified event.

**Critical Rule**: Date-only events are never assigned midnight or fake hour stamps; they are identified as `Date Only` in display layers.

---

## 4. Release Lifecycle & Verification

The state machine for economic calendar events enforces verified lifecycle transitions:
- `SCHEDULED`: Confirmed on an official agency or central-bank schedule.
- `RESCHEDULED`: Official agency published a revised release date/time; previous schedule is preserved in `schedule_revisions`.
- `RELEASE_VERIFIED`: Official statistical report or central-bank decision has been verified by the source.
- `POSTPONED`: Officially postponed by source announcement.
- `CANCELLED`: Officially cancelled by source announcement.

**Integrity Principle**: The mere passage of scheduled clock time does not mark an event as released. Unverified past releases display `Release not yet verified`.

---

## 5. Statistical Observations, Vintages & Previous Values

### 5.1 Observation Reuse
Calendar actuals link directly to canonical economic observation IDs (`obs-us-cpi-202410`, `obs-eu-hicp-202410`, etc.) rather than maintaining a disconnected parallel store.

### 5.2 Release Stages
- `ADVANCE`: Initial estimate (e.g., BEA Advance GDP).
- `PRELIMINARY`: Secondary survey round (e.g., Eurostat Flash CPI).
- `FIRST_RELEASE`: Canonical initial release.
- `REVISED`: Subsequent statistical revision.
- `FINAL`: Closed reference period benchmark.

### 5.3 Previous Values & Revisions
The calendar distinguishes between:
- **Previously Reported Value**: The original observation value known prior to the new release.
- **Revised Previous Value**: When an agency updates the preceding reference period concurrently with releasing the new observation.

---

## 6. Pre-Release Consensus Forecasts

Consensus forecasts represent aggregated professional economist expectations:
- **Source Attribution**: Each forecast preserves its provider (`Bloomberg Survey`, `Reuters Consensus`, `Consensus Economics`, `CFETS`).
- **Aggregation Method**: `MEDIAN`, `MEAN`, `WEIGHTED_MEAN`, or `OFFICIAL_PROJECTION`.
- **Contributor Count**: Displayed when supplied by the survey provider.
- **Pre-Release Cutoff**: Consensus snapshots are frozen prior to official publication to prevent look-ahead contamination. Post-release updates cannot be back-applied to pre-release surprise calculations.
- **Missing State**: Unavailable forecasts display a neutral `—` rather than zero or synthetic estimates.

---

## 7. Statistical Surprise Engine

Economic surprises represent statistical deviations between actual released figures and pre-release consensus forecasts:
$$\text{Surprise} = \text{Actual} - \text{Consensus}$$

Surprise calculations enforce strict unit compatibility:
1. **Percentage-Point Differences**: Used for interest rates, inflation rates, and GDP growth (e.g. $+0.20\text{ pp}$).
2. **Basis-Point Differences**: Used for policy interest rates:
   $$\text{Basis Points} = (\text{Actual Rate} - \text{Consensus Rate}) \times 100 \quad (\text{e.g. } +25\text{ bps})$$
3. **Quantity Differences**: Used for employment counts (e.g. $+35,000\text{ jobs}$).
4. **Index-Point Differences**: Used for survey indices and price index levels.

### 7.1 Surprise Direction
- `ABOVE_CONSENSUS`: Actual strictly exceeds consensus ($> +0.01$).
- `BELOW_CONSENSUS`: Actual falls below consensus ($< -0.01$).
- `IN_LINE`: Actual equals consensus within tolerance.

**Market Disclaimer**: Positive statistical surprises are never labeled as intrinsically "bullish" or "good". Economic surprises measure statistical divergence from expectations; market asset reactions depend on the broader macroeconomic context.

---

## 8. User-Owned Event Alerts & Stage 49 Notification Center

Users can configure personalized alerts for any calendar event:
- **Alert Types**:
  - `BEFORE_SCHEDULED_RELEASE`: Timed reminder ($5\text{m}$, $15\text{m}$, $30\text{m}$, $1\text{h}$, $2\text{h}$ before release).
  - `WHEN_RELEASE_VERIFIED`: Dispatched immediately upon official publication verification.
  - `WHEN_SCHEDULE_CHANGES`: Dispatched if an official agency reschedules or postpones the release.
- **Idempotency & Durable Delivery**: Alerts evaluate idempotently, recording dispatched notification intents to prevent duplicate triggers upon worker restarts.
- **Quotas**: Each user account has a default quota of 100 active alerts.

---

## 9. REST API Reference

Namespace: `/api/v1/economics/calendar`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/economics/calendar/events` | Filtered list of economic releases and central bank events |
| `GET` | `/api/v1/economics/calendar/events/{event_id}` | Comprehensive detail view with observations & consensus |
| `GET` | `/api/v1/economics/calendar/events/{event_id}/observations` | Statistical observations published in the event |
| `GET` | `/api/v1/economics/calendar/events/{event_id}/forecasts` | Pre-release consensus forecast snapshots |
| `GET` | `/api/v1/economics/calendar/events/{event_id}/history` | Schedule revision and postponement history |
| `GET` | `/api/v1/economics/calendar/categories` | Supported release taxonomies |
| `GET` | `/api/v1/economics/calendar/geographies` | Supported geographic jurisdictions |
| `GET` | `/api/v1/economics/calendar/coverage` | Provider coverage and forecast availability matrix |
| `GET` | `/api/v1/economics/calendar/alerts` | List user-owned release alerts |
| `POST` | `/api/v1/economics/calendar/alerts` | Create new release alert |
| `PATCH` | `/api/v1/economics/calendar/alerts/{alert_id}` | Enable/pause or edit alert |
| `DELETE` | `/api/v1/economics/calendar/alerts/{alert_id}` | Cancel/delete alert |
| `GET` | `/api/v1/economics/calendar/alerts/history` | Outbox delivery intent log |
| `POST` | `/api/v1/economics/calendar/alerts/evaluate` | Trigger background alert evaluation |

---

## 10. Operational Source Matrix

| Source Institution | Jurisdiction | Release Families | Schedule Precision | Coverage Status |
|---|---|---|---|---|
| **U.S. Bureau of Labor Statistics (BLS)** | United States (`US`) | CPI, Employment Situation (NFP) | `EXACT_INSTANT` | Active & Verified |
| **U.S. Bureau of Economic Analysis (BEA)** | United States (`US`) | GDP (Advance, Revised) | `EXACT_INSTANT` | Active & Verified |
| **Federal Reserve (FOMC)** | United States (`US`) | Policy Decisions, Meetings | `EXACT_INSTANT` | Active & Verified |
| **Eurostat** | Euro Area (`EA`) | HICP, Flash GDP | `EXACT_INSTANT` | Active & Verified |
| **European Central Bank (ECB)** | Euro Area (`EA`) | Monetary Policy Decisions | `EXACT_INSTANT` | Active & Verified |
| **Office for National Statistics (ONS)** | United Kingdom (`GB`) | CPI, Labor Market | `EXACT_INSTANT` | Active & Verified |
| **Bank of England (BoE MPC)** | United Kingdom (`GB`) | Bank Rate Decisions | `EXACT_INSTANT` | Active & Verified |
| **Statistics Bureau of Japan** | Japan (`JP`) | National CPI | `EXACT_INSTANT` | Active & Verified |
| **Bank of Japan (BoJ)** | Japan (`JP`) | Policy Rate Decisions | `LOCAL_DATE_TIME` | Active & Verified |
| **MoSPI India** | India (`IN`) | CPI Combined, IIP | `EXACT_INSTANT` | Active & Verified |
| **Reserve Bank of India (RBI MPC)** | India (`IN`) | Policy Repo Rate | `LOCAL_DATE_TIME` | Active & Verified |
| **National Bureau of Statistics (NBS)** | China (`CN`) | CPI, Industrial Production | `LOCAL_DATE_TIME` | Active & Verified |
| **People's Bank of China (PBoC)** | China (`CN`) | Loan Prime Rate (LPR) | `EXACT_INSTANT` | Active & Verified |

---

## 11. Roadmap Boundaries & Prohibitions

1. **Stage 92 Responsibility**: The Global Economic Calendar owns verified release schedules, official publication monitoring, actual vs. forecast surprises, and user alerts.
2. **Stage 93 Deferred (Macro Comparisons)**: Stage 92 strictly does NOT implement cross-country macroeconomic matrices, GDP ranking engines, or growth convergence models.
3. **Zero Autonomous Trading**: The Economic Calendar does not execute broker trades, place orders, or generate automated position sizing based on release surprises.
4. **Zero LLM Calls**: Standard economic calendar browsing, filtering, and surprise calculations require zero LLM calls.
