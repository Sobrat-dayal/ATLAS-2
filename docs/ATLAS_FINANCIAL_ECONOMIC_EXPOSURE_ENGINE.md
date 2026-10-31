# ATLAS Stage 137: Financial and Economic Exposure Engine

## 1. System Overview

The **ATLAS Financial and Economic Exposure Engine** provides an institutional-grade, source-backed quantitative foundation for analyzing verified financial and economic exposures across corporate entities, portfolios, geographic territories, sectors, commodities, corporate groups, supply chains, infrastructure assets, derivatives, and macroeconomic benchmarks.

### Core Semantic Invariant
> *"What verified financial or economic exposure exists through these relationships, how is it measured, and what evidence supports the result?"*

The system maintains strict analytical separation between **Exposure** (structural connectedness and quantified holdings/revenues) and **Impact** (realized asset losses, price changes, or speculative market forecasts).

---

## 2. Institutional Invariants & Scope Boundaries

1. **Exposure Is Not Impact**: The engine measures verified structural and financial connectedness. It strictly refrains from predicting future price changes, estimating realized losses, or generating buy/sell trading signals.
2. **Zero Numerical Fabrication**: Every percentage or ratio calculation requires a verified filing, holding, or deterministic formula with explicitly disclosed numerator and denominator.
3. **No Equating Proximity with Economic Loss**: Geographic proximity between a physical facility and an event (e.g., an earthquake epicenter) confirms spatial co-location only. Operational disruption and asset damage remain `UNKNOWN` and `UNAVAILABLE` unless officially reported.
4. **No Inferring Revenue from Facility Counts**: Facility counts indicate operational presence only. Using physical facility counts as revenue or profit proxies is strictly prohibited.
5. **Corporate Group Consolidation & Double-Counting Elimination**: Consolidated parent revenue already encompasses consolidated subsidiaries. Adding parent consolidated revenue and subsidiary revenue is strictly prohibited (`DoubleCountingError`).
6. **Qualitative Supply Chain Disclosures**: Documented supplier or customer commercial ties without disclosed numerical contracts are recorded as qualitative relationships with monetary amounts set to `UNAVAILABLE` (`None`).
7. **Fund Look-Through & Cycle Prevention**: Traverses nested fund holdings by multiplying constituent weights along verified chains. Implements strict cycle detection (`CycleDetectedError`) preventing infinite loops or fabricated multi-pass allocations.
8. **Long and Short Signed Exposure**: Preserves signed net directional exposure ($\sum \text{signed}$) alongside gross economic footprint ($\sum |\text{signed}|$).
9. **Point-in-Time FX Conversion**: Historical conversions strictly utilize point-in-time rates matching financial reporting dates with validated quote directions. Missing historical rates raise `MissingCurrencyRateError`; substituting current rates is prohibited.
10. **Interest Rate Sensitivity**: Evaluates local linear dollar sensitivity using verified DV01 ($-DV01 \times \Delta y_{\text{bps}}$), strictly labeled as a scenario linear approximation.
11. **Derivative Delta-Equivalent Exposure**: Calculated as $\text{Contracts} \times \text{Multiplier} \times \text{Underlying Price} \times \Delta$ without fabricated higher-order Greeks.
12. **Preservation of Unallocated Residuals**: When reported segments explain less than 100% of a denominator (e.g., 85%), coverage is recorded as 85.0% and the unallocated residual is reported as 15.0%. Rescaling incomplete data to 100% without disclosure is prohibited.
13. **Deterministic Scenario Workbench**: Evaluates hypothetical user shocks deterministically, displaying the mandatory prominent notice: `HYPOTHETICAL SCENARIO RESULT`.
14. **Multi-Tenant Privacy**: Proprietary portfolios and custom scenarios belonging to Tenant A are strictly inaccessible to Tenant B (`TenantExposureAccessDeniedError`).
15. **Source Entitlement Invalidation**: When underlying data source licenses are revoked or expired, calculation lineages referencing them are immediately locked (`SourceLicenseRevokedError`).

---

## 3. Architecture & Domain Structure

```
python/atlas/src/atlas/exposure/
├── domain.py                   # Typed domain enums, models, and results (Decimal precision)
├── errors.py                   # Typed domain exceptions enforcing invariants
├── measures/
│   └── definitions.py          # Registered canonical measures with explicit formulas
├── calculations/
│   ├── fx.py                   # Point-in-time FX conversion with quote validation
│   ├── periods.py              # Accounting period comparability verification
│   ├── consolidation.py        # Elimination of subsidiary double-counting
│   ├── portfolio.py            # Signed Net vs Gross valuation and sector/country weights
│   ├── lookthrough.py          # Bounded nested fund look-through with cycle detection
│   └── scenarios.py            # Deterministic shock evaluation and DV01 sensitivity
├── quality/
│   └── coverage.py             # Explicit coverage ratio and unallocated residual tracking
├── lineage/
│   └── provenance.py           # Mathematical lineage audit trail and license validation
├── domains/
│   ├── company.py              # Geographic revenue shares and segment disclosures
│   ├── portfolio.py            # Portfolio holdings, weights, and unclassified disclosures
│   ├── geographic.py           # Geographic presence vs revenue separation
│   ├── corporate_group.py      # Parent vs subsidiary consolidation
│   ├── supply_chain.py         # Qualitative commercial ties vs disclosed contracts
│   ├── infrastructure.py       # Spatial event proximity without inferred loss
│   ├── derivatives.py          # Delta-equivalent options exposure
│   ├── macro.py                # DV01 interest rate sensitivity
│   ├── commodity.py            # Qualitative commodity mentions vs numerical exposure
│   ├── sector.py               # Authoritative GICS/ICB sector mappings
│   └── event_exposure.py       # Event-driven graph traversal to financial exposures
├── seed.py                     # Canonical reference fixtures (Tests A through X)
└── service.py                  # AtlasExposureEngineService master orchestrator
```

---

## 4. REST API Reference

- `GET /api/v1/intelligence/exposure/capabilities` — Returns system capabilities, supported domains, registered measures, and compliance guarantees.
- `GET /api/v1/intelligence/exposure/measures` — Returns registered canonical measure definitions.
- `POST /api/v1/intelligence/exposure/analyze/company` — Geographic revenue share and segment exposure analysis.
- `POST /api/v1/intelligence/exposure/analyze/portfolio` — Portfolio holdings, Net vs Gross, and sector/country breakdowns.
- `POST /api/v1/intelligence/exposure/analyze/event` — Event-driven exposure traversal.
- `POST /api/v1/intelligence/exposure/scenarios/run` — Deterministic scenario shock evaluation.
- `GET /api/v1/intelligence/exposure/runs/{id}` — Retrieve analysis run with tenant authorization checks.
- `GET /api/v1/intelligence/exposure/runs/{id}/results` — List results for an analysis run.
- `GET /api/v1/intelligence/exposure/runs/{id}/coverage` — Coverage ratio and unallocated residual breakdown.
- `GET /api/v1/intelligence/exposure/lineage/{exposure_id}` — Mathematical lineage and source link with license verification.
- `GET /api/v1/intelligence/exposure/fixtures/{fixture_id}` — Pre-seeded reference test fixtures.

---

## 5. Frontend Visual Delivery (`/intelligence`)

Mounted on `/intelligence` with the tab `Exposure Engine (Stage 137)`:
- **`ExposureSummary`**: Header KPI banner displaying Measured Coverage, Unallocated Residual, Net/Gross Economic Footprint, and Active Verified Links.
- **`ExposureTable`**: Interactive tabular grid with Target Entities, Exposure Domain/Type, Amounts, Shares/Weights, Denominators, Evidence Classes, and Inspector triggers.
- **`ExposureInspector`**: Deep inspection side-drawer detailing Numerators, Denominators, Formulas, Bitemporal Timestamps, Source Manifests, and the mandatory Limitations Disclaimer.
- **`ExposureScenarioWorkbench`**: Deterministic scenario shock workbench for simulating percentage shifts on Sectors, Securities, Countries, or Rates, featuring the mandatory `HYPOTHETICAL SCENARIO RESULT` notice.
- **`ExposureCoverageView`**: Multi-segment visual bar comparing Covered Population vs Unallocated Residuals, detailing covered and uncovered dimensions.
