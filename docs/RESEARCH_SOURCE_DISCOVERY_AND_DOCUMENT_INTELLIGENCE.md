# Stage 105: Institutional-Grade Financial Research Source Discovery, Document Intelligence and Evidence Extraction Platform

**Project:** ATLAS — AI-Native Financial Intelligence and Quantitative Research Operating System  
**Canonical Roadmap Position:** Stage 105 of 150  
**Primary Module:** Research  
**Primary Route:** `/research`  
**Sub-Views:** Overview, Investigations, Source Library, Discovery, Document Viewer, Comparison, Activity Timeline  

---

## 1. Executive Overview

Stage 105 expands ATLAS's financial research layer from structured investigation management into an institutional-grade document intelligence, source discovery, and multi-document comparison platform. Built directly on top of Stage 104's research foundation and integrating canonical SEC filings, financial statement disclosures, central bank records, and macroeconomic publications, this stage delivers:

1. **Multi-Facet Research Source Discovery**: Indexed multi-facet search across corporate issuers, regulatory filing types (10-K, 10-Q, 8-K), publisher classifications, reporting periods, and full-text keyword/hybrid search with relevance scoring and highlighted snippets.
2. **Document Structure & Outline Navigation**: Extraction of hierarchical section trees (`ResearchDocumentSection`), character-offset spans (`ResearchDocumentSpan`), processing audit logs (`ResearchDocumentProcessingStatus`), and high-speed in-document search.
3. **Structured Financial Table Extraction**: Multi-dimensional matrix representation of financial tables preserving row labels, column headers, formatted display strings, raw numeric values, unit scales (`EXACT`, `THOUSANDS`, `MILLIONS`, `BILLIONS`, `PERCENTAGE`, `PER_SHARE`), ISO currencies, footnotes, and XBRL fact links.
4. **Evidence Candidate Discovery & Conversion**: Automated scanning and extraction of high-confidence disclosures as candidate evidence, physical location anchor verification against character spans, and one-click promotion into canonical Stage 104 `ResearchEvidence` linked to an active investigation with immutable activity logging.
5. **Multi-Document Comparison & Fact Variance Engine**: Two-document alignment producing unified section diffs (`diff_unified`) and mathematical financial fact variance calculation ($\Delta$ and $\%\Delta$) with robust zero-base division protection.
6. **Institutional Terminal Workspaces**: Three dedicated sub-workspaces (`ResearchSourceDiscovery`, `ResearchDocumentViewer`, and `ResearchDocumentComparison`) integrated with global state management, keyboard navigation, and Bloomberg/FactSet-grade UI ergonomics.

---

## 2. Architecture & Data Flow

```
                      +---------------------------------------+
                      |         ATLAS Client (/research)      |
                      |  - Discovery                         |
                      |  - Document Viewer (3-Pane Reader)   |
                      |  - Document Comparison & Variance    |
                      +-------------------+-------------------+
                                          | HTTP / JSON REST
                                          v
                      +---------------------------------------+
                      |      FastAPI Research Router          |
                      |   /api/v1/research/... (14 Endpoints) |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |           ResearchService             |
                      |  - Query Compilation & Facets         |
                      |  - Outline & Section Resolution       |
                      |  - Financial Table Fact Association   |
                      |  - Candidate Promotion Orchestration  |
                      |  - Variance Math & Unified Diffing    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |     ResearchRepository & Documents    |
                      |  - Pre-Indexed Canonical Filings      |
                      |  - Character Span Indexing            |
                      |  - XBRL-Linked Matrix Extraction      |
                      |  - Append-Only Activity Journal       |
                      +---------------------------------------+
```

---

## 3. Core REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/research/sources/search` | Multi-facet indexed source search with relevance scoring and highlights |
| `GET` | `/api/v1/research/source-types` | List controlled source categories and metadata |
| `GET` | `/api/v1/research/documents/{document_id}` | Retrieve document metadata by accession or source reference ID |
| `GET` | `/api/v1/research/documents/{document_id}/processing-status` | Audit document parsing, sectioning, and span extraction status |
| `GET` | `/api/v1/research/documents/{document_id}/outline` | Hierarchical outline navigation tree with section offsets |
| `GET` | `/api/v1/research/documents/{document_id}/sections` | List all parsed sections of a document |
| `GET` | `/api/v1/research/documents/{document_id}/sections/{section_id}` | Fetch isolated section content and character bounds |
| `POST` | `/api/v1/research/documents/{document_id}/search` | In-document keyword/phrase search with character span offsets |
| `GET` | `/api/v1/research/documents/{document_id}/tables` | List all extracted financial statement tables |
| `GET` | `/api/v1/research/documents/{document_id}/tables/{table_id}` | Retrieve matrix cells, raw values, and footnotes of a table |
| `POST` | `/api/v1/research/evidence/candidates` | Extract candidate evidence disclosures from document spans/tables |
| `POST` | `/api/v1/research/evidence/resolve-location` | Verify physical location anchor against document spans |
| `POST` | `/api/v1/research/evidence/convert-candidate` | Convert candidate into Stage 104 `ResearchEvidence` |
| `POST` | `/api/v1/research/documents/compare` | Two-document aligned section text diffing |
| `POST` | `/api/v1/research/financial-facts/compare` | Comparative financial statement fact variance ($\Delta$ and $\%\Delta$) |

---

## 4. Controlled Taxonomies & Data Models

### Controlled Enums (`enums.py`)
- `DocumentProcessingStatus`: `NOT_STARTED`, `QUEUED`, `PROCESSING`, `COMPLETED`, `PARTIAL`, `FAILED`, `RESTRICTED`, `UNSUPPORTED`.
- `DocumentFormat`: `HTML`, `PDF`, `PLAIN_TEXT`, `MARKDOWN`, `DOCX`, `XBRL_DATASET`.
- `SearchMode`: `KEYWORD`, `EXACT_PHRASE`, `HYBRID`.
- `DocumentComparisonMode`: `FULL_TEXT`, `SECTIONS`, `FINANCIAL_TABLES`.
- `UnitScale`: `EXACT`, `THOUSANDS`, `MILLIONS`, `BILLIONS`, `PERCENTAGE`, `PER_SHARE`.
- `ResearchActivityAction`: Appended with `DOCUMENT_PROCESSED`, `EVIDENCE_CANDIDATE_EXTRACTED`, `DOCUMENTS_COMPARED`.

### Financial Table Matrix Structure (`ResearchDocumentTable`)
```json
{
  "table_id": "tbl-operations-2024",
  "title": "Consolidated Statements of Operations",
  "period_label": "Twelve Months Ended September 28, 2024",
  "currency": "USD",
  "unit_scale": "MILLIONS",
  "headers": ["Line Item", "2024", "2023"],
  "row_labels": ["Total net sales", "Products", "Services", "Cost of sales", "Operating income", "Net income"],
  "cells": [
    ["391035", "383285"],
    ["294866", "298085"],
    ["96169", "85200"],
    ["214306", "214137"],
    ["123216", "114301"],
    ["93736", "96995"]
  ],
  "raw_values": [
    [391035.0, 383285.0],
    [294866.0, 298085.0],
    [96169.0, 85200.0],
    [214306.0, 214137.0],
    [123216.0, 114301.0],
    [93736.0, 96995.0]
  ],
  "footnotes": ["Amounts in millions, except per share data.", "Restated service revenue reflects standard reclassifications."]
}
```

---

## 5. Mathematical Variance & Delta Calculation

Financial statement comparison computes:

$$\Delta = \text{Right Value} - \text{Left Value}$$

$$\%\Delta = \begin{cases} 
\left(\frac{\Delta}{\text{Left Value}}\right) \times 100 & \text{if } \text{Left Value} \neq 0 \\
\text{null} & \text{if } \text{Left Value} = 0 \text{ (Zero-Base Protection)}
\end{cases}$$

When $\text{Left Value} = 0$, runtime division by zero is strictly avoided, returning `null` with explicit `N/A (Zero Base)` labeling in the UI.

---

## 6. Frontend Workspace Architecture

1. **`ResearchSourceDiscovery.tsx`**: Multi-facet search bar with real-time entity and filing type filters, relevance score visualization, hit snippets, and direct links to Document Viewer and Comparison.
2. **`ResearchDocumentViewer.tsx`**: Three-pane institutional reader:
   - **Left Pane:** Hierarchical section outline tree and in-document search with match offsets.
   - **Center Pane:** Active section text reader with paragraph indices and extracted financial table matrices.
   - **Right Pane:** Source provenance inspector and candidate evidence cards with one-click conversion to an investigation.
3. **`ResearchDocumentComparison.tsx`**: Document A vs. Document B comparison engine featuring preset filing pairs (e.g., Apple FY24 vs. FY23 10-K), unified text diffs with addition/removal line stats, and financial line item variance tables.
4. **`useResearchWorkspace.ts`**: Unified workspace hook managing navigation across all 7 views (`OVERVIEW`, `INVESTIGATIONS`, `SOURCES`, `DISCOVERY`, `DOCUMENT_VIEWER`, `COMPARE`, `ACTIVITY`).

---

## 7. Verification & Quality Gates

- **Backend Pytest Suite:** 32 tests passing (`test_research_document_intelligence_v1.py` and `test_research_foundation_v1.py`) covering multi-facet search, outline parsing, table extraction, anchor resolution, candidate promotion, text diffing, variance math, and error handling.
- **Frontend Test Suite:** 74 tests passing (`node:test` suite including `research_document_intelligence.test.ts` and `research_foundation.test.ts`).
- **TypeScript Static Verification:** 0 errors (`npx tsc --noEmit` exited 0).
- **Production Build:** Clean Next.js compilation across all 38 application routes including `/research`.
- **Ruff Linting:** 0 warnings or errors across all modified API files.
