# ATLAS — Stage 100: Institutional Financial News Discovery, Search and Timelines

## 1. Executive Summary & Canonical Roadmap Verification

Stage 100 of the 150-stage canonical ATLAS development roadmap builds the institutional-grade **Financial News Discovery, Search, and Chronological Timeline System**.

```
ATLAS ROADMAP NEWS SEQUENCE:
Stage 99:  Financial News Platform Foundation (Canonical Articles, Deduplication, Provenance)
Stage 100: Advanced Financial News Discovery, Search and Timelines (Discovery Modes, Facets, Chronology)
Stage 101: Subsequent News Module Development (Pending Canonical Sequencing)
Stage 102: Subsequent News Module Development
Stage 103: Subsequent News Module Development
Stage 104: Research Module Development Commences
```

### Roadmap Boundary Verification
- The frozen roadmap confirms Stages 99–103 comprise the News development sequence.
- Primary route remains `/news` across the AppShell; all 20 canonical top-level routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, etc.) remain intact and unaltered.
- Stage 100 is strictly a read, discovery, search, and chronological timeline layer built on top of Stage 99's authoritative data models and ingestion engine.
- AI-generated summarization, LLM article synthesis, sentiment classification, predictive market impact scores, automated news-driven trading, and autonomous monitoring agents remain strictly deferred to later stages.

---

## 2. Discovery Architecture & Canonical Data Flow

The Discovery layer is a high-performance, strictly source-qualified exploration engine operating over the Stage 99 canonical storage layer.

```
+-----------------------------------------------------------------------------------+
|                        ATLAS AUTHENTICATED APPSHELL                               |
|                                     |                                             |
|                                     v                                             |
|                             /news WORKSPACE                                       |
+-----------------------------------------------------------------------------------+
                                      |
       +------------------------------+------------------------------+
       |                              |                              |
       v                              v                              v
[Discovery Modes]            [Advanced Search]             [Discovery Filters]
- All News                   - Quoted phrases              - Topics (14 canonical)
- Markets (Equities, FX, etc)- Multi-token AND/OR          - Sectors (GICS/ICB)
- Companies (Canonical ID)   - Term relevance scoring      - Publishers & Sources
- Securities (Instrument ID) - Highlight generation        - Geographies & Languages
- Topics & Taxonomy          - Prefix suggestions          - Date presets & Timezones
- Industries & Sectors                                     - Faceted counts
- Watchlist-scoped news
       |                              |                              |
       +------------------------------+------------------------------+
                                      |
                                      v
                       POST /api/v1/news/discover
                       POST /api/v1/news/facets
                       POST /api/v1/news/timeline
                                      |
                                      v
                    [NewsDiscoveryQuery Compilation]
                                      |
                                      v
                   [Source & Entitlement Verification]
                                      |
                                      v
               [Stage 99 Authoritative NewsRepository]
                - Canonical NewsArticle Entities
                - Linked Financial Entities (Stage 17/18)
                - Deduplication Engine & Audit Revisions
                - Deterministic Topic/Industry Classifiers
                                      |
       +------------------------------+------------------------------+
       |                                                             |
       v                                                             v
[News Feed Table View]                                  [Chronological Timeline View]
- Keyset cursor pagination                               - Interval bucketing (Day/Week/Month)
- High-density tabular layout                             - Timezone localization (IANA)
- Duplicate & syndication badges                         - Article density aggregation
- Direct & related entity chips                          - Published vs First-Seen separation
       |                                                             |
       +------------------------------+------------------------------+
                                      |
                                      v
                        [Article Detail Inspector]
                        - Publisher & Source Provenance
                        - Licensed Excerpt Display Only
                        - Revision & Withdrawal Status
                        - Entity & Security Deep Links
```

---

## 3. Discovery Query Domain & Schemas

### NewsDiscoveryQuery
```python
class NewsDiscoveryQuery(BaseModel):
    mode: NewsDiscoveryMode = NewsDiscoveryMode.ALL
    entity_ids: list[str] = []
    tickers: list[str] = []
    topic_ids: list[str] = []
    industries: list[str] = []
    source_ids: list[str] = []
    publisher_ids: list[str] = []
    categories: list[NewsCategory] = []
    countries: list[str] = []
    languages: list[str] = []
    article_types: list[NewsArticleType] = []
    query: str | None = None
    date_preset: NewsDatePreset = NewsDatePreset.ALL_TIME
    start_date: datetime | None = None
    end_date: datetime | None = None
    sort_order: NewsSortOrder = NewsSortOrder.PUBLISHED_DESC
    limit: int = 30
    cursor: str | None = None
```

### Discovery Modes
1. `ALL`: Unrestricted discovery across all authorized financial news.
2. `MARKETS`: Filtered to asset-class market categories (`EQUITIES`, `FIXED_INCOME`, `FOREIGN_EXCHANGE`, `COMMODITIES`).
3. `COMPANIES`: Company-centric news requiring canonical Company ID (Stage 18).
4. `SECURITIES`: Instrument-centric news requiring canonical Instrument ID (Stage 17).
5. `TOPICS`: Macroeconomic and corporate development news matching canonical topics.
6. `INDUSTRIES`: Sector/industry news matching canonical GICS/ICB sectors.
7. `WATCHLIST`: Aggregated news matching securities in the user's authenticated watchlists.

---

## 4. Advanced Search & Explainable Relevance

### Safe Search Syntax
- **Exact Phrases**: Quoted terms (e.g., `"Federal Reserve"`, `"High-NA EUV"`) require exact contiguous character-sequence matching across the headline or permitted excerpt.
- **Multi-Token Terms**: Unquoted terms are parsed into normalized tokens. Articles containing query tokens match and are ranked according to token overlap.
- **Search Boundaries**: Query lengths are capped at 500 characters, tokens at 10, and phrase groups at 5 to prevent regex exhaustion or computational resource abuse.
- **Sanitization**: All search strings are stripped of HTML tags, control characters, and SQL injection syntax before query compilation.

### Deterministic Relevance Scoring Formula
Search relevance is computed explainably based on term density and structural placement:
$$\text{Score} = S_{\text{raw}} + S_{\text{phrases}} + S_{\text{tokens}} + S_{\text{overlap}} + S_{\text{topic}}$$

- Raw exact query in headline: **+100 points**
- Raw exact query in excerpt: **+40 points**
- Quoted exact phrase in headline: **+50 points**
- Quoted exact phrase in excerpt: **+20 points**
- Query token in headline: **+15 points per token**
- Query token in excerpt: **+5 points per token**
- All-token overlap bonus: **+30 points** (rewarding full coverage)
- Topic alignment: **+10 points**

**Critical Standard:** Relevance reflects text-matching density and alignment; it is never presented as market impact or price-movement probability.

---

## 5. Canonical Topic Taxonomy & Industry Classification

### 14 Canonical News Topics (`NewsTopic`)
1. `EARNINGS_RELEASES`: Quarterly and annual earnings, revenue milestones, EPS performance.
2. `MERGERS_ACQUISITIONS`: M&A transactions, tender offers, buyouts, divestitures.
3. `DIVIDENDS_DISTRIBUTIONS`: Cash dividends, special payouts, distribution adjustments.
4. `SHARE_BUYBACKS`: Share repurchase authorizations and programmatic buyback executions.
5. `CAPITAL_RAISING`: Secondary equity offerings, bond issuances, convertible notes.
6. `INTEREST_RATES_MONETARY_POLICY`: Central bank policy decisions, policy rate targets, FOMC/ECB/RBI announcements.
7. `INFLATION_PRICES`: CPI, PPI, PCE price indices, wage growth, core inflation metrics.
8. `EMPLOYMENT_LABOR`: Non-farm payrolls, unemployment claims, labor force participation.
9. `FOREIGN_EXCHANGE_CURRENCIES`: Major and cross currency pairs, FX interventions, dollar index.
10. `COMMODITIES_ENERGY`: Crude oil, natural gas, precious metals, strategic mineral supply.
11. `FINANCIAL_REGULATION_COMPLIANCE`: SEC rules, antitrust enforcement, compliance mandates.
12. `CORPORATE_GOVERNANCE_BOARD`: Board elections, activist campaigns, executive succession, demergers.
13. `TECHNOLOGY_AI_INNOVATION`: Semiconductor lithography, AI infrastructure, enterprise cloud platforms.
14. `SUPPLY_CHAIN_LOGISTICS`: Freight shipping, industrial manufacturing capacity, component supply.

### Deterministic Topic Classifier
Articles are classified during ingestion using deterministic regex and category mappings:
```python
def classify_topics_for_article(
    headline: str,
    excerpt: str,
    categories: list[NewsCategory | str],
) -> list[str]:
    ...
```

### Industry Sector Resolution
Canonical GICS/ICB classification: `INFORMATION_TECHNOLOGY`, `FINANCIALS`, `HEALTHCARE`, `CONSUMER_DISCRETIONARY`, `CONSUMER_STAPLES`, `INDUSTRIALS`, `ENERGY`, `MATERIALS`, `UTILITIES`, `REAL_ESTATE`, `COMMUNICATION_SERVICES`.
- Direct industry tags are preferred.
- Company-derived industry tags are explicitly labeled as derived.

---

## 6. Faceted Search & Count Integrity

Faceted search computes discrete, non-leaking aggregate counts:
- `sources`: Articles per source provider.
- `publishers`: Articles per verified publisher.
- `categories`: Articles per canonical news category.
- `topics`: Articles per active canonical topic.
- `countries`: Articles per geographic region.
- `article_types`: Articles per content classification.

**Integrity Guarantees:**
- Counts strictly reflect active search text and filters.
- Restricted articles do not leak counts to unauthorized sessions.
- Deduplication semantics count distinct canonical stories, not raw provider fetches.

---

## 7. Chronological Timelines & Timezones

### Timeline Architecture
- **Bucketing Intervals**: `DAY`, `WEEK`, and `MONTH`.
- **Timezone Conversion**: Uses standard Python `zoneinfo.ZoneInfo` and client-selected IANA timezones (UTC, America/New_York, Europe/London, Asia/Kolkata, Asia/Tokyo).
- **Date Precision**: Date-only articles (00:00:00Z) are preserved without artificial second-level precision.
- **Empty Periods**: Gaps in time are left honestly empty; no synthetic event nodes or causal arrows are generated.
- **Timestamp Distinction**: Original publisher `published_at` governs timeline placement; `first_seen_at` and `ingested_at` remain transparently inspectable.

---

## 8. REST Endpoints Specification

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/news/discover` | Multi-dimensional news discovery, search, and keyset pagination |
| `POST` | `/api/v1/news/facets` | Entitlement-aware facet aggregations under active filters |
| `POST` | `/api/v1/news/timeline` | Chronological timeline aggregation by day, week, or month |
| `GET` | `/api/v1/news/topics` | List canonical topic taxonomy (14 topics) |
| `GET` | `/api/v1/news/topics/{topic_id}` | Topic detail and keywords |
| `GET` | `/api/v1/news/suggestions` | Fast metadata-backed prefix autocomplete for search input |

All endpoints require standard ATLAS authentication (`get_current_user`).

---

## 9. Security, Licensing & Side-Effect Guarantees

1. **Licensing Protection**: Only licensed headlines and permitted excerpts are returned or searched; unauthorized full-text scraping or paywall circumvention is strictly prohibited.
2. **XSS Prevention**: Headlines, excerpts, and highlights are treated as plain text and rendered safely without `dangerouslySetInnerHTML`.
3. **SSRF Mitigation**: External publisher links are validated against `is_safe_external_url` to prevent loopback, RFC 1918, link-local, or AWS metadata IP requests.
4. **SQL & DSL Protection**: All search terms are parameterized and query complexity is bounded.
5. **Zero Side-Effects**: Read-only news exploration produces:
   - Security writes: 0
   - Company writes: 0
   - Portfolio mutations: 0
   - Watchlist mutations: 0
   - Trading orders: 0
   - AI summarization calls: 0

---

## 10. Automated Verification & Quality Gates

### Backend Verification
- `apps/api/tests/test_news_discovery_v1.py` (28 test cases): Topic catalog, deterministic classification, industry resolution, mode filtering, exact quoted phrase search, token matching, relevance ranking, keyset pagination, date presets, facets aggregation, timezone-aware timeline bucketing, search suggestions, watchlist scoping, and API endpoints.
- `apps/api/tests/test_news_v1.py` (30 test cases): Stage 99 regressions passed 100%.
- Total Backend News Tests: **58 passed in 4.42s**.
- Full Backend Regression Suite (Screener NL + Economic Calendar): **53 passed in 4.06s**.
- Ruff Linter: **0 errors across all Python code**.

### Frontend Verification
- `apps/web/src/lib/news/__tests__/discovery.test.ts` & `news.test.ts`: **40 tests passed cleanly**.
- TypeScript Typecheck (`npx tsc --noEmit`): **0 errors**.
- Next.js Production Build (`pnpm build`): **Compiled successfully in 2.7s; `/news` prerendered cleanly**.
