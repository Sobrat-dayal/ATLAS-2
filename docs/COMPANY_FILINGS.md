# COMPANY FILINGS INTELLIGENCE (STAGE 86)

## Master Architecture & Specification

Institutional-grade Company Filings Intelligence system inside ATLAS, integrating canonical regulatory filing ingestion, official SEC EDGAR integration, annual (10-K) and quarterly (10-Q) reports, material-event disclosures (8-K), proxy statements (DEF 14A), ownership/insider references (13F, Form 4), structured XBRL financial data extraction, full-text document search, revision and amendment tracking, side-by-side filing comparison, and professional corporate research workspaces.

---

## 1. Executive Summary & Master Directive

ATLAS Stage 86 delivers a comprehensive, regulator-grounded, and secure Company Filings Intelligence system embedded natively within the existing `/companies` module.

The system allows quantitative researchers, equity analysts, forensic accountants, and compliance officers to:
- **Discover and catalog genuine regulatory filings** from authorized sources including the U.S. Securities and Exchange Commission (SEC EDGAR);
- **Inspect immutable original documents** with content hashes (SHA-256) and verified accession numbers;
- **Safely view regulatory documents** via multi-stage HTML sanitization that eliminates script execution, iframes, and active content;
- **Audit structured XBRL financial facts** with standard US-GAAP taxonomy concepts, instant vs duration contexts, exact units, dimensional qualification, and precision;
- **Search disclosures via full-text indexing** with genuine textual excerpts, section headings, character offsets, and relevance scoring;
- **Compare filing revisions and amendments** with unified textual diffing and structured financial fact variance calculations;
- **Trace end-to-end provenance** across Financial Statements (Stage 82), Financial Ratios (Stage 83), Earnings (Stage 84), and Ownership (Stage 85).

### Strict Non-Negotiable Boundaries:
- **Stage 86 Owns Filings Intelligence**.
- **Stage 87 Owns Peers** (comparable company analysis, sector valuation multiples).
- **Stage 88 Owns Supply Chains** (supplier-customer relationship networks).
- **Stages 104–109 Own Research RAG**.
- **Zero Synthetic Disclosures**: Never invent accession numbers, filing dates, financial figures, or SEC URLs.
- **Zero Real-Time Conflation**: Distinguish between fiscal reporting period end dates, filing dates, acceptance datetimes, and ingestion timestamps.
- **Zero LLM Calls**: 0 LLM calls for filings metadata, parsing, or extraction; 0 trading orders; 0 portfolio mutations.

---

## 2. Canonical Filing Domain Architecture

ATLAS models regulatory filings as immutable, source-qualified legal disclosures submitted under specific regulatory jurisdictions:

```
                            +----------------------+
                            |   Issuing Company    | (Stage 18 Entity)
                            +----------+-----------+
                                       |
                            +----------v-----------+
                            | Regulatory Issuer    | (CIK / LEI / Ticker)
                            +----------+-----------+
                                       |
                       +---------------+---------------+
                       |                               |
                       v                               v
            +--------------------+          +--------------------+
            |  RegulatoryFiling  |          |  FilingDocument    | (Stage 20 Document)
            | (Accession Number) |          | (Primary/Exhibit)  |
            +----------+---------+          +----------+---------+
                       |                               |
                       +---------------+---------------+
                                       |
                                       v
                           +-----------------------+
                           |   Structured Content  |
                           +-----------+-----------+
                                       |
             +-------------------------+-------------------------+
             |                         |                         |
             v                         v                         v
   +-------------------+     +-------------------+     +-------------------+
   | Extracted Sections|     |    XBRL Facts     |     |   Search Index    |
   | (Items / Headings)|     | (Taxonomy Concepts|     | (Full-Text Vectors|
   +-------------------+     |  Units & Decimals)|     |  Snippet Context) |
                             +-------------------+     +-------------------+
```

### Core Entities:
1. **`RegulatoryFiling`**: Official filing record identified by its canonical UUID, issuer entity ID, regulator (`SEC_EDGAR`), official accession number (e.g. `0000320193-24-000106`), official form code (`10-K`), reporting period (`2024-09-28`), filing date (`2024-11-01`), and acceptance timestamp (`2024-11-01T16:04:32Z`).
2. **`FilingDocument`**: Canonical document attachment with filename, MIME type, byte size, cryptographic content digest (SHA-256), primary document flag, and official archive URL.
3. **`XBRLFact`**: Machine-readable financial disclosure fact with taxonomy concept (`us-gaap:Revenues`), accounting label, context period type (`DURATION` or `INSTANT`), period end date, unit (`USD`, `SHARES`), exact numeric value, precision decimals, and reporting dimensions.
4. **`FilingSection`**: Extracted structural section (e.g. `Item 1. Business`, `Item 7. MD&A`, `Item 8. Financial Statements`) with character offset and anchor reference.

---

## 3. Regulatory Source Architecture & SEC EDGAR Integration

### Supported Source Regulators:
| Regulator Code | Jurisdiction | Operational Status | Access Method | Fair Access Policy |
| :--- | :--- | :--- | :--- | :--- |
| **`SEC_EDGAR`** | United States | **ACTIVE / PRODUCTION** | Official Submissions API & Archives | User-Agent required; &le; 10 req/s shared rate limit |
| **`SEBI`** | India | Architecture Prepared | Authorized Disclosures Gateway | Explicit licensing required |
| **`NSE` / `BSE`** | India | Architecture Prepared | Exchange Corporate Disclosures | Terms of service compliance |
| **`MCA`** | India | Architecture Prepared | Ministry of Corporate Affairs | Authorized gateway credentials |
| **`COMPANIES_HOUSE`** | United Kingdom | Architecture Prepared | REST API | Registered developer API key |

### SEC EDGAR Access Policy & Compliance:
1. **User-Agent Identification**: In accordance with SEC EDGAR Fair Access requirements, all outbound requests identify the application, organization, and technical contact email:
   `AtlasPlatform/1.0 (Contact: compliance@atlasfinancial.io)`
2. **Shared Rate Limiting**: Centralized token bucket or Redis-backed rate limiter strictly enforces a ceiling of 10 requests per second across all ingestion workers and API tasks.
3. **HTTP 429 Handling**: Exponential backoff with jitter and retry-after header compliance.
4. **Direct Official URLs**: Primary document links resolve directly to immutable SEC web archives (`https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodashes}/{filename}`).

---

## 4. Supported Filing Categories & Taxonomy

| Category Code | Display Name | Official Form Types | Period Applicability | Amendment Forms |
| :--- | :--- | :--- | :--- | :--- |
| **`ANNUAL_REPORTS`** | Annual Reports | `10-K`, `20-F`, `40-F` | Fiscal Year End | `10-K/A`, `20-F/A` |
| **`QUARTERLY_REPORTS`**| Quarterly Reports | `10-Q` | Fiscal Quarter End | `10-Q/A` |
| **`CURRENT_REPORTS`** | Current Events | `8-K`, `6-K` | Event Occurred Date | `8-K/A`, `6-K/A` |
| **`PROXY_STATEMENTS`** | Proxy Statements | `DEF 14A`, `DEFA14A` | Annual Meeting Date | `DEF 14A/A` |
| **`OWNERSHIP_INSIDER`**| Ownership Disclosures | `13F-HR`, `SC 13D`, `SC 13G`, `3`, `4`, `5` | Position / Event Date | `/A` variants |
| **`REGISTRATION`** | Registration Statements| `S-1`, `S-3`, `F-1` | Offering Date | `S-1/A`, `S-3/A` |

---

## 5. Security & Safe Document Processing

Regulatory documents originate from external sources and may contain malicious HTML, embedded JavaScript, cross-site scripting vectors, or malformed XML.

### Ingestion Threat Model & Defenses:
1. **HTML Sanitization**:
   - Explicit tag allowlist: `div`, `p`, `span`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `h1`–`h6`, `b`, `i`, `strong`, `em`, `ul`, `ol`, `li`, `br`, `hr`.
   - Strict removal of `<script>`, `<iframe>`, `<object>`, `<embed>`, `<link>`, `<form>`, and `<applet>`.
   - Complete stripping of all inline event handlers (`onload`, `onerror`, `onclick`, `onmouseover`).
   - Disallowance of `javascript:`, `vbscript:`, and `data:` URI schemes.
2. **XML/XBRL XXE Defense**:
   - Defuses XML External Entity (XXE) attacks by resolving DTDs and entities safely without external network resolution.
   - Disallows recursive entity expansion (Billion Laughs / quadratic blowup).
3. **Decompression & Resource Limits**:
   - Enforces a maximum document byte size (50 MB) and parser timeout (30 seconds).
   - Prevents zip-bomb expansion during archive ingestion.
4. **Cryptographic Content Verification**:
   - Computes SHA-256 digest on downloaded bytes.
   - Preserves original bytes in immutable storage.

---

## 6. Structured XBRL Financial Extraction

Stage 86 extracts authoritative accounting facts directly from XBRL instance documents (`.xml`, `.htm` inline XBRL) without loss of context or precision:

- **US-GAAP Taxonomy Concepts**: Preserves official concept identity (e.g. `us-gaap:Revenues`, `us-gaap:CostOfGoodsAndServicesSold`, `us-gaap:GrossProfit`, `us-gaap:ResearchAndDevelopmentExpense`, `us-gaap:OperatingIncomeLoss`, `us-gaap:NetIncomeLoss`, `us-gaap:EarningsPerShareDiluted`, `us-gaap:Assets`, `us-gaap:Liabilities`, `us-gaap:StockholdersEquity`).
- **Context Period Type**: Distinguishes between `DURATION` (Income Statement and Cash Flow items covering a period) and `INSTANT` (Balance Sheet items measured at a specific point in time).
- **Units & Scale**: Preserves exact unit definitions (`USD`, `SHARES`, `USD_PER_SHARE`, `PERCENT`) and decimal precision.
- **Dimensional Breakdowns**: Preserves reporting dimensions such as business segments (e.g. iPhone, Services, Mac) without conflating them with consolidated company totals.
- **Canonical Hand-off**: Feeds validated financial facts into Stage 82 Financial Statements and Stage 83 Financial Ratios.

---

## 7. Full-Text Document Search & Highlighting

Full-text search operates over genuinely extracted and indexed filing disclosures:
- **Lexical and Section Indexing**: Indexes text segments with character offsets and parent section titles.
- **Snippet Extraction**: Returns matched sentence windows with location context.
- **Exact Highlighting**: Emphasizes matched keywords without fabricating missing passages.
- **Company-Scoped Queries**: Bounded search queries scoped strictly to the selected issuer entity.

---

## 8. Filing Comparison & Amendment Tracking

When an issuer files an amended disclosure (e.g. Form 10-K/A amending Form 10-K) or files consecutive annual reports, ATLAS enables unified multi-dimensional comparison:

1. **Textual Diffing**:
   - Computes unified line-by-line diffs (`+` additions, `-` deletions).
   - Groups diffs by document section (e.g. Part I, Item 1; Part II, Item 8).
2. **XBRL Fact Variances**:
   - Aligns facts with identical taxonomy concepts, context periods, and units.
   - Calculates Absolute Difference ($$Revised - Prior$$) and Percentage Variance.
   - Detects restatements when a prior fiscal period value is revised in a subsequent filing.
3. **Provenance Integrity**:
   - Records the exact accession numbers and SHA-256 content hashes of both compared documents.

---

## 9. Cross-Module Lineage Integration

| Upstream Module | Stage | Filing Intelligence Lineage Integration |
| :--- | :--- | :--- |
| **Universal Entities** | Stage 16 | Filing issuer UUID and reporting entity identity |
| **Financial Instruments** | Stage 17 | Related traded equity securities (Common Stock, Preferred) |
| **Document Entities** | Stage 20 | Canonical storage, content hashing, and access policies |
| **Provenance** | Stage 24 | Complete regulatory citation links (`SEC:EDGAR:{accession}`) |
| **Financial Statements** | Stage 82 | Source lineage linking normalized line items to XBRL facts |
| **Financial Ratios** | Stage 83 | Formula inputs traced to filing disclosures |
| **Earnings** | Stage 84 | Form 8-K / 10-Q press release and exhibit source links |
| **Ownership** | Stage 85 | Form 13F, 13D/G, and Form 4 insider disclosure references |

---

## 10. REST API Reference

All endpoints are mounted under `/api/v1/companies/{company_id}/filings` and require authenticated credentials with the `ATLAS_ACCESS` permission.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Catalog of filings with filters for category, form type, period, and pagination. |
| `GET` | `/overview` | Executive summary: coverage, latest 10-K, latest 10-Q, latest 8-K. |
| `GET` | `/coverage` | Source regulator coverage, CIK, available forms, date bounds, and fair access status. |
| `GET` | `/search?q={query}` | Company-scoped full-text search across indexed filing documents. |
| `GET` | `/compare?left_filing_id={l}&right_filing_id={r}` | Unified textual diff and XBRL fact variance comparison. |
| `GET` | `/{filing_id}` | Detailed filing metadata, attachments list, and structural sections. |
| `GET` | `/{filing_id}/documents` | Complete list of primary documents and exhibit attachments. |
| `GET` | `/{filing_id}/content` | Authorized document content (sanitized HTML and extracted plain text). |
| `GET` | `/{filing_id}/facts` | Extracted structured XBRL financial facts with taxonomy concepts and values. |
| `GET` | `/{filing_id}/sources` | Official source reference, official archive URL, SHA-256 hash, and attribution. |

---

## 11. Verification & Quality Gates

| Verification Gate | Command / Tool | Status |
| :--- | :--- | :--- |
| **Python Unit & API Tests** | `pytest apps/api/tests/test_company_filings.py -v` | **14 / 14 PASSED** |
| **Full Companies Regression**| `pytest apps/api/tests/test_compan*.py` | **147 / 147 PASSED** |
| **Python Code Quality** | `ruff check python/atlas/... apps/api/...` | **ALL CHECKS PASSED** |
| **TypeScript Typecheck** | `cmd /c npx tsc --noEmit` | **0 ERRORS** |
| **Next.js Production Build** | `cmd /c npm run build` | **COMPILED IN 2.8s** |

---

## 12. Next Stage Boundary

- **Stage 86 Complete**: Institutional Company Filings Intelligence.
- **Stage 87**: Build Company Peers and Comparable Company Analysis (Next Canonical Stage).
