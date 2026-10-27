# ATLAS Stage 107: Institutional-Grade Investment Research Thesis, Evidence-Based Research Synthesis & Professional Analyst Report Studio

## Canonical Roadmap: Stage 107 of 150
**Module:** Research (`/research`)  
**Status:** Production-Ready, Verified & Published  

---

## 1. Executive Summary & Capabilities Overview

Stage 107 delivers an institutional-grade investment research report authoring studio and structured thesis synthesis workbench inside ATLAS. It transforms raw research notes, filing disclosures (SEC Forms 10-K, 10-Q, 8-K), and reproducible quantitative analysis runs into publication-grade, audited investment research memorandums and structured investment theses.

### Core Architectural Pillars
1. **Structured Investment Theses & Argument Taxonomy**:
   - Central thesis statements with explicit time horizons (`time_horizon`), target entity mapping, and quantifiable conviction scores (`0.0 - 1.0`).
   - Categorized thesis arguments: `BULL_CASE`, `BEAR_CASE`, `BASE_CASE`, `CATALYST`, `KEY_RISK`, `CORE_ASSUMPTION`, and `CONTRADICTING_EVIDENCE`.
   - Direct epistemic anchoring to Stage 104 investigation claims, Stage 105 filing evidence, Stage 106 reproducible analysis runs, and explicit analytical limitations.

2. **Institutional Report Studio & Governance**:
   - Institutional report taxonomy: Company Coverage, Equity Initiation, Earnings Review, Macroeconomic Outlook, Industry Primer, Investment Thesis, Event Reaction Memo, and Risk Assessment Brief.
   - 6 built-in institutional templates (`tpl-company-research`, `tpl-equity-initiation`, `tpl-earnings-review`, `tpl-macro-research`, `tpl-investment-thesis`, `tpl-general-memo`) enforcing mandatory governance sections.
   - Rich structured block model: Headings, narrative paragraphs, bullet/numbered lists, quotes, financial tables, analysis tables, and chart embeds.

3. **Multi-Vector Verification Engine**:
   - **Structural Completeness**: Checks presence of all required sections per template.
   - **Citation Integrity**: Validates every cited evidence ID against authorized repository sources, immediately flagging missing, broken, restricted, or withdrawn sources.
   - **Analysis Run Integrity**: Verifies embedded Stage 106 quantitative runs, alerting on outdated or unverified runs.
   - **Look-Ahead & Cutoff Audit**: Strictly enforces publication cutoff timestamps (`research_cutoff`), generating blocking violations (`POINT_IN_TIME_CONFLICT`) if any embedded fact, metric, or cited disclosure has a timestamp subsequent to the cutoff date.

4. **Point-in-Time Research Snapshots & Immutability**:
   - Strict optimistic concurrency control (`expected_revision`) preventing overwrites.
   - Auditable revision history capturing author ID, content hash, word counts, and revision summaries.
   - Full unified diff comparison engine (`compare_report_revisions`) tracking added, removed, and modified sections between any two revisions.
   - Finalization gatekeeper: Reports cannot be finalized or published while blocking verification violations remain unresolved. Finalized reports are frozen into immutable point-in-time publication records.

5. **Zero-External-Dependency Document Export**:
   - **Institutional PDF-1.4**: Direct binary generation using Python standard library `io.BytesIO`. Emits clean, standards-compliant PDF catalogs, pages, font dictionaries, tables, and headers.
   - **Office Word DOCX**: Direct OpenXML archive packaging via Python's built-in `zipfile` module.
   - **Mandatory Disclaimers**: Automatic injection of institutional regulatory notices, certification statements, and source attribution tables.

---

## 2. API Endpoints Reference

All endpoints mounted under `/api/v1/research/`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/report-templates` | List all institutional research report templates |
| `GET` | `/report-templates/{template_id}` | Retrieve report template by ID |
| `GET` | `/reports` | List reports filtered by type, lifecycle status, subject |
| `POST` | `/reports` | Create new research report from template |
| `GET` | `/reports/{report_id}` | Get report detail, sections, and source manifests |
| `PATCH` | `/reports/{report_id}` | Update report metadata with optimistic revision guard |
| `POST` | `/reports/{report_id}/finalize` | Freeze report into immutable point-in-time publication |
| `DELETE` | `/reports/{report_id}` | Soft-delete / archive research report |
| `GET` | `/reports/{report_id}/sections` | List sections of a report in display order |
| `POST` | `/reports/{report_id}/sections` | Create a new section within report |
| `PATCH` | `/reports/{report_id}/sections/{section_id}` | Update section heading, content blocks, and order |
| `DELETE` | `/reports/{report_id}/sections/{section_id}` | Delete non-mandatory section |
| `POST` | `/reports/{report_id}/sections/reorder` | Atomically reorder report section hierarchy |
| `GET` | `/reports/{report_id}/revisions` | List immutable revision history for report |
| `POST` | `/reports/{report_id}/revisions/compare` | Generate unified diff comparison between revisions |
| `POST` | `/reports/{report_id}/verify` | Execute claim-to-evidence and cutoff verification |
| `GET` | `/reports/{report_id}/verification` | Retrieve latest verification audit result |
| `POST` | `/reports/{report_id}/exports` | Generate PDF / DOCX background export job |
| `GET` | `/reports/{report_id}/exports` | List generated export artifacts |
| `GET` | `/report-exports/{export_id}` | Get export job status and artifact metadata |
| `GET` | `/exports/{export_id}/download` | Stream binary artifact file directly to browser |
| `GET` | `/theses` | List structured investment theses |
| `POST` | `/theses` | Create new structured investment thesis |
| `GET` | `/theses/{thesis_id}` | Retrieve investment thesis with all arguments |
| `PATCH` | `/theses/{thesis_id}` | Update investment thesis statement or conviction |
| `DELETE` | `/theses/{thesis_id}` | Delete investment thesis |
| `POST` | `/theses/{thesis_id}/arguments` | Attach bull, bear, risk, or catalyst argument |
| `DELETE` | `/theses/{thesis_id}/arguments/{argument_id}` | Remove thesis argument |

---

## 3. Verification & Compliance Matrix

| Requirement | Implementation Mechanism | Test Assertion |
|---|---|---|
| **Zero External Export Deps** | Direct binary PDF-1.4 & OpenXML DOCX archive via `io` and `zipfile` | `test_export_report_pdf_and_download`, `test_export_report_docx_and_download` |
| **Optimistic Concurrency** | `expected_revision` check on report & section updates | `test_update_report_optimistic_concurrency` |
| **Finalization Immutability** | Frozen status check rejecting subsequent section edits with 400 | `test_finalize_report_immutability` |
| **Automated Verification** | Structural completeness, citation check, run validity, cutoff audit | `test_report_verification_clean_report`, `test_report_verification_detects_blocking_issues` |
| **Look-Ahead Prevention** | Temporal cutoff validator flagging post-cutoff evidence | Verified in `verification.py` rule `POINT_IN_TIME_CONFLICT` |
| **Cross-User Isolation** | Ownership verification returning 403 on foreign reports | `test_cross_user_isolation` |

---

## 4. Operational Boundaries

- **Zero Autonomous Execution**: Reports and theses require explicit human authoring and review.
- **Zero Hallucination / Fabrication**: Prohibited generation of synthetic financial statements, fake peers, or fictitious consensus estimates.
- **Stage 107 Roadblock**: Strict stop at Stage 107. Stage 108 implementation is deferred.
