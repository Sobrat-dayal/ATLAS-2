# ATLAS Fundamental Data Architecture

## Purpose
ATLAS relies on canonical, strictly validated domain models for financial fundamental data. Rather than leaking third-party provider schemas or ambiguous data structures throughout the application, ATLAS defines a Universal Fundamental Data Language in the `atlas.fundamentals` package (Stage 34).

Fundamental Data represents reported accounting statements, fiscal period metadata, and accounting units.

## Core Principles

1. **Company Entity Centric**: Fundamental Data belongs to a canonical Company entity (`entity_id`), not a trading ticker. Tickers are routing aliases, but the source of truth for fundamentals is the actual company entity.
2. **Offline Models**: Canonical models (e.g. `IncomeStatement`, `BalanceSheet`) do not contain network requests, database connections, or ORM logic. They are pure, validated Pydantic V2 schemas.
3. **Canonical Precision**: Financial values must preserve exact reported precision. All fundamental values are captured using `CanonicalDecimal`, serialized strictly as strings to prevent binary floating-point data loss in JSON/JSONB.
4. **Base Accounting Units**: Values must use their base units (e.g. `currency="USD"`, `scale=0`) with explicit metadata, preventing arbitrary scaling (like thousands or millions) silently propagating.
5. **No Derived Metrics**: Fundamental models represent reported facts (e.g. "Revenue", "Net Income"). Calculated metrics, ratios, and valuation models are separate from canonical fundamental representations.

## Architecture

```text
       Raw Provider Payload
               │
               ▼
   ┌───────────────────────┐
   │ OpenBBProviderAdapter │ (Implements adapter mapping)
   └───────────┬───────────┘
               │
               ▼
┌─────────────────────────────┐
│    ATLAS Canonical Models   │ (atlas.fundamentals)
│                             │
│ - IncomeStatement           │
│ - BalanceSheet              │
│ - CashFlowStatement         │
│ - FinancialFact             │
└─────────────────────────────┘
               │
               ▼
   Global Application Context
```

## The Fundamental Concept Registry

ATLAS enforces a strict taxonomy of fundamental accounting concepts via the `FundamentalConceptRegistry`. 

Each `StatementLineItem` is validated against this registry to ensure:
- **Concept Existence**: The concept key (e.g. `"revenue"`) is recognized.
- **Statement Type Validation**: The concept belongs on the correct statement (e.g. `cash_and_cash_equivalents` must be on a Balance Sheet).
- **Period Nature Validation**: Concepts are strictly evaluated as either `DURATION` (Income Statement, Cash Flow) or `INSTANT` (Balance Sheet).
- **Unit Kind Validation**: Ensures that values have the correct dimensional unit (e.g. `CURRENCY` vs `SHARES` vs `CURRENCY_PER_SHARE`).

## Identifiers and Entities

Canonical Fundamental models use `uuid.UUID` representing the Stage 18 Company Entity. 
Provider integrations are responsible for maintaining the provenance, but the models themselves operate strictly on ATLAS internal `entity_id`.

## Provider Protocols

To supply fundamental data, providers must implement `@runtime_checkable` protocols:
- `IncomeStatementFundamentalProvider`
- `BalanceSheetFundamentalProvider`
- `CashFlowFundamentalProvider`
- `FinancialFactsFundamentalProvider`

The Gateway verifies provider capabilities at runtime using `FundamentalProviderCapabilities` to properly route client requests to capable integrations.

## ClickHouse
Stage 37 does not choose or create Fundamental ClickHouse schemas.
