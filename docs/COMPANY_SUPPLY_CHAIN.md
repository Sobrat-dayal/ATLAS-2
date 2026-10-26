# ATLAS Company Supply Chain Intelligence (Stage 88)

## 1. Executive Overview

Stage 88 implements **Institutional-Grade Company Supply Chain Intelligence** for the ATLAS platform, integrated into the `/companies` workspace.

The system empowers equity analysts, credit researchers, supply chain risk officers, and quantitative investors to discover, explore, visualize, and audit verified commercial relationships between corporate entities.

### Core Capabilities:
1. **Canonical Entity Resolution**: Counterparties are keyed by persistent canonical UUIDs, distinguishing legal entities from brand names and parent entities from subsidiaries.
2. **Strict Supplier-to-Customer Directionality**: All relationships adhere to the canonical orientation:
   $$\text{SUPPLIER} \longrightarrow \text{CUSTOMER}$$
   meaning the Supplier delivers goods, components, or services to the Customer.
3. **Comprehensive Commercial Taxonomy**: 12 specific commercial edge classifications, including component supply, raw materials, contract manufacturing (Foundry/OSAT), OEM, ODM, distribution channels, and logistics.
4. **Verifiable Filing Evidence**: Zero-inference standard. Every edge is linked to authentic regulatory filings (SEC Form 10-K, Form 8-K, Corporate Procurement Disclosures) with document IDs, section anchors, publication timestamps, and quoted disclosure text.
5. **Bounded Multi-Tier Network Traversal**: Breadth-first graph traversal engine supporting Tier-1 direct relationships, Tier-2 precursors (e.g., semiconductor capital equipment and raw silicon), and cycle protection with strict server-side resource limits ($\text{depth} \le 3$, $\text{max nodes} \le 150$, $\text{max edges} \le 300$).
6. **Customer & Supplier Concentration Analysis**: Source-reported dependency metrics under ASC 280 segment reporting rules, preserving anonymous customer disclosures without speculative guessing.
7. **Point-in-Time Historical Timeline**: Audit trail of announced supply agreements, multi-year extensions, and supplier changes without look-ahead bias.
8. **Disclosure Boundary & Coverage Reporting**: Explicit quantification of coverage boundaries, authorized providers, jurisdictions, and documented limitations.

---

## 2. Canonical Relationship Orientation & Semantics

The ATLAS corporate relationship graph models commercial transactions strictly from upstream to downstream:

```
[Supplier: Taiwan Semiconductor Manufacturing Co.] 
                    │
                    │ SUPPLIES_COMPONENTS_TO (A-Series & M-Series Silicon)
                    ▼
          [Customer / Subject: Apple Inc.]
                    │
                    │ DISTRIBUTES_PRODUCTS_FOR (Retail & Enterprise Distribution)
                    ▼
          [Channel Partner: Best Buy Co., Inc.]
```

### Relationship Categories:
| Category Code | Description | Example |
| :--- | :--- | :--- |
| `SUPPLIES_COMPONENTS_TO` | Direct custom or standard components | Sony CMOS image sensors $\to$ Apple Inc. |
| `SUPPLIES_RAW_MATERIALS_TO` | Bulk inputs, chemicals, wafers | Shin-Etsu silicon ingots $\to$ TSMC |
| `SUPPLIES_PRODUCTS_TO` | Off-the-shelf commercial goods | Qualcomm 5G modems $\to$ Apple Inc. |
| `PROVIDES_SERVICES_TO` | Technical, IP, or engineering services | Cloud infrastructure $\to$ Enterprise client |
| `CONTRACT_MANUFACTURES_FOR` | Contract assembly and fabrication | Hon Hai (Foxconn) assembly $\to$ Apple Inc. |
| `OEM_SUPPLIES_TO` | Original Equipment Manufacturer parts | Foxconn specialized chassis $\to$ Apple Inc. |
| `ODM_MANUFACTURES_FOR` | Original Design Manufacturer units | Reference board design $\to$ Customer |
| `DISTRIBUTES_PRODUCTS_FOR` | Retail and commercial distribution | Best Buy distribution $\to$ Consumer hardware |
| `PROVIDES_LOGISTICS_TO` | Freight, warehousing, fulfillment | Carrier delivery $\to$ Hardware manufacturer |
| `SELLS_GOODS_TO` | General commercial transactions | Commercial sales agreement |
| `LICENSES_TECHNOLOGY_TO` | Intellectual property or patents | Arm architecture licensing $\to$ Semiconductor designer |
| `OTHER_COMMERCIAL_RELATIONSHIP` | Qualified commercial contract | Documented commercial partnership |

---

## 3. Entity Resolution Principles

1. **No Ticker-Only Joins**: Counterparty nodes are identified by verified canonical UUIDs.
2. **Legal Entity vs. Brand**: A commercial statement citing "Gorilla Glass" is resolved to the contracting legal entity *Corning Incorporated*.
3. **Parent vs. Subsidiary**: Assembly relationships naming *Hon Hai Precision Industry Co., Ltd.* preserve the legal parent entity rather than an unverified local operating subsidiary.
4. **Public & Private Entities**: Unlisted private suppliers and foreign joint ventures are supported as canonical entities without requiring public exchange tickers.
5. **Anonymous Disclosures**: When SEC filings state *"During fiscal 2024, one customer accounted for 87% of net sales"*, ATLAS records `is_anonymous = true` with counterparty title *"Customer A (Anonymous Disclosed in SEC 10-K Note 12)"*. The system strictly forbids guessing or fabricating the identity of Customer A.

---

## 4. Evidence & Provenance Verification

Every commercial relationship edge requires explicit supporting evidence:
- **`source_document_id`**: Canonical document reference (e.g., `sec-edgar-aapl-10k-2024`).
- **`source_title`**: Formal publication title (e.g., *SEC Form 10-K (Annual Report) - Apple Inc.*).
- **`section_anchor`**: Exact filing section (e.g., *Item 1. Business - Supply Agreement Disclosures*).
- **`filing_date`**: Verified date filed with the regulatory authority.
- **`published_at`**: Point-in-time timestamp for historical backtesting and no-lookahead isolation.
- **`excerpt`**: Verbatim extracted quote from the disclosure.
- **`review_status`**: Review tier (`VERIFIED`, `SOURCE_REPORTED`, `CORROBORATED`).

---

## 5. Bounded Multi-Tier Graph Traversal

The traversal engine (`traverse_supply_network`) executes bounded Breadth-First Search (BFS):
1. **Tier 1 Direct**: Upstream suppliers (`edge.target == subject`) and downstream customers (`edge.source == subject`).
2. **Tier 2 Precursors**: Suppliers to direct suppliers (e.g., *ASML Holding N.V.* photolithography systems $\to$ *TSMC* $\to$ *Apple Inc.*).
3. **Cycle Protection**: Visited node tracking prevents infinite loops in circular or reciprocal commercial relationships (e.g., Company A $\to$ Company B $\to$ Company C $\to$ Company A).
4. **Performance Limits**: Traversal depth capped at 3, maximum 150 nodes, maximum 300 edges.

---

## 6. Customer & Supplier Concentration

### Customer Concentration:
Under ASC 280 (Segment Reporting) and Item 101 of Regulation S-K:
- Customers accounting for $\ge 10\%$ of consolidated net sales must be disclosed.
- Exposure percentage is source-reported from the audited financial footnote.
- For high-dependency suppliers (e.g., *Cirrus Logic* where Customer A represents 87% of net sales), the exact percentage and dollar exposure are recorded with denominator qualification.

### Supplier Concentration:
- Disclosed in Item 1A (Risk Factors) and Item 1 (Business).
- Single-source critical dependencies (e.g., TSMC advanced packaging for custom silicon) are preserved with qualitative criticality indicators.

---

## 7. HTTP API Specification

Base Route: `/api/v1/companies/{company_id}/supply-chain`

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/overview` | Executive summary, supplier counts, concentration flags, coverage summary |
| `GET` | `/suppliers` | Direct & multi-tier supplier relationships with product context and evidence |
| `GET` | `/customers` | Direct customer relationships and commercial distribution channels |
| `GET` | `/network` | Bounded directed graph topology (nodes and edges) with depth control |
| `GET` | `/relationships/{id}` | Detailed relationship record and product specifications |
| `GET` | `/relationships/{id}/evidence` | Supporting regulatory filing excerpts and citation lineage |
| `GET` | `/concentration` | Source-reported customer and supplier revenue concentration observations |
| `GET` | `/history` | Historical timeline of disclosed supply agreements and renewals |
| `GET` | `/coverage` | Disclosure boundaries, authorized providers, and documented limitations |
| `GET` | `/filters` | Available taxonomy codes, verification statuses, and covered countries |

---

## 8. Frontend Architecture & Workspaces

The Supply Chains workspace is mounted within `/companies` under the subtab `Supply Chains`:
- **Overview Cards**: High-level counts for direct suppliers, distribution channels, concentration risks, and filing freshness.
- **Suppliers Table**: High-density table with tier badges (Tier 1 vs Tier 2), category tags, supplied items, and one-click evidence inspector.
- **Customers Table**: Directional customer table showing channel types, product scopes, and reported revenue dependencies.
- **Network Explorer**: Interactive directed SVG network visualization displaying upstream precursors, direct suppliers, subject entity, and downstream distribution channels with directional bezier flow arrows and zoom controls.
- **Edge Inspector Drawer**: Full regulatory evidence audit modal displaying verbatim SEC excerpts, section anchors, and review status.
- **Dependency Analysis**: Disclosed customer concentration table, anonymous counterparty cards, and single-source supplier dependencies.
- **Historical Timeline**: Chronological point-in-time milestone timeline.
- **Evidence & Coverage**: Comprehensive data coverage specification, active providers, and documented disclosure thresholds.

---

## 9. Invariants & Security Boundaries

1. **Zero LLM Calls**: Supply chain relationships, counterparties, and concentration percentages are never generated by generative AI.
2. **Zero Inferred Edges**: Shared industry or sector classifications never synthesize supplier relationships.
3. **No Look-Ahead Leakage**: Historical views use only filings published on or before the observation date.
4. **No Trading Execution**: Ordinary supply chain intelligence queries never execute trades, broker actions, or portfolio alterations.
5. **No Stage 89 Economics**: Macroeconomic indicators, central bank policies, and country forecasting remain strictly reserved for Stage 89.
