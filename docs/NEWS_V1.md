# ATLAS News Platform Foundation (Stage 99)

## Overview & Architecture

The **ATLAS Financial News Platform Foundation (Stage 99)** establishes the canonical, institutional-grade, source-verified news infrastructure for ATLAS. Operating at the primary top-level route `/news`, the platform provides institutional investors, analysts, traders, and researchers with source-qualified, timestamp-verified financial news directly linked to canonical market entities (Companies, Financial Instruments, and Geographies).

```
ATLAS Authenticated AppShell / Navigation (/news)
              |
              v
     NewsWorkspace (React/Next.js)
              |
   +----------+----------+
   |                     |
   v                     v
NewsFeedTable     NewsArticlePreview
(Density table)   (Publisher attribution,
                   safe external links,
                   canonical entity chips)
              |
              v
   HTTP REST API (/api/v1/news)
              |
   +----------+-----------------------------+
   |                                        |
   v                                        v
NewsService                              NewsIngestionService
- Keyset cursor pagination              - Authorized Provider Adapters
- In-memory feed cache & invalidation    - Canonical URL Normalization
- Category / Source / Entity filters     - SSRF & HTML Sanitization
- Bounded headline & excerpt search      - Duplicate Detection & SHA-256 ID
- Source freshness & coverage reports    - Syndication & Revision Tracking
- Provider entitlement enforcement       - Canonical Entity Linking (Ticker Disambiguation)
                                            |
                                            v
                                     NewsRepository
                             (PostgreSQL / Seed In-Memory Store)
```

---

## Canonical Domain Models

### 1. Canonical Article Identity (`NewsArticle`)
An immutable representation of a published piece of media from an authorized provider:
- `article_id`: Deterministic SHA-256 identifier based on provider and native source article ID (`sha256(f"{source_provider_id}:{provider_article_id}")[:24]`).
- `source_provider_id`: Identifying the distributor or ingestion pipeline (e.g., `openbb_news`, `financial_wire_direct`).
- `provider_article_id`: Native identifier within upstream provider.
- `publisher_id`: Canonical verified publisher (e.g., `reuters`, `bloomberg`, `wsj`, `sec_gov`).
- `headline`: Source-provided headline (sanitized, preserving verbatim wording).
- `permitted_excerpt`: Copyright-compliant excerpt or abstract. Full text is never stored or redistributed without explicit licensing.
- `canonical_url` & `original_url`: Normalized URL stripping tracking queries (`utm_*`, `fbclid`) while preserving destination semantics.
- `article_type`: Classified as `NEWS_REPORT`, `WIRE_REPORT`, `PRESS_RELEASE`, `OFFICIAL_ANNOUNCEMENT`, `MARKET_COMMENTARY`, `OPINION`, or `ANALYSIS`.
- `availability_status`: `AVAILABLE`, `METADATA_ONLY`, `SOURCE_RESTRICTED`, `WITHDRAWN`, `REMOVED`, or `SOURCE_UNAVAILABLE`.
- `licensing_status`: `LICENSED_DISTRIBUTION`, `PUBLIC_OPEN_ACCESS`, `RESTRICTED_EXCERPT_ONLY`, or `FAIR_USE_METADATA`.
- `is_syndicated`, `original_wire_publisher_id`, `duplicate_group_id`: Tracking syndication without conflating independent reports.

### 2. Timestamp Semantics
To guarantee timestamp integrity, five distinct temporal properties are tracked:
- `published_at`: Stated publication timestamp from the authoritative publisher (converted to UTC).
- `source_updated_at`: Optional timestamp when the publisher corrected or amended the article.
- `first_seen_at`: Timestamp when ATLAS first observed the record.
- `ingested_at`: Timestamp when the record was normalized and persisted into the canonical store.
- `last_fetched_at`: Timestamp when ATLAS last verified upstream record availability.
*Rule: Ingestion timestamps are never substituted for publication timestamps.*

### 3. Canonical Publisher Registry (`NewsPublisher`)
Publishers are distinct entities from providers. Pre-seeded publishers include:
- Financial News Agencies: Reuters, Bloomberg, Dow Jones / WSJ, Financial Times, CNBC, MarketWatch, Associated Press.
- Regional & National Press: The Economic Times, Mint, Nikkei Asia.
- Regulatory & Central Bank Authorities: U.S. SEC, U.S. Federal Reserve, Reserve Bank of India, European Central Bank.
- Corporate Wires: PR Newswire, Business Wire.

### 4. Financial News Sources (`NewsSource`)
Represents authorized source adapters with latency classes and entitlement requirements:
- `openbb_news` (`LICENSED_NEWS_API`, `NEAR_REAL_TIME`, authenticated).
- `financial_wire_direct` (`LICENSED_RSS_FEED`, `SCHEDULED_BATCH`, authenticated).
- `regulator_announcements` (`OFFICIAL_PUBLIC_FEED`, `SCHEDULED_BATCH`, public).
- `corporate_press_wire` (`APPROVED_STRUCTURED_DATASET`, `DELAYED_FEED`, public).

---

## Ingestion & Normalization

### 1. Canonical URL Normalization
- Converts protocol and host to lowercase.
- Strips default ports (`:80`, `:443`).
- Removes tracking query parameters: `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `fbclid`, `gclid`, `ref`, `source`, `campaign`, `trk`.
- Strips URL fragments (`#...`).
- Retains functional parameters (e.g., `id`, `articleId`, `storyId`).

### 2. Content Sanitization & SSRF Defense
- **HTML Sanitization**: Strips dangerous `<script>`, `<style>`, and `<iframe>` blocks before removing residual markup, preserving natural spacing between block elements.
- **SSRF Defense**: External URLs undergo strict scheme (`http`/`https` only) and IP resolution checks. Localhost, loopback (`127.0.0.0/8`, `::1`), private RFC 1918 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and AWS metadata endpoints are rejected.
- **Frontend Safe Navigation**: External links open with `target="_blank" rel="noopener noreferrer"` and scheme validation.

### 3. Deduplication & Revisions
- **Deterministic Identity**: Deduplication prioritizes Provider Native ID, followed by Publisher ID and Canonical URL.
- **Syndicated Wire Reports**: If a wire article (e.g. Reuters) is syndicated by another outlet, `is_syndicated=True` and `original_wire_publisher_id="reuters"` are recorded, preserving separate publisher provenance.
- **Revisions & Corrections**: Updates to existing articles increment `revision_number` and record a `NewsArticleRevision` with `change_type` (`CORRECTION`, `UPDATE`, `HEADLINE_CHANGE`, `WITHDRAWAL`).
- **Withdrawals**: Withdrawn stories are set to `availability_status=WITHDRAWN`, hiding excerpts and providing transparent editorial retraction indicators.

---

## Financial Entity Linking

ATLAS News resolves entity mentions to Stage 16 Universal Entities, Stage 17 Financial Instruments, and Stage 18 Companies:
- **Ticker Word Collision Filter**: Short English words that collide with tickers (e.g., `IT`, `ON`, `CAN`, `ARE`, `FOR`, `ALL`, `A`, `I`) are excluded from auto-linking unless explicitly cashtagged (e.g., `$IT`).
- **Exchange & Share-Class Disambiguation**:
  - `GOOGL` (Class A) vs `GOOG` (Class C).
  - ADRs (e.g., `INFY` ADR on NYSE) vs underlying listings (`INFY.NSE` on National Stock Exchange of India).
- **Resolution Methods**:
  - `VERIFIED_SOURCE_TAG`: Upstream structured ticker metadata.
  - `VERIFIED_IDENTIFIER_MATCH`: Exact match against Company/Instrument registries.
  - `CASHTAG_DETERMINISTIC`: Confirmed `$TICKER` pattern.
  - `AMBIGUOUS_UNRESOLVED`: Flagged when unambiguous exchange context is missing.
- **No Hallucinated Financial Impact**: Entity linking is strictly factual. News mentions never claim or imply market-impact predictions, expected returns, or investment recommendations.

---

## News API Contracts (`/api/v1/news`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/news/feed` | Keyset-paginated source-qualified chronological news feed. |
| `GET` | `/api/v1/news/articles/{id}` | Canonical article details with verified publisher metadata and revisions. |
| `GET` | `/api/v1/news/articles/{id}/revisions` | Audit trail of corrections and metadata updates. |
| `GET` | `/api/v1/news/sources` | Permitted news source registry with capabilities. |
| `GET` | `/api/v1/news/publishers` | Verified publisher metadata and verified domains. |
| `GET` | `/api/v1/news/categories` | Controlled financial category taxonomy. |
| `GET` | `/api/v1/news/search` | Bounded headline and excerpt search (max 200 chars). |
| `GET` | `/api/v1/news/entities/{entity_id}` | Articles mentioning a canonical Company or Instrument. |
| `GET` | `/api/v1/news/coverage` | Provider, country, and publisher coverage summary. |
| `GET` | `/api/v1/news/status` | Source freshness, latency class, and ingestion status. |
| `POST` | `/api/v1/news/ingest` | Privileged, idempotent ingestion endpoint for authorized workers. |

### Keyset Pagination Cursor
- Queries order strictly by `published_at DESC, article_id DESC`.
- Cursors encode `iso_published_at|article_id` in base64 URL-safe format.
- Queries evaluate strictly `published_at < cursor_ts OR (published_at == cursor_ts AND article_id < cursor_id)` to guarantee zero duplicate or skipped rows between pages.

---

## Frontend Workspace (`/news`)

The frontend delivers an institutional-grade, Bloomberg-inspired financial news terminal:
- **Category Tabs**: Instant switching across `All`, `Markets`, `Companies`, `Economics`, `Central Banks`, `Regulation`, and `Technology`.
- **Search & Filter Bar**:
  - Headline keyword search with instant clear.
  - Source filter (authorized providers).
  - Publisher filter (verified financial publishers).
  - Geographic region filter (`US`, `IN`, `EU`, `UK`, `JP`).
  - Clear Filters action button.
- **NewsFeedTable**:
  - High-density tabular layout.
  - Formatted UTC and relative publication timestamps.
  - Verified publisher tag with domain link.
  - Financial category badges with color coding.
  - Interactive canonical entity chips navigating to `/companies/{id}` and `/markets`.
  - Full keyboard accessibility: Up/Down arrow keys move article selection.
- **NewsArticlePreview**:
  - Split-pane article details.
  - Publisher verification badge and wire service attribution.
  - Copyright-compliant licensed excerpt.
  - Publication, first-seen, and ingestion timestamps.
  - Safe external navigation button (`Read Original Article`).
  - Canonical entity chips with ticker symbols and company IDs.
- **Freshness & Coverage**:
  - Real-time freshness badge and latency class indicator.
  - Coverage modal inspecting active providers, publishers, and licensing policies.
  - Distinct empty-result states vs source outage indicators.

---

## Verification & Testing

The Stage 99 implementation is verified across multiple layers:
1. **Backend Tests (`apps/api/tests/test_news_v1.py`)**:
   - 30 comprehensive pytest tests covering:
     - Canonical article identity generation & SHA-256 uniqueness.
     - SSRF defense (blocking 127.0.0.1, 10.0.0.1, 169.254.169.254, ftp/file schemes).
     - HTML sanitization (stripping `<script>`, `<iframe>`, block spacing).
     - Timestamp conversions and UTC guarantees.
     - Deduplication, syndication, revisions, and withdrawals.
     - Company & Instrument entity linking, ticker collision rejection (`IT`, `ON`).
     - Keyset cursor pagination (disjoint pages, no off-by-one errors).
     - Search, categories, publishers, sources, coverage, and status endpoints.
2. **Backend Regression Tests**:
   - 123 tests passing cleanly across `test_news_v1.py`, `test_economics_v1.py`, `test_screeners.py`, and `test_screener_nl_translation.py`.
3. **Python Lint & Style**:
   - `uv run ruff check` passed with 0 errors across all news packages.
4. **Frontend Unit Tests (`apps/web/src/lib/news/__tests__/news.test.ts`)**:
   - 32 tests passing covering formatting, category styles, external URL validation, and SSRF prevention.
5. **TypeScript Check**:
   - `npx tsc --noEmit` exited with code 0 across the entire Next.js workspace.
6. **Production Build**:
   - `pnpm build` succeeded with code 0, generating all 38 application routes including `/news`.

---

## Roadmap Boundaries

- **Completed Stage 99**: Foundational news platform, canonical data layer, authorized ingestion, entity linking, feeds, pagination, and `/news` workspace.
- **Deferred to Stages 100–103**: Advanced news intelligence, AI news summarization, sentiment scoring, market-impact prediction, causal analysis, event clustering, automated research briefs.
- **Deferred to Stage 104+**: General research workflows and research notebooks.
- **Strict Prohibition**: News ingestion must never trigger automated trading, order routing, portfolio mutation, or broker API calls.
