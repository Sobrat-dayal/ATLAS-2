# ATLAS Company Financial Ratios & Fundamental Analysis Architecture (Stage 83)

## 1. Executive Overview & Mission

Stage 83 transforms the ATLAS Companies module into an institutional-grade, numerically validated fundamental analysis environment. It establishes a trusted, versioned Financial Ratio Registry and computation service that evaluates corporate profitability, liquidity, financial leverage, operational efficiency, cash flow generation, and equity/enterprise valuation multiples.

Every financial ratio in ATLAS is calculated strictly from explicitly defined, compatible, authorized financial observations using a trusted formula whose inputs, methodology, units, reporting periods, source revisions, and calculation timestamps are traceable to canonical accounting facts from Stage 82 Financial Statements and Stage 34 Fundamental Data.

### Core Architecture Principles:
- **No Float Arithmetic / No NaN / No Infinity:** All ratios are computed using lossless Python `Decimal` quantization. Division by zero or non-positive denominators yield typed `UNAVAILABLE` or `NOT_MEANINGFUL` (`N/M`) states rather than NaN or Infinity.
- **Strict Flow/Stock Alignment:** Income and cash flow metrics (flows) combined with balance sheet metrics (stocks) calculate average balances over opening and closing periods (e.g. `(Ending Equity + Beginning Equity) / 2`).
- **Point-in-Time Integrity:** Ratios respect financial publication dates, restatements, and market observation timestamps without future data leakage or look-ahead bias.
- **Explicit Valuation Context:** Market-based valuation multiples (P/E, EV/EBITDA, P/B, P/S, P/FCF, Dividend Yield) require qualified canonical market capitalization and share counts from Stage 33/41. Cross-listings are never double-counted.
- **Zero LLM / Zero Trading / Zero Provider Fanout:** 100% deterministic pure mathematical formulas executed on authenticated canonical financial facts.

---

## 2. Canonical Ratio Registry & Catalog (44 Ratios)

The registry defines 44 canonical financial ratios organized into 6 core analytical categories:

| Category | Count | Ratio Identifiers |
| :--- | :---: | :--- |
| **Profitability** | 8 | `profitability.gross_margin`, `profitability.operating_margin`, `profitability.ebitda_margin`, `profitability.net_margin`, `profitability.roe`, `profitability.roa`, `profitability.roic`, `profitability.roce` |
| **Liquidity** | 4 | `liquidity.current_ratio`, `liquidity.quick_ratio`, `liquidity.cash_ratio`, `liquidity.operating_cash_flow_ratio` |
| **Solvency & Leverage** | 7 | `solvency.debt_to_equity`, `solvency.debt_to_assets`, `solvency.debt_to_capital`, `solvency.net_debt`, `solvency.interest_coverage`, `solvency.debt_to_ebitda`, `solvency.net_debt_to_ebitda` |
| **Efficiency** | 8 | `efficiency.asset_turnover`, `efficiency.inventory_turnover`, `efficiency.receivables_turnover`, `efficiency.payables_turnover`, `efficiency.dso`, `efficiency.dio`, `efficiency.dpo`, `efficiency.cash_conversion_cycle` |
| **Cash Flow** | 6 | `cashflow.free_cash_flow`, `cashflow.free_cash_flow_margin`, `cashflow.operating_cash_flow_margin`, `cashflow.cash_conversion`, `cashflow.capex_to_revenue`, `cashflow.free_cash_flow_yield` |
| **Valuation Multiples** | 11 | `valuation.pe`, `valuation.forward_pe`, `valuation.pb`, `valuation.ps`, `valuation.price_to_cash_flow`, `valuation.price_to_free_cash_flow`, `valuation.enterprise_value`, `valuation.ev_to_ebitda`, `valuation.ev_to_revenue`, `valuation.dividend_yield`, `valuation.earnings_yield` |

---

## 3. Ratio Methodology Specifications

### 3.1 Profitability Ratios

1. **Gross Profit Margin (`profitability.gross_margin`):**
   - Formula: `(Gross Profit / Revenue) * 100`
   - Inputs: `gross_profit`, `revenue`
   - Unit: `PERCENT`
   - Policy: Denominator must be strictly positive. If revenue ≤ 0, returns `NOT_MEANINGFUL`.

2. **Operating Profit Margin (`profitability.operating_margin`):**
   - Formula: `(Operating Income / Revenue) * 100`
   - Inputs: `operating_income`, `revenue`
   - Unit: `PERCENT`
   - Policy: Negative operating margins are valid negative values.

3. **EBITDA Margin (`profitability.ebitda_margin`):**
   - Formula: `(EBITDA / Revenue) * 100`
   - Inputs: `ebitda` (or `operating_income + depreciation_amortization`), `revenue`
   - Unit: `PERCENT`

4. **Net Profit Margin (`profitability.net_margin`):**
   - Formula: `(Net Income / Revenue) * 100`
   - Inputs: `net_income`, `revenue`
   - Unit: `PERCENT`

5. **Return on Equity - ROE (`profitability.roe`):**
   - Formula: `(Net Income / Average Equity) * 100`
   - Inputs: `net_income`, `ending_equity`, `beginning_equity`
   - Denominator: `Average Equity = (Ending Equity + Beginning Equity) / 2`
   - Unit: `PERCENT`
   - Policy: If Average Equity ≤ 0, returns `NOT_MEANINGFUL` (`N/M`) to avoid mathematical illusions where negative losses divided by negative equity create pseudo-positive returns.

6. **Return on Assets - ROA (`profitability.roa`):**
   - Formula: `(Net Income / Average Total Assets) * 100`
   - Inputs: `net_income`, `ending_assets`, `beginning_assets`
   - Denominator: `Average Assets = (Ending Assets + Beginning Assets) / 2`
   - Unit: `PERCENT`

7. **Return on Invested Capital - ROIC (`profitability.roic`):**
   - Formula: `(NOPAT / Average Invested Capital) * 100`
   - Inputs: `operating_income`, `tax_expense`, `income_before_tax`, `ending_equity`, `ending_debt`, `ending_cash`, `beginning_equity`, `beginning_debt`, `beginning_cash`
   - NOPAT: `Operating Income * (1 - Effective Tax Rate)`, where effective tax rate is capped between 0% and 50%.
   - Invested Capital: `Total Debt + Stockholders' Equity - Cash & Equivalents`
   - Unit: `PERCENT`

8. **Return on Capital Employed - ROCE (`profitability.roce`):**
   - Formula: `(EBIT / Average Capital Employed) * 100`
   - Inputs: `operating_income`, `ending_assets`, `ending_current_liabilities`, `beginning_assets`, `beginning_current_liabilities`
   - Capital Employed: `Total Assets - Current Liabilities`
   - Unit: `PERCENT`

---

### 3.2 Liquidity Ratios

9. **Current Ratio (`liquidity.current_ratio`):**
   - Formula: `Current Assets / Current Liabilities`
   - Inputs: `current_assets`, `current_liabilities`
   - Unit: `MULTIPLE`

10. **Quick Ratio / Acid Test (`liquidity.quick_ratio`):**
    - Formula: `(Current Assets - Inventories) / Current Liabilities`
    - Inputs: `current_assets`, `inventory`, `current_liabilities`
    - Unit: `MULTIPLE`

11. **Cash Ratio (`liquidity.cash_ratio`):**
    - Formula: `Cash & Cash Equivalents / Current Liabilities`
    - Inputs: `cash_and_equivalents`, `current_liabilities`
    - Unit: `MULTIPLE`

12. **Operating Cash Flow Ratio (`liquidity.operating_cash_flow_ratio`):**
    - Formula: `Operating Cash Flow / Current Liabilities`
    - Inputs: `operating_cash_flow`, `current_liabilities`
    - Unit: `MULTIPLE`

---

### 3.3 Solvency & Financial Leverage Ratios

13. **Debt-to-Equity (`solvency.debt_to_equity`):**
    - Formula: `Total Debt / Total Stockholders' Equity`
    - Inputs: `total_debt`, `stockholders_equity`
    - Unit: `MULTIPLE`
    - Policy: If equity ≤ 0, returns `NOT_MEANINGFUL`.

14. **Debt-to-Assets (`solvency.debt_to_assets`):**
    - Formula: `Total Debt / Total Assets`
    - Inputs: `total_debt`, `total_assets`
    - Unit: `MULTIPLE`

15. **Debt-to-Capital (`solvency.debt_to_capital`):**
    - Formula: `Total Debt / (Total Debt + Stockholders' Equity)`
    - Inputs: `total_debt`, `stockholders_equity`
    - Unit: `MULTIPLE`

16. **Net Debt (`solvency.net_debt`):**
    - Formula: `Total Debt - Cash & Cash Equivalents`
    - Inputs: `total_debt`, `cash_and_equivalents`
    - Unit: `MONETARY`
    - Policy: Can be negative when a company has net net cash balances.

17. **Interest Coverage Ratio (`solvency.interest_coverage`):**
    - Formula: `EBIT / Interest Expense`
    - Inputs: `operating_income`, `interest_expense`
    - Unit: `MULTIPLE`
    - Policy: If interest expense = 0, returns `UNAVAILABLE` rather than Infinity.

18. **Debt/EBITDA (`solvency.debt_to_ebitda`):**
    - Formula: `Total Debt / EBITDA`
    - Inputs: `total_debt`, `ebitda`
    - Unit: `MULTIPLE`
    - Policy: If EBITDA ≤ 0, returns `NOT_MEANINGFUL`.

19. **Net Debt/EBITDA (`solvency.net_debt_to_ebitda`):**
    - Formula: `Net Debt / EBITDA`
    - Inputs: `total_debt`, `cash_and_equivalents`, `ebitda`
    - Unit: `MULTIPLE`

---

### 3.4 Operational Efficiency Ratios

20. **Asset Turnover (`efficiency.asset_turnover`):**
    - Formula: `Revenue / Average Total Assets`
    - Inputs: `revenue`, `ending_assets`, `beginning_assets`
    - Unit: `MULTIPLE`

21. **Inventory Turnover (`efficiency.inventory_turnover`):**
    - Formula: `Cost of Goods Sold / Average Inventory`
    - Inputs: `cost_of_goods_sold`, `ending_inventory`, `beginning_inventory`
    - Unit: `MULTIPLE`

22. **Receivables Turnover (`efficiency.receivables_turnover`):**
    - Formula: `Revenue / Average Accounts Receivable`
    - Inputs: `revenue`, `ending_receivables`, `beginning_receivables`
    - Unit: `MULTIPLE`

23. **Payables Turnover (`efficiency.payables_turnover`):**
    - Formula: `Cost of Goods Sold / Average Accounts Payable`
    - Inputs: `cost_of_goods_sold`, `ending_payables`, `beginning_payables`
    - Unit: `MULTIPLE`

24. **Days Sales Outstanding - DSO (`efficiency.dso`):**
    - Formula: `(Average Accounts Receivable / Revenue) * 365`
    - Inputs: `ending_receivables`, `beginning_receivables`, `revenue`
    - Unit: `DAYS`

25. **Days Inventory Outstanding - DIO (`efficiency.dio`):**
    - Formula: `(Average Inventory / Cost of Goods Sold) * 365`
    - Inputs: `ending_inventory`, `beginning_inventory`, `cost_of_goods_sold`
    - Unit: `DAYS`

26. **Days Payables Outstanding - DPO (`efficiency.dpo`):**
    - Formula: `(Average Accounts Payable / Cost of Goods Sold) * 365`
    - Inputs: `ending_payables`, `beginning_payables`, `cost_of_goods_sold`
    - Unit: `DAYS`

27. **Cash Conversion Cycle - CCC (`efficiency.cash_conversion_cycle`):**
    - Formula: `DIO + DSO - DPO`
    - Inputs: `dio`, `dso`, `dpo`
    - Unit: `DAYS`

---

### 3.5 Cash Flow & Capital Expenditure Metrics

28. **Free Cash Flow (`cashflow.free_cash_flow`):**
    - Formula: `Operating Cash Flow - Capital Expenditures`
    - Inputs: `operating_cash_flow`, `capital_expenditures`
    - Sign Normalization: CapEx is treated as positive cash outflow; if reported signed negative in source statements, it is correctly normalized to avoid double-negative subtraction.
    - Unit: `MONETARY`

29. **Free Cash Flow Margin (`cashflow.free_cash_flow_margin`):**
    - Formula: `(Free Cash Flow / Revenue) * 100`
    - Inputs: `free_cash_flow`, `revenue`
    - Unit: `PERCENT`

30. **Operating Cash Flow Margin (`cashflow.operating_cash_flow_margin`):**
    - Formula: `(Operating Cash Flow / Revenue) * 100`
    - Inputs: `operating_cash_flow`, `revenue`
    - Unit: `PERCENT`

31. **Cash Conversion Ratio (`cashflow.cash_conversion`):**
    - Formula: `Operating Cash Flow / Net Income`
    - Inputs: `operating_cash_flow`, `net_income`
    - Unit: `MULTIPLE`

32. **CapEx Intensity / CapEx to Revenue (`cashflow.capex_to_revenue`):**
    - Formula: `(Capital Expenditures / Revenue) * 100`
    - Inputs: `capital_expenditures`, `revenue`
    - Unit: `PERCENT`

33. **Free Cash Flow Yield (`cashflow.free_cash_flow_yield`):**
    - Formula: `(Free Cash Flow / Market Capitalization) * 100`
    - Inputs: `free_cash_flow`, `market_cap`
    - Unit: `PERCENT`

---

### 3.6 Valuation Multiples

34. **Price-to-Earnings - Trailing P/E (`valuation.pe`):**
    - Formula: `Market Capitalization / Net Income` (or `Price / EPS`)
    - Inputs: `market_cap`, `net_income`
    - Unit: `MULTIPLE`
    - Policy: If Net Income ≤ 0, returns `NOT_MEANINGFUL` (`N/M`).

35. **Forward P/E (`valuation.forward_pe`):**
    - Formula: `Price / Forward EPS Consensus`
    - Inputs: `price`, `forward_eps`
    - Policy: Supported only when verified authorized forward consensus estimates exist (Stage 84 preview; returns `UNAVAILABLE` without verified estimates).

36. **Price-to-Book - P/B (`valuation.pb`):**
    - Formula: `Market Capitalization / Total Stockholders' Equity`
    - Inputs: `market_cap`, `stockholders_equity`
    - Unit: `MULTIPLE`
    - Policy: If Stockholders' Equity ≤ 0, returns `NOT_MEANINGFUL`.

37. **Price-to-Sales - P/S (`valuation.ps`):**
    - Formula: `Market Capitalization / Revenue`
    - Inputs: `market_cap`, `revenue`
    - Unit: `MULTIPLE`

38. **Price-to-Cash-Flow - P/CF (`valuation.price_to_cash_flow`):**
    - Formula: `Market Capitalization / Operating Cash Flow`
    - Inputs: `market_cap`, `operating_cash_flow`
    - Unit: `MULTIPLE`

39. **Price-to-Free-Cash-Flow - P/FCF (`valuation.price_to_free_cash_flow`):**
    - Formula: `Market Capitalization / Free Cash Flow`
    - Inputs: `market_cap`, `free_cash_flow`
    - Unit: `MULTIPLE`
    - Policy: If FCF ≤ 0, returns `NOT_MEANINGFUL`.

40. **Enterprise Value - EV (`valuation.enterprise_value`):**
    - Formula: `Market Capitalization + Total Debt - Cash & Cash Equivalents`
    - Inputs: `market_cap`, `total_debt`, `cash_and_equivalents`
    - Unit: `MONETARY`

41. **EV/EBITDA (`valuation.ev_to_ebitda`):**
    - Formula: `Enterprise Value / EBITDA`
    - Inputs: `enterprise_value`, `ebitda`
    - Unit: `MULTIPLE`
    - Policy: If EBITDA ≤ 0, returns `NOT_MEANINGFUL`.

42. **EV/Revenue (`valuation.ev_to_revenue`):**
    - Formula: `Enterprise Value / Revenue`
    - Inputs: `enterprise_value`, `revenue`
    - Unit: `MULTIPLE`

43. **Dividend Yield (`valuation.dividend_yield`):**
    - Formula: `(Dividends Paid / Market Capitalization) * 100`
    - Inputs: `dividends_paid`, `market_cap`
    - Unit: `PERCENT`

44. **Earnings Yield (`valuation.earnings_yield`):**
    - Formula: `(Net Income / Market Capitalization) * 100`
    - Inputs: `net_income`, `market_cap`
    - Unit: `PERCENT`

---

## 4. REST API Endpoint Specifications

All endpoints require authentication (`PermissionCode.ATLAS_ACCESS`) under namespace `/api/v1/companies/{company_id}/ratios`:

1. **`GET /api/v1/companies/{company_id}/ratios/catalog`**
   - Returns all 44 registered canonical ratio definitions, versions, required inputs, output units, and policies.

2. **`GET /api/v1/companies/{company_id}/ratios`**
   - Query Parameters: `period_id` (default "FY2024"), `period_type` (default "ANNUAL"), `category` (optional filter).
   - Computes and returns qualified financial ratios with exact values, formatted values, units, status, and input facts.

3. **`GET /api/v1/companies/{company_id}/ratios/history`**
   - Query Parameters: `ratio_id` (required), `period_type` (default "ANNUAL"), `limit` (default 10).
   - Returns chronological time-series points across fiscal periods for historical trend analysis.

4. **`GET /api/v1/companies/{company_id}/ratios/{ratio_id}/methodology`**
   - Returns registered formula definition, numerator and denominator rules, and calculation notes.

5. **`GET /api/v1/companies/{company_id}/ratios/{ratio_id}/lineage`**
   - Query Parameters: `period_id` (default "FY2024").
   - Returns exact contributing accounting statement facts (concept, reported amount, currency, statement type, revision).

---

## 5. Frontend Financial Ratios Workspace

Located inside `/companies` under the dedicated "Financial Ratios" tab:
- **`FinancialRatiosWorkspace.tsx`**: Top-level workspace with Category Navigation, Period Selector (Annual/Quarterly/TTM), Search Filter, and Table.
- **`RatioTrendChart.tsx`**: SVG visual trend chart plotting historical periods with hover guidelines, point tooltips, zero baselines, min/max/avg stats, and directional trend indicators.
- **`RatioFormulaModal.tsx`**: Inspection popover displaying exact canonical formulas, numerator/denominator descriptions, institutional policies, and source fact lineage.

---

## 6. Stage Roadmap Boundaries

- **Stage 83 owns Canonical Financial Ratios.**
- **Stage 84 owns Company Earnings Analytics** (EPS surprises, consensus revisions, call transcripts, corporate guidance).
- **Stage 85 owns Company Ownership & Shareholder Structure.**
- **Stage 86 owns Regulatory Filings & EDGAR Parsers.**
- **Stage 87 owns Peer Groups & Cross-Company Benchmarking.**
- **Stage 88 owns Supply Chains & Corporate Exposure Networks.**
