# ATLAS — COMPANIES V1 ARCHITECTURE & SPECIFICATION

## Canonical Company Intelligence Profiles, Verified Corporate Identity, Issuer-to-Security Relationships, Sector and Industry Classification, Geographic Information, Qualified Financial Summaries, Corporate Research References and Professional Company Analysis Workspaces

---

## 1. Executive Overview

Stage 81 transforms `/companies` from an initial shell into a production-grade, canonical company intelligence workspace within the ATLAS financial operating system.

ATLAS enforces a strict financial ontology:
> **A Company is a canonical corporate entity, not a stock ticker, exchange listing, ETF, financial quote or trading instrument.**

A corporate legal entity may issue multiple financial instruments across equity, debt, and derivative asset classes; an equity instrument may have multiple exchange listings, dual-class voting rights, or international depositary receipts (ADRs/GDRs); a company's share price is a qualified market observation of a specific security listing at a venue, never an intrinsic universal property of the company itself.

Stage 81 establishes the canonical foundation for the company analysis domain, strictly bounded before detailed Financial Statements (Stage 82), Financial Ratios (Stage 83), Earnings (Stage 84), Ownership (Stage 85), Filings (Stage 86), Peers (Stage 87), and Supply Chains (Stage 88).

---

## 2. Core Architectural Principles

1. **Canonical Identity Separation**:
   - Company entities exist in `atlas.companies` and `atlas.entities`.
   - Financial instruments exist in `atlas.instruments`.
   - Market series and quotes exist in `atlas.market_data`.
   - Never use a ticker symbol as a company primary key.
   - Never merge distinct legal entities due to name similarities or corporate rebranding.

2. **Entity-to-Security Relationship Graph**:
   - All relationships between companies and financial instruments are queried through the verified Stage 23 Relationship Graph (`atlas.relationships`).
   - Supports explicit relationship types: `ISSUES_EQUITY`, `ISSUES_DEBT`, `ISSUES_PREFERRED`, `DEPOSITARY_RECEIPT_OF`, `SUBSIDIARY_OF`, `GUARANTOR_OF`.
   - Retains relationship validity timestamps, source attribution, and verification status.

3. **Qualified Market Context**:
   - Quotes belong to securities and venues, not companies.
   - Market summaries identify the qualified reference listing (e.g. primary equity listing) with explicit venue, currency, quote measure (`last`, `bid`, `ask`, `mid`, `clean_price`, `nav`), observation timestamp, and delay status (`realtime`, `delayed_15min`, `eod`).
   - Never invent synthetic market capitalization by multiplying arbitrary last prices by obsolete share counts or double-counting cross-listings.

4. **Qualified Financial Summary**:
   - Reuses canonical fundamental data from Stage 34 (`_STATEMENT_STORE`).
   - Presents qualified high-level summary metrics: Revenue, Net Income, Reported EPS, Total Assets, Total Equity, Cash & Equivalents.
   - Explicitly displays reporting currency, fiscal period (`FY2023`, `Q3-2024`), period end date, publication date, consolidation scope (`consolidated` vs `standalone`), and restatement status.
   - Zero synthetic TTM fabrication or unverified statement normalization (reserved for Stage 82).

5. **Cross-Module Navigation**:
   - "Open in Markets": Links to `/markets/equities` or `/markets/bonds` with the verified `instrument_entity_id`.
   - "Open in Charts": Links to `/charts?instrument={id}&symbol={symbol}`.
   - "Add to Watchlist": Invokes Stage 76 Watchlist membership API using the target `instrument_entity_id` (never the company entity ID).
   - "Set Selected Entity": Sets the active global entity context (`useSelectedEntity`) with the canonical company UUID.

6. **Strict Production Boundaries**:
   - Zero LLM calls for company facts, corporate descriptions, or financial summaries.
   - Zero provider fanout or unbudgeted external requests on page load.
   - Zero autonomous agent or trading order side-effects.

---

## 3. Data Model & Schemas

### 3.1 Company Identity (`CompanyIdentity`)
```typescript
interface CompanyIdentity {
  company_entity_id: string;        // Stable canonical UUID
  display_name: string;             // User-facing corporate name
  legal_name?: string | null;       // Registered legal name
  short_name?: string | null;       // Standard abbreviated name
  aliases: string[];                // Historical or trading aliases
  status: string;                   // 'active' | 'inactive' | 'dissolved' | 'merged'
  organization_type?: string | null;// 'corporation' | 'limited_company' | 'holding'
  website_url?: string | null;      // Verified official corporate website
}
```

### 3.2 Corporate Identifiers (`CompanyIdentifierItem`)
```typescript
interface CompanyIdentifierItem {
  scheme_key: string;               // 'LEI' | 'CIK' | 'CRN' | 'INTERNAL'
  scheme_name: string;              // 'Legal Entity Identifier' | 'SEC Central Index Key'
  value: string;                    // Sourced identifier string
  source: string;                   // Authority / provenance source
  verification_status: string;      // 'verified' | 'unverified'
}
```
*Note: ISIN and FIGI identify financial instruments and are explicitly excluded from company-level corporate legal identity.*

### 3.3 Classification (`CompanyClassification`)
```typescript
interface CompanyClassification {
  taxonomy: string;                 // 'GICS' | 'ICB' | 'SIC' | 'NAICS'
  taxonomy_version?: string | null; // e.g. '2023'
  sector_code?: string | null;
  sector_name?: string | null;
  industry_code?: string | null;
  industry_name?: string | null;
  source: string;
}
```

### 3.4 Corporate Geography (`CompanyGeography`)
```typescript
interface CompanyGeography {
  headquarters_country?: string | null;
  headquarters_city?: string | null;
  incorporation_jurisdiction?: string | null;
  country_code?: string | null;     // ISO 3166-1 alpha-2 / alpha-3
  address_text?: string | null;
}
```

### 3.5 Related Securities (`RelatedSecurityItem`)
```typescript
interface RelatedSecurityItem {
  instrument_entity_id: string;
  symbol?: string | null;
  display_name: string;
  asset_class: string;             // 'equity' | 'bond' | 'preferred' | 'fund'
  security_type: string;           // 'common_stock' | 'adr' | 'corporate_bond' | 'class_a'
  relationship_type: string;       // 'ISSUES_EQUITY' | 'ISSUES_DEBT' | 'DEPOSITARY_RECEIPT_OF'
  share_class_name?: string | null;// e.g. 'Class A', 'Class C'
  exchange_or_venue?: string | null;// 'NASDAQ', 'NYSE', 'LSE', 'OTC'
  currency: string;
  is_primary_listing: boolean;
  is_quote_available: boolean;
  latest_price?: string | null;
  percentage_change?: string | null;
  change_direction?: 'up' | 'down' | 'flat' | null;
  quote_measure?: string | null;   // 'Last' | 'Bid' | 'Ask' | 'Clean Price' | 'NAV'
  delay_status: string;            // 'realtime' | 'delayed_15min' | 'eod'
}
```

### 3.6 Financial Summary (`CompanyFinancialSummary`)
```typescript
interface CompanyFinancialSummary {
  status: 'AVAILABLE' | 'UNAVAILABLE' | 'NOT_ENTITLED';
  reporting_currency: string;
  fiscal_period?: string | null;
  period_end_date?: string | null;
  publication_date?: string | null;
  metrics: FinancialSummaryMetric[];
}

interface FinancialSummaryMetric {
  metric_key: string;             // 'revenue' | 'net_income' | 'eps' | 'total_assets' | 'total_equity' | 'cash_and_equivalents'
  metric_name: string;            // 'Total Revenue' | 'Net Income' | 'Reported Diluted EPS'
  value?: string | null;          // Formatted value (e.g. '$383.29B', '$6.13')
  raw_value?: number | null;
  currency: string;
  fiscal_period?: string | null;
  consolidation_scope: string;    // 'consolidated' | 'standalone'
  restatement_status: string;     // 'original' | 'restated'
}
```

---

## 4. API Endpoints

All endpoints are registered under `/api/v1/companies` in FastAPI (`atlas_api.routers.companies`):

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/companies` | Bounded directory search by name, ticker, LEI, CIK, or alias |
| `GET` | `/api/v1/companies/{company_id}` | Aggregate canonical company overview |
| `GET` | `/api/v1/companies/{company_id}/profile` | Corporate profile (identity, description, website) |
| `GET` | `/api/v1/companies/{company_id}/securities` | Paginated verified related financial instruments |
| `GET` | `/api/v1/companies/{company_id}/market-summary` | Qualified market context & reference listing snapshot |
| `GET` | `/api/v1/companies/{company_id}/financial-summary` | Qualified Stage 34 fundamental metrics |
| `GET` | `/api/v1/companies/{company_id}/news` | Paginated verified corporate news references |
| `GET` | `/api/v1/companies/{company_id}/documents` | Paginated verified corporate research and filings |

---

## 5. UI Architecture

The frontend is implemented in Next.js 16 (App Router) in `apps/web`:
- `/companies`: Company intelligence workspace with searchable directory empty state when unselected.
- `/companies/[companyId]`: Deep-linkable canonical route loading the company overview directly.

### Component Structure
- `CompaniesWorkspace`: Top subheader with directory search, return-to-directory button, and resizable layout split.
- `CompanyHeader`: Verified corporate identity badges, legal name, aliases, copyable entity UUID, classification tags, official website link, and terminal-wide entity selection.
- `CompanyOverviewTab`: Corporate description, identifiers card, industry classification card, geography card, and issuance market context.
- `CompanySecuritiesTab`: High-density financial instruments table with share classes, venues, quotes, status indicators, and cross-navigation actions ("Markets", "Charts", "+ Watchlist").
- `CompanyFinancialsTab`: Reporting currency, period end, filing date, and key metrics grid (Revenue, Net Income, EPS, Assets, Equity, Cash). Includes Stage 82 roadmap disclaimer.
- `CompanyNewsDocsTab`: Sourced corporate news articles and regulatory filing document references.
- `AddToWatchlistModal`: Interactive modal enabling users to select an owned watchlist and add the verified security via `addWatchlistItem` with zero ticker ambiguity.

---

## 6. Verification and Compliance

- **Backend Test Suite**: `apps/api/tests/test_companies_v1.py` passes 16 comprehensive unit and integration tests.
- **Linting**: Ruff passes 100% clean across `atlas.companies`, `routers/companies.py`, and test files.
- **Frontend Type Checking**: `tsc --noEmit` passes with 0 errors across the entire `apps/web` project.
- **Production Build**: Next.js production build (`next build`) compiles all routes cleanly, generating static `/companies` and dynamic `/companies/[companyId]`.
- **Side Effect Guarantees**: Company profile reads perform zero database mutations, zero provider subscriptions, zero trading orders, and zero LLM invocations.
