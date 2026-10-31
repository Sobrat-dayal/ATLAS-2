"""Slippage Simulation Models (Stage 143)."""

from __future__ import annotations

from atlas.trading.backtesting.domain import SlippagePolicy


class SimulatedSlippageEngine:
    """Calculates adverse execution price impact and slippage costs."""

    @staticmethod
    def calculate_adjusted_price(
        order_side: str,  # "BUY" | "SELL"
        base_price: float,
        policy: SlippagePolicy,
        slippage_value: float,
        tick_size: float = 0.01,
        order_quantity: float = 1.0,
        bar_volume: float = 1000.0,
    ) -> tuple[float, float]:
        """
        Adjust execution price adversely for simulated slippage.
        Returns (adjusted_price, slippage_cost_per_unit).
        Enforces Test C.
        """
        if policy == SlippagePolicy.NONE or slippage_value <= 0:
            return base_price, 0.0

        adverse_delta = 0.0

        if policy == SlippagePolicy.FIXED_TICKS:
            adverse_delta = slippage_value * tick_size
        elif policy == SlippagePolicy.FIXED_BPS:
            # 1 bp = 0.0001
            adverse_delta = base_price * (slippage_value * 0.0001)
        elif policy == SlippagePolicy.VOLUME_WEIGHTED:
            # Impact scales linearly with participation rate
            participation = min(1.0, order_quantity / max(1.0, bar_volume))
            adverse_delta = base_price * 0.01 * participation * slippage_value

        if order_side.upper() == "BUY":
            adjusted_price = round(base_price + adverse_delta, 4)
        else:
            adjusted_price = round(max(0.01, base_price - adverse_delta), 4)

        return adjusted_price, adverse_delta
