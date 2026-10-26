# ATLAS Stage 98: Institutional-Grade Natural-Language Financial Screener Translation Engine

## 1. Executive Summary & Canonical Roadmap Alignment
Stage 98 represents the culmination of the 5-stage Screener series (Stages 94, 95, 96, 97, 98) within ATLAS. It introduces the **Natural-Language Financial Screener Translation Engine**, an institutional-grade query interpretation subsystem that translates unstructured, human financial queries into deterministic, schema-constrained filter specifications.

This stage bridges quantitative intent and rigorous execution:
1. **Deterministic Primary Implementation**: Zero external LLM calls or API keys are required for normal operational parsing, validation, and translation.
2. **Schema-Constrained Grounding**: Natural language queries are grounded exclusively to the canonical 70-filter catalog established across Stages 94–96.
3. **Financial Terminology Understanding**: Comprehensive multi-locale lexicon resolving aliases, abbreviations, financial ratios, technical indicators, and Indian/international numeric magnitudes.
4. **Interactive Ambiguity Resolution**: Subjective phrases (e.g., "cheap", "profitable", "oversold") trigger structured clarifying questions with presets rather than fabricated assumptions.
5. **Prompt-Injection Defense**: Robust pattern detection rejecting instruction-override attempts, prompt leaking, and adversarial manipulation.
6. **Query Modification Diffing**: Transparent comparison of added, modified, removed, and retained filters when mutating existing screens.

```
                      ATLAS SCREENER WORKSPACE (/screeners)
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
 [VISUAL FILTER BUILDER]                                [NATURAL-LANGUAGE ENGINE]
 • Manual Condition Composition                         • Plain-Text Input
 • Metric Selector & Operators                          • Lexicon Grounding (70 Filters)
 • Direct Registry Validation                           • Numeric & Currency Normalizer
           │                                                         │
           │                     ┌───────────────────────────────────┤
           │                     ▼                                   ▼
           │           [AMBIGUITY DETECTOR]               [SECURITY & INJECTION GUARD]
           │           • Subjective Terms                 • Override Prevention
           │           • Disambiguation Questions         • Safety Diagnostics
           │                     │                                   │
           │                     └─────────────────┬─────────────────┘
           │                                       ▼
           │                            [TRANSLATION PROPOSAL]
           │                            • Filter Conditions (Stage 94-96 Schema)
           │                            • Universe & Scope Overrides
           │                            • Sort Keys & Direction
           │                            • Modifications Diff
           │                                       │
           └─────────────────────┬─────────────────┘
                                 ▼
                     [STAGE 94-97 SCREENER ENGINE]
                     • Execution & Verification
                     • Sorting & Quantitative Ranking
                     • Multi-Sheet Export (CSV/XLSX)
```

---

## 2. Core Architectural Principles & Guardrails

### 2.1 Natural Language as an Input Surface
Natural language is strictly an input modality, not an alternative execution engine. A translated natural language query compiles directly into a canonical `ScreenerRunRequest` validated by the Stage 94–97 screener schema. The underlying execution engine remains the single source of truth for all universe filtering, statistical calculations, and data provenance.

### 2.2 Zero Fabricated Data or Metrics
The translation engine strictly forbids:
- Fabricating non-existent financial metrics or indicators.
- Estimating or inventing security match counts without evaluating against the catalog.
- Silently omitting unsupported user clauses.
- Silently guessing thresholds for subjective or vague terms.

If a requirement cannot be deterministically mapped to the catalog, it is marked with status `UNSUPPORTED`, and a clear explanation is provided to the user.

---

## 3. Financial Lexicon & Semantic Mapping

The semantic engine maps plain English, industry shorthand, and regional phrasing across the 70 canonical filters.

### 3.1 Valuation & Fundamentals
- **P/E Ratio**: "pe", "p/e", "price to earnings", "price-to-earnings", "earnings multiple", "trailing pe", "ttm pe".
- **Forward P/E**: "forward pe", "fpe", "ntm pe", "forward price to earnings".
- **P/B Ratio**: "pb", "p/b", "price to book", "book multiple", "price/book".
- **EV/EBITDA**: "ev/ebitda", "enterprise multiple", "ev to ebitda", "enterprise value to ebitda".
- **EV/Sales**: "ev/sales", "ev to sales", "enterprise value to sales".
- **Dividend Yield**: "dividend yield", "div yield", "dividend", "yield".
- **Return on Equity (ROE)**: "roe", "return on equity", "equity return".
- **Return on Assets (ROA)**: "roa", "return on assets".
- **Return on Capital Employed (ROCE)**: "roce", "return on capital employed".
- **Debt-to-Equity**: "debt to equity", "debt/equity", "d/e", "leverage ratio".
- **Current Ratio**: "current ratio", "working capital ratio", "liquidity ratio".
- **Free Cash Flow Yield**: "fcf yield", "free cash flow yield".

### 3.2 Technical Indicators & Lookback Parameters
- **RSI**: "rsi", "relative strength", "relative strength index". Parameter extraction defaults to `period=14`.
- **SMA / EMA**: "sma", "moving average", "simple moving average", "ema", "exponential moving average". Parameter extraction handles lookback windows (e.g., "50-day", "200 day", "20 sma").
- **MACD**: "macd", "moving average convergence divergence". Parameter extraction defaults to `(12, 26, 9)`.
- **Bollinger Bands**: "bollinger", "bb", "bollinger bands". Defaults to `period=20, std_dev=2.0`.
- **Average True Range (ATR)**: "atr", "average true range". Defaults to `period=14`.
- **ADX**: "adx", "average directional index", "trend strength". Defaults to `period=14`.

### 3.3 Numeric & Magnitude Normalization
The engine normalizes both Western and Indian numbering formats:
- **Indian Numbering**:
  - `lakh` / `lakhs`: Multiplier $10^5$ ($100,000$).
  - `crore` / `crores`: Multiplier $10^7$ ($10,000,000$).
  - `lakh crore`: Multiplier $10^{12}$ ($1,000,000,000,000$).
- **International Abbreviations**:
  - `k`: Multiplier $10^3$ ($1,000$).
  - `m` / `million`: Multiplier $10^6$ ($1,000,000$).
  - `b` / `bn` / `billion`: Multiplier $10^9$ ($1,000,000,000$).
  - `tr` / `trillion`: Multiplier $10^{12}$ ($1,000,000,000,000$).
- **Percentages & Basis Points**:
  - "15%" $\to$ numeric value `15.0`.
  - "100 bps" $\to$ numeric value `1.0` (basis points divided by 100).
- **Ranges**:
  - "between 5000 crore and 20000 crore INR" $\to$ extracted and resolved before clause splitting.

### 3.4 Currency Normalization
Recognizes and extracts currencies:
- **INR / ₹**: `INR`
- **USD / $**: `USD`
- **EUR / €**: `EUR`
- **GBP / £**: `GBP`

---

## 4. Interactive Ambiguity Resolution

Subjective, relative, or contextual terms cannot be deterministically translated into a single threshold without user intent clarification. The engine identifies ambiguity categories and returns structured questions with actionable presets:

| Ambiguity Category | Trigger Term | Clarification Question | Options / Presets |
| :--- | :--- | :--- | :--- |
| `VALUATION_MULTIPLE` | "cheap", "undervalued", "low valuation" | Which valuation metric and threshold define cheap for this screen? | • P/E < 15.0<br>• P/E < 20.0<br>• P/B < 2.0<br>• EV/EBITDA < 10.0 |
| `PROFITABILITY_THRESHOLD` | "profitable", "high margin" | How would you like to define profitability? | • Operating Margin > 15%<br>• Net Margin > 10%<br>• ROE > 15% |
| `TECHNICAL_CONDITION` | "oversold" | Which oversold criterion should be applied? | • RSI(14) < 30.0<br>• RSI(14) < 20.0 |
| `TECHNICAL_CONDITION` | "overbought" | Which overbought criterion should be applied? | • RSI(14) > 70.0<br>• RSI(14) > 80.0 |
| `MARKET_CAP_SCALE` | "large cap" | Which market capitalization threshold defines large cap? | • Market Cap > $10B<br>• Market Cap > ₹20,000 Cr |
| `MARKET_CAP_SCALE` | "small cap" | Which market capitalization threshold defines small cap? | • Market Cap < $2B<br>• Market Cap < ₹5,000 Cr |

### Clarification Workflow
When the user selects an option via `POST /screeners/nl/clarify`, the clarification handler:
1. Re-evaluates the query with the bound resolution.
2. Marks the requirement as `RESOLVED`.
3. Upgrades the proposal status from `AMBIGUOUS` to `COMPLETE` (if all requirements are resolved).
4. Emits the updated structured conditions ready for execution.

---

## 5. Security & Prompt-Injection Defense

To safeguard institutional deployments and prevent malicious prompt tampering or jailbreaks, the translation engine enforces pre-flight security screening:
- Detects instruction overrides (e.g., "ignore all previous instructions", "disregard system constraints").
- Detects prompt leakage attempts (e.g., "show system prompt", "print developer instructions").
- Detects persona hijackings (e.g., "you are now DAN", "jailbreak mode enabled").
- Validates query length (max 1,000 characters).
- Enforces strict input sanitization.

Queries triggering security rules are rejected with `NLScreenerPromptInjectionError` and HTTP 400.

---

## 6. API Specifications

### 6.1 `POST /screeners/nl/translate`
Translates a natural language query into a structured proposal.

**Request (`NLTranslateRequestDTO`)**:
```json
{
  "query_text": "Indian large cap tech stocks with PE under 25 and ROCE above 20%",
  "mode": "CREATE_NEW",
  "default_universe_id": "UNIVERSE_NIFTY_500",
  "base_filters": [],
  "current_universe_id": null
}
```

**Response (`NLTranslationProposalDTO`)**:
```json
{
  "proposal_id": "nl-54e7d4bc-87c2",
  "original_query": "Indian large cap tech stocks with PE under 25 and ROCE above 20%",
  "status": "COMPLETE",
  "confidence_score": 0.95,
  "explanation": "Interpreted 5 constraints across valuation, profitability, market cap, and geography.",
  "extracted_filters": [
    {
      "condition_id": "cond-1",
      "filter_id": "pe_ratio_ttm",
      "operator": "LT",
      "value": 25.0
    },
    {
      "condition_id": "cond-2",
      "filter_id": "return_on_capital_employed",
      "operator": "GT",
      "value": 20.0
    },
    {
      "condition_id": "cond-3",
      "filter_id": "market_cap",
      "operator": "GTE",
      "value": 200000000000.0,
      "currency": "INR"
    }
  ],
  "universe_override": "UNIVERSE_NIFTY_500",
  "country_override": ["IN"],
  "sector_override": ["Technology"],
  "sort_criteria": [],
  "resolutions": [],
  "ambiguities": [],
  "modifications_diff": null
}
```

### 6.2 `POST /screeners/nl/clarify`
Resolves ambiguous requirements with explicit user selections.

**Request (`NLClarifyRequestDTO`)**:
```json
{
  "proposal_id": "nl-54e7d4bc-87c2",
  "selected_options": {
    "ambig-valuation-pe": "pe_lt_15"
  }
}
```

### 6.3 `GET /screeners/nl/capabilities`
Returns the translation engine's supported filters, aliases, indicators, and capabilities manifest.

---

## 7. Frontend User Experience

The web client integrates Stage 98 into the `/screeners` workspace:
1. **Mode Switcher**: Easily toggle between **Visual Filters** (manual rule builder) and **Natural Language (AI)** translation.
2. **Interactive Prompt Console**: Input natural language financial queries with quick-fill institutional examples.
3. **Translation Review Panel**:
   - Status badge (`COMPLETE`, `AMBIGUOUS`, `UNSUPPORTED`).
   - Confidence indicator ($0\%$ to $100\%$).
   - Plain-English interpretation overview.
   - Disambiguation questions with instant selectable options.
   - Filter preview chips showing metric, operator, value, currency, and parameters.
   - Diff badges for query modification (Added, Modified, Removed, Retained).
4. **Action Handlers**:
   - **Apply & Run Screener**: Immediately executes the translated proposal and populates the results table.
   - **Transfer to Visual Builder**: Hands off the generated filters to the visual builder for manual fine-tuning.

---

## 8. Verification & Quality Metrics

Stage 98 has been verified across both backend and frontend test suites:
- **Backend (Pytest)**:
  - `apps/api/tests/test_screener_nl_translation.py`: 29 test cases covering golden queries, magnitudes (crores, lakhs, billions), currency resolution, technical indicators, ambiguity prompts, interactive clarification, security validation, and API endpoints. All 29 passed.
  - Complete Screener Suite (Stages 94–98): 95 test cases across `python/atlas` and `apps/api` all passing cleanly.
  - Ruff Linter & Formatter: 0 errors.
- **Frontend (Node/TSX)**:
  - `apps/web/src/lib/screeners/__tests__/stage98_nl_translation.test.ts`: 27 tests covering request construction, proposal validation, ambiguity rendering, unsupported handling, diff calculation, and execution compilation. All 27 passed.
  - TypeScript Compilation: `tsc --noEmit` exits with 0 errors.

---

## 9. Stage Completion & Roadmap Hand-Off

With Stage 98 complete, the Screener module has achieved full institutional maturity across all 5 planned stages:
- **Stage 94**: Core Screener Engine, Canonical Filter Catalog, In-Memory Storage & Search.
- **Stage 95**: Institutional Visual Screener Builder, Live Preview, Contradiction Detection.
- **Stage 96**: Multi-Factor Screener Engine, Advanced Technical and Fundamental Indicators.
- **Stage 97**: Saved Screeners, Multi-Column Sorting, Factor Ranking, and Multi-Sheet Exports.
- **Stage 98**: Natural-Language Screener Translation Engine, Semantic Mapping, Ambiguity Disambiguation.

The next roadmap stage is **Stage 99 (News Module)**. In accordance with platform governance, no Stage 99 implementation work has commenced.
