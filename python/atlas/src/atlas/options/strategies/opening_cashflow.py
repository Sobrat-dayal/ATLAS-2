"""Strategy Opening Cash Flow and Premium Calculations (Stage 141).

Signed cash flow convention:
- Long options pay premium (negative cash flow / debit)
- Short options receive premium (positive cash flow / credit)
- Net cash flow = Sum of leg cash flows minus estimated transaction fees
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from atlas.options.domain import LegSide, OptionStrategyLeg


def calculate_opening_cash_flow(legs: List[OptionStrategyLeg]) -> Dict[str, Any]:
    """Calculate signed opening cash flow, net debit/credit, and estimated fees."""
    total_cash_flow = 0.0
    total_fees = 0.0

    for leg in legs:
        leg_premium_total = leg.quantity * leg.multiplier * leg.entry_premium
        fee = getattr(leg, "estimated_fee", 0.0) or getattr(leg, "custom_fee", 0.0)
        total_fees += fee

        if leg.side in (LegSide.LONG_CALL, LegSide.LONG_PUT):
            # Debit: cash outflow
            total_cash_flow -= leg_premium_total
        else:
            # Credit: cash inflow
            total_cash_flow += leg_premium_total

    # Fees further reduce cash received or increase cash paid
    net_flow_after_fees = round(total_cash_flow - total_fees, 2)
    is_net_debit = net_flow_after_fees < 0.0

    return {
        "net_opening_cash_flow": net_flow_after_fees,
        "is_net_debit": is_net_debit,
        "total_estimated_fees": round(total_fees, 2),
        "gross_premium_cash_flow": round(total_cash_flow, 2),
    }
