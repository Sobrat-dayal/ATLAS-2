"""Pre-Trade Risk Controls and Capital Compliance (Stage 143)."""

from __future__ import annotations

from typing import Optional, Tuple


class PreTradeRiskControls:
    """Evaluates simulated orders against configured risk limits and available capital."""

    @staticmethod
    def validate_order(
        order_side: str,  # "BUY" | "SELL"
        quantity: float,
        price: float,
        current_cash: float,
        current_position_qty: float,
        max_position_size: Optional[float] = None,
        account_type: str = "MARGIN",
        max_leverage: float = 2.0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate order submission against account buying power and position caps.
        Enforces Test D (Order Rejection).
        """
        order_notional = abs(quantity) * price

        # 1. Buying Power check for opening/increasing long position
        if order_side.upper() == "BUY":
            if account_type.upper() == "CASH":
                if order_notional > current_cash:
                    return False, f"INSUFFICIENT_CASH: Required ${order_notional:.2f} > Available ${current_cash:.2f}"
            else:  # MARGIN
                max_buying_power = current_cash * max_leverage
                if order_notional > max_buying_power:
                    return False, f"INSUFFICIENT_BUYING_POWER: Required ${order_notional:.2f} > Max Margin BP ${max_buying_power:.2f}"

        # 2. Maximum Position Size Limit check
        if max_position_size is not None and max_position_size > 0:
            projected_qty = abs(current_position_qty + (quantity if order_side.upper() == "BUY" else -quantity))
            if projected_qty > max_position_size:
                return False, f"MAX_POSITION_SIZE_EXCEEDED: Projected {projected_qty} > Limit {max_position_size}"

        return True, None
