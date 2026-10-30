"""ATLAS Financial Risk Foundation — Multi-Currency Risk Engine (Stage 115).

Calculates foreign exchange return adjustments, local vs base currency return volatility,
and unhedged foreign cash risk.
"""

from typing import Dict, List, Optional, Tuple
from .volatility import HistoricalVolatilityEngine


class MultiCurrencyRiskEngine:
    """Manages currency translations, exchange rate volatility, and base-currency returns."""

    @staticmethod
    def compose_base_return(r_local: float, r_fx: float) -> float:
        """Composes base currency return from local return and FX movement.

        Formula:
            1 + R_base = (1 + R_local) * (1 + R_FX)
            R_base = R_local + R_FX + (R_local * R_FX)
        """
        return (1.0 + r_local) * (1.0 + r_fx) - 1.0

    @staticmethod
    def convert_return_series_to_base(
        local_returns: List[float],
        fx_returns: List[float],
    ) -> List[float]:
        """Converts an entire local return series to base currency using aligned FX returns."""
        if len(local_returns) != len(fx_returns):
            return local_returns

        return [
            MultiCurrencyRiskEngine.compose_base_return(r_l, r_fx)
            for r_l, r_fx in zip(local_returns, fx_returns)
        ]

    @staticmethod
    def compute_currency_volatility(
        fx_returns: List[float],
        annualization_factor: float = 252.0,
    ) -> float:
        """Computes annualized realized volatility of the exchange rate return series."""
        if len(fx_returns) < 2:
            return 0.0
        _, _, ann_vol = HistoricalVolatilityEngine.compute_realized_volatility(
            fx_returns, annualization_factor=annualization_factor
        )
        return ann_vol

