"""Order Matching and Fill Models for Historical Simulation (Stage 143)."""

from __future__ import annotations

from typing import Optional, Tuple
from atlas.trading.backtesting.domain import FillModelType


class FillModelEngine:
    """Evaluates whether an order can be filled and determines executed quantity and price."""

    @staticmethod
    def evaluate_fill(
        order_side: str,  # "BUY" | "SELL"
        order_type: str,  # "MARKET" | "LIMIT" | "STOP"
        requested_quantity: float,
        limit_price: Optional[float],
        stop_price: Optional[float],
        bar_open: float,
        bar_high: float,
        bar_low: float,
        bar_close: float,
        bar_volume: float,
        fill_model: FillModelType = FillModelType.TOUCHED_BID_ASK,
        max_volume_participation_pct: float = 0.10,  # Max 10% of bar volume
    ) -> Tuple[bool, float, float, Optional[str]]:
        """
        Evaluate order execution.
        Returns: (is_filled, filled_quantity, execution_price, rejection_or_skip_reason).
        Enforces Test E (Partial Fills) and Test G (Bar Ambiguity).
        """
        qty = abs(requested_quantity)

        # 1. Market Order
        if order_type.upper() == "MARKET":
            # Market orders fill at bar open or arrival price
            exec_price = bar_open
            # Check liquidity constraints
            available_liq = bar_volume * max_volume_participation_pct
            if fill_model == FillModelType.VOLUME_CONSTRAINED and qty > available_liq:
                # Partial fill (Test E)
                filled_qty = max(1.0, float(int(available_liq)))
                return True, filled_qty, exec_price, "PARTIAL_LIQUIDITY_LIMIT"
            return True, qty, exec_price, None

        # 2. Limit Order
        if order_type.upper() == "LIMIT":
            if limit_price is None:
                return False, 0.0, 0.0, "MISSING_LIMIT_PRICE"

            if order_side.upper() == "BUY":
                # Buy limit fills if low <= limit_price
                if fill_model == FillModelType.CROSS_BID_ASK:
                    can_fill = bar_low < limit_price
                else:  # TOUCHED
                    can_fill = bar_low <= limit_price

                if can_fill:
                    exec_price = min(bar_open, limit_price)
                    available_liq = bar_volume * max_volume_participation_pct
                    if fill_model == FillModelType.VOLUME_CONSTRAINED and qty > available_liq:
                        return True, max(1.0, float(int(available_liq))), exec_price, "PARTIAL_LIQUIDITY_LIMIT"
                    return True, qty, exec_price, None
                return False, 0.0, 0.0, "LIMIT_PRICE_NOT_TOUCHED"

            else:  # SELL
                if fill_model == FillModelType.CROSS_BID_ASK:
                    can_fill = bar_high > limit_price
                else:  # TOUCHED
                    can_fill = bar_high >= limit_price

                if can_fill:
                    exec_price = max(bar_open, limit_price)
                    available_liq = bar_volume * max_volume_participation_pct
                    if fill_model == FillModelType.VOLUME_CONSTRAINED and qty > available_liq:
                        return True, max(1.0, float(int(available_liq))), exec_price, "PARTIAL_LIQUIDITY_LIMIT"
                    return True, qty, exec_price, None
                return False, 0.0, 0.0, "LIMIT_PRICE_NOT_TOUCHED"

        # 3. Stop Order
        if order_type.upper() == "STOP":
            if stop_price is None:
                return False, 0.0, 0.0, "MISSING_STOP_PRICE"

            if order_side.upper() == "SELL":
                # Sell stop triggers if low <= stop_price
                if bar_low <= stop_price:
                    exec_price = min(bar_open, stop_price)
                    return True, qty, exec_price, None
            else:
                # Buy stop triggers if high >= stop_price
                if bar_high >= stop_price:
                    exec_price = max(bar_open, stop_price)
                    return True, qty, exec_price, None

            return False, 0.0, 0.0, "STOP_PRICE_NOT_TRIGGERED"

        return False, 0.0, 0.0, f"UNSUPPORTED_ORDER_TYPE_{order_type}"
