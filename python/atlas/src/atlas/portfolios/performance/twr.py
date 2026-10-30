"""Time-Weighted Return (TWR) and Modified Dietz Engine for ATLAS (Stage 111).

Implements exact subperiod segmentation around external flows to neutralize
the distorting effect of deposits and withdrawals on investment returns.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from atlas.portfolios.performance.errors import (
    PortfolioPerformanceBeginningValuationMissingError,
    PortfolioPerformanceTwrUnavailableError,
)
from atlas.portfolios.performance.models import SubperiodReturn


def calculate_exact_twr(
    period_start: datetime,
    period_end: datetime,
    beginning_value: Decimal,
    ending_value: Decimal,
    # flows_with_marks: list of (flow_timestamp, net_portfolio_flow, pre_flow_valuation)
    flows_with_marks: List[Tuple[datetime, Decimal, Decimal]],
) -> Tuple[Decimal, List[SubperiodReturn]]:
    """Calculates exact Time-Weighted Return (TWR) via geometric subperiod compounding.

    Neutralizes external contributions and withdrawals by evaluating investment
    performance immediately prior to each cash flow.
    """
    if beginning_value <= Decimal("0.00") and not flows_with_marks:
        if ending_value == Decimal("0.00"):
            return Decimal("0.00"), []
        raise PortfolioPerformanceBeginningValuationMissingError(
            "Cannot calculate TWR with zero beginning valuation and no initial external contribution"
        )

    subperiods: List[SubperiodReturn] = []
    
    # Case 1: No external flows during the measurement period
    if not flows_with_marks:
        if beginning_value <= Decimal("0.00"):
            raise PortfolioPerformanceBeginningValuationMissingError("Beginning valuation must be positive")
        sub_return = (ending_value / beginning_value) - Decimal("1.0")
        subperiods.append(
            SubperiodReturn(
                subperiod_index=1,
                start_time=period_start,
                end_time=period_end,
                start_value=beginning_value,
                end_value_pre_flow=ending_value,
                net_external_flow=Decimal("0.00"),
                end_value_post_flow=ending_value,
                subperiod_return=sub_return,
                cumulative_twr_linked=sub_return,
            )
        )
        return sub_return, subperiods

    # Case 2: One or more external cash flows require subperiod segmentation
    # Sort chronologically
    sorted_flows = sorted(flows_with_marks, key=lambda x: x[0])
    
    current_start_value = beginning_value
    current_start_time = period_start
    compounded_factor = Decimal("1.0")

    for idx, (flow_time, flow_amount, pre_flow_val) in enumerate(sorted_flows, start=1):
        # Subperiod from current_start_time to flow_time
        if current_start_value <= Decimal("0.00"):
            # If starting from zero and receiving initial funding, skip zero return step
            sub_ret = Decimal("0.00")
        else:
            sub_ret = (pre_flow_val / current_start_value) - Decimal("1.0")

        post_flow_val = pre_flow_val + flow_amount
        compounded_factor *= (Decimal("1.0") + sub_ret)
        cum_twr = compounded_factor - Decimal("1.0")

        subperiods.append(
            SubperiodReturn(
                subperiod_index=idx,
                start_time=current_start_time,
                end_time=flow_time,
                start_value=current_start_value,
                end_value_pre_flow=pre_flow_val,
                net_external_flow=flow_amount,
                end_value_post_flow=post_flow_val,
                subperiod_return=sub_ret,
                cumulative_twr_linked=cum_twr,
            )
        )

        current_start_value = post_flow_val
        current_start_time = flow_time

    # Final subperiod from last flow to period_end
    if current_start_value <= Decimal("0.00"):
        final_ret = Decimal("0.00")
    else:
        final_ret = (ending_value / current_start_value) - Decimal("1.0")

    compounded_factor *= (Decimal("1.0") + final_ret)
    total_twr = compounded_factor - Decimal("1.0")

    subperiods.append(
        SubperiodReturn(
            subperiod_index=len(sorted_flows) + 1,
            start_time=current_start_time,
            end_time=period_end,
            start_value=current_start_value,
            end_value_pre_flow=ending_value,
            net_external_flow=Decimal("0.00"),
            end_value_post_flow=ending_value,
            subperiod_return=final_ret,
            cumulative_twr_linked=total_twr,
        )
    )

    return total_twr, subperiods


def calculate_modified_dietz(
    period_start: datetime,
    period_end: datetime,
    beginning_value: Decimal,
    ending_value: Decimal,
    # flows: list of (flow_timestamp, net_portfolio_flow)
    flows: List[Tuple[datetime, Decimal]],
) -> Optional[Decimal]:
    """Calculates approximate time-weighted return using the Modified Dietz formula.

    Formula:
        R_MD = (V_E - V_B - Sum(F_i)) / (V_B + Sum(W_i * F_i))
    where:
        W_i = (T_end - t_i) / (T_end - T_start)
    """
    total_seconds = (period_end - period_start).total_seconds()
    if total_seconds <= 0:
        return None

    sum_flows = sum((f[1] for f in flows), Decimal("0.00"))
    weighted_flows = Decimal("0.00")

    for flow_time, flow_amount in flows:
        remaining_seconds = (period_end - flow_time).total_seconds()
        weight = Decimal(str(max(0.0, min(1.0, remaining_seconds / total_seconds))))
        weighted_flows += weight * flow_amount

    denominator = beginning_value + weighted_flows
    if denominator <= Decimal("0.00"):
        return None

    numerator = ending_value - beginning_value - sum_flows
    return numerator / denominator

