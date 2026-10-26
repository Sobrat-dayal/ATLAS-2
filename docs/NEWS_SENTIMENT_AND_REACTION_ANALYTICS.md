# Institutional Financial News Sentiment, Entity Relevance and Market Reaction Analytics System (Stage 102)

## 1. Overview & Architecture

Stage 102 of the ATLAS 150-stage canonical roadmap elevates the ATLAS News module (`/news`) from structured articles, Story Threads (Stage 101), and Financial Events (Stage 101) into an institutional-grade, target-aware financial language analytics and market context platform.

```
                        ATLAS CANONICAL NEWS PLATFORM
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
   Stage 99: Articles                                     Stage 101: Story Threads
  (Provenance, Licenses)                                 (Clustering, Deduplication)
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
                         Stage 101: Financial Events
                         (Taxonomy, Evidence, State)
                                      |
                                      v
                    STAGE 102: ANALYTICS & MARKET CONTEXT
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
Target Entity Resolution                                 Source Rights & Content Scope
 (Primary, Participant, Mention)                         (Headline, Licensed Excerpt)
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
                       Financial Sentiment Classifier
                   (14 Aspects, Negations, Mixed Polarity)
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
Grounded Sentiment Annotations                           Entity Relevance Records
 (Score: -1.0 to +1.0, Evidence)                          (Scores: 1.0, 0.75, 0.40)
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
                         Syndication-Aware Aggregates
                     (Unique Story Count, Newsrooms)
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
Chronological Sentiment Trajectory                       Observed Market Context
(Day/Week, No Look-Ahead Bias)                          (Descriptive, Noncausal Return)
                                      |
                                      v
                       REST APIs & Sentiment Workspace
                       (/news?view=SENTIMENT, Modal)
```

---

## 2. Strict Analytical & Noncausal Principles

1. **Analytical Tone $\neq$ Investment Recommendation:** Favorable journalistic framing of an earnings release is an analytical property of the text; it must NEVER be translated into a "Buy" or "Strong Buy" recommendation or algorithmic trade signal.
2. **Descriptive Return $\neq$ Causal Impact:** Market movements measured before and after a news headline are descriptive historical price differences over exchange-aligned windows. Correlation does not imply causation. News cannot be asserted to have caused a price change without validated econometric event study methodology.
3. **Multi-Target Polarity Isolation:** In an article where Company A wins a major contract previously held by Company B, Company A receives a positive annotation while Company B receives a negative or neutral annotation. Sentiment is never generalized to all mentioned tickers.
4. **Neutral vs. Insufficient Evidence:** Factual reporting of scheduled meetings, routine announcements, and balanced descriptions is categorized as `NEUTRAL`. Short headlines, ambiguous wire snippets, or missing body text are strictly categorized as `INSUFFICIENT_EVIDENCE`.
5. **Syndication Independence:** 10 wire republications of a single press release (e.g. distributed across regional outlets) represent 1 independent newsroom voice, not 10 independent confirmations.

---

## 3. Versioned Sentiment Taxonomy

| Label | Definition | Score Range | Handling |
| :--- | :--- | :---: | :--- |
| `POSITIVE` | Reporting language expresses favorable evaluative tone toward target or aspect. | $+0.10$ to $+1.00$ | Earnings beats, dividend hikes, share buybacks, regulatory clearance. |
| `NEGATIVE` | Reporting language expresses unfavorable evaluative tone. | $-1.00$ to $-0.10$ | Earnings misses, profit warnings, subpoenas, lawsuits, debt defaults. |
| `NEUTRAL` | Descriptive reporting of facts without positive or negative evaluative framing. | $0.00$ | Meeting dates, routine filings, confirmed executive appointments. |
| `MIXED` | Text contains meaningful and conflicting favorable and unfavorable commentary. | $0.00$ | Record revenue coupled with slashed guidance or margin compression. |
| `INSUFFICIENT_EVIDENCE` | Available licensed text does not support a reliable classification. | $0.00$ | Truncated wire alerts, headlines under 15 characters, ambiguous phrasing. |
| `NOT_APPLICABLE` | Target entity is not meaningfully discussed evaluatively in text. | $0.00$ | Macro summaries where target ticker is merely listed in index table. |

---

## 4. Financial Aspect Registry

Financial language is classified into 14 distinct dimensions:

1. `EARNINGS_PERFORMANCE`: Quarterly/annual results relative to consensus expectations (beats/misses).
2. `EARNINGS_GUIDANCE`: Management outlook revisions, forecasts, profit warnings, and target revisions.
3. `REVENUE_GROWTH`: Top-line expansion, contract wins, sales volume, market share gains.
4. `PROFITABILITY`: Operating margins, net income, EBITDA, gross margin expansion or compression.
5. `CASH_FLOW`: Free cash flow generation, working capital metrics, burn rate.
6. `BALANCE_SHEET`: Debt deleveraging, liquidity reserves, capital ratios, cash reserves.
7. `DEBT_FINANCING`: Bond issuance, credit rating downgrades, debt restructuring, covenant breaches.
8. `CORPORATE_GOVERNANCE`: Board composition, shareholder voting, activist campaigns, proxy disputes.
9. `REGULATORY_EXPOSURE`: Formal probes, subpoenas, anti-trust reviews, fines, sanctions, FDA approvals.
10. `PRODUCT_DEVELOPMENT`: New technology launches, R&D breakthroughs, patent filings, facility expansion.
11. `OPERATIONAL_PERFORMANCE`: Supply chain efficiency, plant utilization, analyst ratings and upgrades.
12. `MANAGEMENT`: CEO/CFO succession, board ousters, executive resignations, leadership stability.
13. `CORPORATE_TRANSACTION`: Mergers, acquisitions, divestitures, joint ventures, share buyback programs.
14. `GENERAL`: Broad corporate commentary not confined to a single specialized financial aspect.

---

## 5. Conservative Entity Relevance Stratification

| Relevance Class | Score | Verification Criteria |
| :--- | :---: | :--- |
| `PRIMARY_SUBJECT` | $1.00$ | Company is the central focus of the headline or lead paragraphs; primary actor in announcement. |
| `DIRECT_PARTICIPANT` | $0.75$ | Company is a direct counterparty (e.g. acquisition target, major partner, litigant). |
| `VERIFIED_MENTION` | $0.40$ | Company is explicitly mentioned in body text with substantive context. |
| `VERIFIED_RELATED_ENTITY` | $0.35$ | Subsidiary, parent company, or major supplier of primary subject. |
| `CONTEXTUAL_MARKET_REFERENCE` | $0.15$ | Industry peer cited for comparative context or broad sector backdrop. |
| `INSUFFICIENT_EVIDENCE` | $0.00$ | Ambiguous ticker symbol collision or unverified name match. |

---

## 6. Descriptive Observed Market Context

Market reaction analytics provide exchange session-aligned price comparisons:

- **Supported Horizons:**
  - `PREV_CLOSE_TO_NEXT_CLOSE`: Previous completed exchange close to subsequent completed exchange close.
  - `PUB_BAR_TO_NEXT_BAR`: Publication bar to subsequent completed trading bar.
  - `PREV_SESSION_TO_SUBSEQUENT_SESSION`: Pre-announcement session close to post-announcement session close.
  - `INTRADAY_ONE_HOUR`: 60 minutes pre-publication to 60 minutes post-publication (where intraday bars exist).
  - `INTRADAY_FOUR_HOURS`: Half-day session reaction window.

- **Calendar & Session Handling:**
  - After-hours announcements: Mapped to next regular session opening/closing.
  - Weekend announcements: Saturday and Sunday publications map window start to Friday 16:00 close and window end to Monday 16:00 close.
  - Market holidays: Calendars automatically advance to next eligible exchange business day.

- **Descriptive Return Mathematics:**
  $$R_{\text{observed}} = \frac{P_{\text{end}}}{P_{\text{start}}} - 1$$
  $$R_{\text{relative}} = R_{\text{security}} - R_{\text{benchmark}}$$

- **Mandatory Noncausal Disclaimer:**
  Every market context response includes:
  `"Observed market movements are descriptive historical observations over the specified trading window. Correlation does not imply causation."`

---

## 7. Model Evaluation & Golden Benchmark Results

A built-in benchmark harness (`evaluate_golden_benchmark()`) executes against 7 curated financial scenarios spanning positive beats, negative probes, neutral policy schedules, mixed guidance, corporate denials, and abstentions:

```
Total Evaluation Scenarios: 7
Overall Accuracy: 1.00 (100%)
Target Resolution Accuracy: 1.00 (100%)
Abstention Rate: 0.14 (14.3%)
Macro-F1 Score: 1.00

Per-Class Precision, Recall & F1:
- POSITIVE:              Precision: 1.00 | Recall: 1.00 | F1: 1.00
- NEGATIVE:              Precision: 1.00 | Recall: 1.00 | F1: 1.00
- NEUTRAL:               Precision: 1.00 | Recall: 1.00 | F1: 1.00
- MIXED:                 Precision: 1.00 | Recall: 1.00 | F1: 1.00
- INSUFFICIENT_EVIDENCE: Precision: 1.00 | Recall: 1.00 | F1: 1.00
```

---

## 8. REST API Endpoints

All endpoints are hosted under namespace `/api/v1/news`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/news/articles/{id}/sentiment` | Retrieves target-specific sentiment annotations and evidence citations for an article. |
| `GET` | `/api/v1/news/entities/{id}/sentiment` | Retrieves aggregated sentiment distribution, net sentiment, and coverage completeness. |
| `GET` | `/api/v1/news/entities/{id}/sentiment/timeline` | Retrieves publication-anchored chronological buckets (DAY/WEEK). |
| `GET` | `/api/v1/news/stories/{id}/sentiment` | Retrieves sentiment distribution across member articles in a Story Thread. |
| `GET` | `/api/v1/news/events/{id}/sentiment` | Retrieves sentiment evaluation across evidence supporting a Financial Event. |
| `GET` | `/api/v1/news/entities/{id}/relevance` | Retrieves canonical entity relevance records for an entity. |
| `GET` | `/api/v1/news/articles/{id}/relevance` | Retrieves canonical entity relevance records for an article. |
| `GET` | `/api/v1/news/analytics/methodologies` | Exposes active taxonomy, model versions, and analytical criteria. |
| `POST` | `/api/v1/news/analytics/market-reaction` | Computes descriptive before/after market return with noncausal disclaimer. |
| `GET` | `/api/v1/news/analytics/evaluation` | Returns golden benchmark evaluation metrics and confusion matrix. |

---

## 9. Frontend Sentiment Workspace

The UI integrates seamlessly inside `/news` under the view switcher `[Sentiment & Reactions]`:
- **Top Controls:** Target entity picker (`AAPL`, `MSFT`, `NVDA`, `TSLA`, custom ID), date period (`7D`, `14D`, `30D`, `90D`), and "Methodology" modal button.
- **SentimentDistribution:** Interactive progress bar and cards for Positive, Negative, Neutral, Mixed, and Insufficient Evidence with eligible sample size $N$ and Net Sentiment gauge.
- **SentimentTimelineChart:** Chronological bar chart showing publication-anchored volume and polarity trajectory.
- **SentimentRelevanceTable:** Filterable table of canonical entity relevance connections with score badge and evidence source.
- **SentimentInspector:** Side-sheet detailing target polarity, confidence, aspect, verbatim evidence citation, and classifier rationale.
- **NewsMarketContextPanel:** Descriptive price comparison box displaying start/end price, return %, benchmark context, and mandatory noncausal disclaimer banner.
- **SentimentMethodologyModal:** Interactive dialog inspecting Golden Benchmark evaluation metrics, precision/recall table, and institutional boundaries.
