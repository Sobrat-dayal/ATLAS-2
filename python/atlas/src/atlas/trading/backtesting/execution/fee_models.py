"""Transaction Cost and Fee Models for Simulated Execution (Stage 143)."""

from __future__ import annotations

from typing import Optional
from atlas.trading.backtesting.domain import FeeModelType


class SimulatedFeeEngine:
    """Calculates realistic transaction costs, exchange fees, and commissions."""

    @staticmethod
    def calculate_commission(
        fee_model: FeeModelType,
        quantity: float,
        price: float,
        is_option: bool = False,
        commission_rate: Optional[float] = None,
        min_commission: float = 1.0,
    ) -> float:
        """
        Calculate total commission for a simulated fill.
        Enforces Test B: Gross Profit = $100, Commission = $12 -> Net Profit = $88.
        """
        if fee_model == FeeModelType.ZERO_FEE:
            return 0.0

        qty = abs(quantity)
        rate = commission_rate if commission_rate is not None else (0.65 if is_option else 0.005)

        if fee_model == FeeModelType.PER_CONTRACT:
            return round(max(min_commission, qty * rate), 2)
        elif fee_model == FeeModelType.PER_SHARE:
            return round(max(min_commission, qty * rate), 2)
        elif fee_model == FeeModelType.PERCENTAGE:
            notional = qty * price
            return round(notional * (rate / 100.0), 2)
        elif fee_model == FeeModelType.MAKER_TAKER:
            # Standard taker fee: 10 bps
            notional = qty * price
            return round(notional * 0.001, 2)

        return 0.0
