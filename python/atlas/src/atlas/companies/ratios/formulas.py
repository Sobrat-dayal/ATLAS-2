"""Deterministic Exact Decimal Formulas for Financial Ratios (Stage 83).

Rules & Invariants:
- All financial calculations use exact Python Decimal. Binary floating-point is strictly prohibited.
- Zero Denominator Protection: Returns (None, "Division by zero", RatioStatus.UNAVAILABLE).
- Negative Denominator Policy: If policy is NOT_MEANINGFUL (e.g. ROE with negative equity base,
  or P/E with non-positive earnings), returns (None, explanation, RatioStatus.NOT_MEANINGFUL).
- Never emits NaN or Infinity.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

from atlas.companies.ratios.enums import RatioStatus


def safe_divide(
    numerator: Optional[Decimal],
    denominator: Optional[Decimal],
    scale_multiplier: Decimal = Decimal("1"),
    strict_positive_denominator: bool = False,
    allow_negative_denominator: bool = True,
    not_meaningful_reason: str = "Denominator not meaningful (N/M)",
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    """Safely divides two decimals, applying exact division and zero/negative protections."""
    if numerator is None:
        return None, "Numerator missing or unavailable", RatioStatus.INSUFFICIENT_DATA
    if denominator is None:
        return None, "Denominator missing or unavailable", RatioStatus.INSUFFICIENT_DATA

    if denominator == Decimal("0"):
        return None, "Division by zero — denominator is 0", RatioStatus.UNAVAILABLE

    if strict_positive_denominator and denominator <= Decimal("0"):
        return None, not_meaningful_reason, RatioStatus.NOT_MEANINGFUL

    if not allow_negative_denominator and denominator < Decimal("0"):
        return None, not_meaningful_reason, RatioStatus.NOT_MEANINGFUL

    try:
        raw_val = (numerator / denominator) * scale_multiplier
        # Standard rounding to 6 decimal places for exact storage
        val = raw_val.quantize(Decimal("0.000001"))
        return val, None, RatioStatus.AVAILABLE
    except (InvalidOperation, ZeroDivisionError) as e:
        return None, f"Arithmetic failure: {str(e)}", RatioStatus.UNAVAILABLE


# -----------------------------------------------------------------------------
# Profitability Formulas
# -----------------------------------------------------------------------------

def calculate_gross_margin(gross_profit: Optional[Decimal], revenue: Optional[Decimal]) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        gross_profit, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base (N/M)"
    )


def calculate_operating_margin(operating_income: Optional[Decimal], revenue: Optional[Decimal]) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        operating_income, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base (N/M)"
    )


def calculate_ebitda_margin(
    operating_income: Optional[Decimal],
    depreciation_and_amortization: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if operating_income is None or depreciation_and_amortization is None:
        return None, "Operating income or D&A input unavailable for EBITDA calculation", RatioStatus.INSUFFICIENT_DATA
    ebitda = operating_income + depreciation_and_amortization
    return safe_divide(
        ebitda, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base (N/M)"
    )


def calculate_net_margin(net_income: Optional[Decimal], revenue: Optional[Decimal]) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        net_income, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base (N/M)"
    )


def calculate_roe(net_income: Optional[Decimal], average_equity: Optional[Decimal]) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        net_income, average_equity, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Negative or zero equity base (N/M)"
    )


def calculate_roa(net_income: Optional[Decimal], average_assets: Optional[Decimal]) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        net_income, average_assets, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive asset base (N/M)"
    )


def calculate_roic(
    operating_income: Optional[Decimal],
    income_tax_expense: Optional[Decimal],
    income_before_tax: Optional[Decimal],
    average_invested_capital: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if operating_income is None:
        return None, "Operating income unavailable for ROIC", RatioStatus.INSUFFICIENT_DATA
    if average_invested_capital is None:
        return None, "Invested capital unavailable for ROIC", RatioStatus.INSUFFICIENT_DATA

    # Effective tax rate calculation with bounded limits [0, 50%]
    tax_rate = Decimal("0.21")  # Standard US statutory corporate benchmark fallback
    if income_tax_expense is not None and income_before_tax is not None and income_before_tax > Decimal("0"):
        computed_rate = income_tax_expense / income_before_tax
        if Decimal("0") <= computed_rate <= Decimal("0.60"):
            tax_rate = computed_rate

    nopat = operating_income * (Decimal("1") - tax_rate)
    return safe_divide(
        nopat, average_invested_capital, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive invested capital base (N/M)"
    )


def calculate_roce(
    operating_income: Optional[Decimal],
    average_capital_employed: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        operating_income, average_capital_employed, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive capital employed base (N/M)"
    )


# -----------------------------------------------------------------------------
# Liquidity Formulas
# -----------------------------------------------------------------------------

def calculate_current_ratio(
    current_assets: Optional[Decimal],
    current_liabilities: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        current_assets, current_liabilities,
        strict_positive_denominator=True, not_meaningful_reason="Current liabilities non-positive"
    )


def calculate_quick_ratio(
    cash_and_equivalents: Optional[Decimal],
    short_term_investments: Optional[Decimal],
    accounts_receivable: Optional[Decimal],
    current_liabilities: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if current_liabilities is None:
        return None, "Current liabilities missing", RatioStatus.INSUFFICIENT_DATA
    cash = cash_and_equivalents or Decimal("0")
    st_inv = short_term_investments or Decimal("0")
    ar = accounts_receivable or Decimal("0")
    quick_assets = cash + st_inv + ar
    return safe_divide(
        quick_assets, current_liabilities,
        strict_positive_denominator=True, not_meaningful_reason="Current liabilities non-positive"
    )


def calculate_cash_ratio(
    cash_and_equivalents: Optional[Decimal],
    short_term_investments: Optional[Decimal],
    current_liabilities: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if current_liabilities is None:
        return None, "Current liabilities missing", RatioStatus.INSUFFICIENT_DATA
    cash = cash_and_equivalents or Decimal("0")
    st_inv = short_term_investments or Decimal("0")
    cash_assets = cash + st_inv
    return safe_divide(
        cash_assets, current_liabilities,
        strict_positive_denominator=True, not_meaningful_reason="Current liabilities non-positive"
    )


def calculate_operating_cash_flow_ratio(
    operating_cash_flow: Optional[Decimal],
    current_liabilities: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        operating_cash_flow, current_liabilities,
        strict_positive_denominator=True, not_meaningful_reason="Current liabilities non-positive"
    )


# -----------------------------------------------------------------------------
# Solvency & Leverage Formulas
# -----------------------------------------------------------------------------

def calculate_debt_to_equity(
    total_debt: Optional[Decimal],
    total_equity: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        total_debt, total_equity,
        strict_positive_denominator=True, not_meaningful_reason="Negative equity base (N/M)"
    )


def calculate_debt_to_assets(
    total_debt: Optional[Decimal],
    total_assets: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        total_debt, total_assets,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive asset base"
    )


def calculate_debt_to_capital(
    total_debt: Optional[Decimal],
    total_equity: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if total_debt is None or total_equity is None:
        return None, "Total debt or total equity missing", RatioStatus.INSUFFICIENT_DATA
    total_capital = total_debt + total_equity
    return safe_divide(
        total_debt, total_capital,
        strict_positive_denominator=True, not_meaningful_reason="Total capital non-positive"
    )


def calculate_net_debt(
    total_debt: Optional[Decimal],
    cash_and_equivalents: Optional[Decimal],
    short_term_investments: Optional[Decimal] = None,
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if total_debt is None:
        return None, "Total debt missing", RatioStatus.INSUFFICIENT_DATA
    cash = cash_and_equivalents or Decimal("0")
    st_inv = short_term_investments or Decimal("0")
    net_debt = total_debt - (cash + st_inv)
    return net_debt, None, RatioStatus.AVAILABLE


def calculate_interest_coverage(
    operating_income: Optional[Decimal],
    interest_expense: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if interest_expense is None:
        return None, "Interest expense unavailable", RatioStatus.INSUFFICIENT_DATA
    abs_interest = abs(interest_expense)
    if abs_interest == Decimal("0"):
        return None, "Zero interest expense — coverage undefined", RatioStatus.UNAVAILABLE
    return safe_divide(
        operating_income, abs_interest,
        strict_positive_denominator=True, not_meaningful_reason="Zero or negative interest expense"
    )


def calculate_debt_to_ebitda(
    total_debt: Optional[Decimal],
    ebitda: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        total_debt, ebitda,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive EBITDA (N/M)"
    )


def calculate_net_debt_to_ebitda(
    net_debt: Optional[Decimal],
    ebitda: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        net_debt, ebitda,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive EBITDA (N/M)"
    )


# -----------------------------------------------------------------------------
# Efficiency Formulas
# -----------------------------------------------------------------------------

def calculate_asset_turnover(
    revenue: Optional[Decimal],
    average_assets: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        revenue, average_assets,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive assets base"
    )


def calculate_inventory_turnover(
    cost_of_revenue: Optional[Decimal],
    average_inventory: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        cost_of_revenue, average_inventory,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive inventory base"
    )


def calculate_receivables_turnover(
    revenue: Optional[Decimal],
    average_receivables: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        revenue, average_receivables,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive receivables base"
    )


def calculate_payables_turnover(
    cost_of_revenue: Optional[Decimal],
    average_payables: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        cost_of_revenue, average_payables,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive payables base"
    )


def calculate_dso(
    average_receivables: Optional[Decimal],
    revenue: Optional[Decimal],
    period_days: int = 365,
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if average_receivables is None:
        return None, "Average accounts receivable missing", RatioStatus.INSUFFICIENT_DATA
    scaled_ar = average_receivables * Decimal(str(period_days))
    return safe_divide(
        scaled_ar, revenue,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_dio(
    average_inventory: Optional[Decimal],
    cost_of_revenue: Optional[Decimal],
    period_days: int = 365,
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if average_inventory is None:
        return None, "Average inventory missing", RatioStatus.INSUFFICIENT_DATA
    scaled_inv = average_inventory * Decimal(str(period_days))
    return safe_divide(
        scaled_inv, cost_of_revenue,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive cost of revenue base"
    )


def calculate_dpo(
    average_payables: Optional[Decimal],
    cost_of_revenue: Optional[Decimal],
    period_days: int = 365,
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if average_payables is None:
        return None, "Average payables missing", RatioStatus.INSUFFICIENT_DATA
    scaled_ap = average_payables * Decimal(str(period_days))
    return safe_divide(
        scaled_ap, cost_of_revenue,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive cost of revenue base"
    )


def calculate_cash_conversion_cycle(
    dso: Optional[Decimal],
    dio: Optional[Decimal],
    dpo: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if dso is None or dio is None or dpo is None:
        return None, "DSO, DIO, or DPO input missing for Cash Conversion Cycle", RatioStatus.INSUFFICIENT_DATA
    ccc = (dso + dio - dpo).quantize(Decimal("0.000001"))
    return ccc, None, RatioStatus.AVAILABLE


# -----------------------------------------------------------------------------
# Cash Flow Formulas
# -----------------------------------------------------------------------------

def calculate_free_cash_flow(
    operating_cash_flow: Optional[Decimal],
    capital_expenditures: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if operating_cash_flow is None:
        return None, "Operating cash flow unavailable", RatioStatus.INSUFFICIENT_DATA
    if capital_expenditures is None:
        return None, "Capital expenditures unavailable", RatioStatus.INSUFFICIENT_DATA

    # CapEx is usually reported as negative outflow. If negative, subtract abs or add signed.
    abs_capex = abs(capital_expenditures)
    fcf = operating_cash_flow - abs_capex
    return fcf, None, RatioStatus.AVAILABLE


def calculate_free_cash_flow_margin(
    free_cash_flow: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        free_cash_flow, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_operating_cash_flow_margin(
    operating_cash_flow: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        operating_cash_flow, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_cash_conversion(
    operating_cash_flow: Optional[Decimal],
    net_income: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        operating_cash_flow, net_income,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive net income (N/M)"
    )


def calculate_capex_to_revenue(
    capital_expenditures: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if capital_expenditures is None:
        return None, "CapEx unavailable", RatioStatus.INSUFFICIENT_DATA
    abs_capex = abs(capital_expenditures)
    return safe_divide(
        abs_capex, revenue, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_free_cash_flow_yield(
    free_cash_flow: Optional[Decimal],
    market_cap: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        free_cash_flow, market_cap, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Market capitalization non-positive"
    )


# -----------------------------------------------------------------------------
# Valuation Formulas
# -----------------------------------------------------------------------------

def calculate_pe(
    market_cap: Optional[Decimal],
    net_income: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_cap, net_income,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive net income (N/M)"
    )


def calculate_forward_pe(
    market_price: Optional[Decimal],
    forward_eps: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_price, forward_eps,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive forward EPS (N/M)"
    )


def calculate_pb(
    market_cap: Optional[Decimal],
    total_equity: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_cap, total_equity,
        strict_positive_denominator=True, not_meaningful_reason="Negative equity base (N/M)"
    )


def calculate_ps(
    market_cap: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_cap, revenue,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_price_to_cash_flow(
    market_cap: Optional[Decimal],
    operating_cash_flow: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_cap, operating_cash_flow,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive operating cash flow (N/M)"
    )


def calculate_price_to_free_cash_flow(
    market_cap: Optional[Decimal],
    free_cash_flow: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        market_cap, free_cash_flow,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive free cash flow (N/M)"
    )


def calculate_enterprise_value(
    market_cap: Optional[Decimal],
    total_debt: Optional[Decimal],
    cash_and_equivalents: Optional[Decimal],
    short_term_investments: Optional[Decimal] = None,
    preferred_stock: Optional[Decimal] = None,
    minority_interest: Optional[Decimal] = None,
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if market_cap is None:
        return None, "Market capitalization unavailable for EV calculation", RatioStatus.INSUFFICIENT_DATA
    debt = total_debt or Decimal("0")
    cash = cash_and_equivalents or Decimal("0")
    st_inv = short_term_investments or Decimal("0")
    pref = preferred_stock or Decimal("0")
    min_int = minority_interest or Decimal("0")

    ev = market_cap + debt + pref + min_int - (cash + st_inv)
    return ev, None, RatioStatus.AVAILABLE


def calculate_ev_to_ebitda(
    enterprise_value: Optional[Decimal],
    ebitda: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        enterprise_value, ebitda,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive EBITDA (N/M)"
    )


def calculate_ev_to_revenue(
    enterprise_value: Optional[Decimal],
    revenue: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        enterprise_value, revenue,
        strict_positive_denominator=True, not_meaningful_reason="Non-positive revenue base"
    )


def calculate_dividend_yield(
    dividends_paid: Optional[Decimal],
    market_cap: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    if dividends_paid is None:
        return None, "Dividends paid data unavailable", RatioStatus.INSUFFICIENT_DATA
    abs_div = abs(dividends_paid)
    return safe_divide(
        abs_div, market_cap, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Market capitalization non-positive"
    )


def calculate_earnings_yield(
    net_income: Optional[Decimal],
    market_cap: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[str], RatioStatus]:
    return safe_divide(
        net_income, market_cap, scale_multiplier=Decimal("100"),
        strict_positive_denominator=True, not_meaningful_reason="Market capitalization non-positive"
    )
