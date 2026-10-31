"""Calculations module for financial exposure engine."""

from atlas.exposure.calculations.fx import convert_currency_point_in_time
from atlas.exposure.calculations.periods import verify_period_compatibility
from atlas.exposure.calculations.consolidation import calculate_group_consolidated_revenue
from atlas.exposure.calculations.portfolio import calculate_portfolio_exposures, PortfolioPosition, PortfolioSummary
from atlas.exposure.calculations.lookthrough import calculate_fund_lookthrough, FundConstituentEdge
from atlas.exposure.calculations.scenarios import (
    evaluate_position_scenario_shocks,
    calculate_dv01_sensitivity,
    calculate_option_delta_equivalent
)

__all__ = [
    "convert_currency_point_in_time",
    "verify_period_compatibility",
    "calculate_group_consolidated_revenue",
    "calculate_portfolio_exposures",
    "PortfolioPosition",
    "PortfolioSummary",
    "calculate_fund_lookthrough",
    "FundConstituentEdge",
    "evaluate_position_scenario_shocks",
    "calculate_dv01_sensitivity",
    "calculate_option_delta_equivalent",
]

