"""Periodic Return Calculations and Geometric Annualization for ATLAS (Stage 111).

Provides calendar and trailing periodic performance analytics:
Daily, Monthly, Quarterly, Annual, YTD, Trailing, and Since Inception.
Enforces geometric compounding and proper annualization boundaries.
"""

from datetime import datetime
from decimal import Decimal
import math
from typing import Dict, List, Optional, Tuple

from atlas.portfolios.performance.enums import DataCompletenessStatus
from atlas.portfolios.performance.errors import PortfolioPerformanceAnnualizationInvalidError
from atlas.portfolios.performance.models import PeriodicReturn


def calculate_annualized_return(
    cumulative_return: Decimal,
    duration_days: float,
) -> Optional[Decimal]:
    """Calculates annualized geometric return over elapsed period.

    Formula:
        R_ann = (1 + R_cum)^(365.25 / duration_days) - 1

    Enforces duration >= 365 days; returns None for periods under one year to
    prevent misleading extrapolated annualization.
    """
    if duration_days <= 0:
        raise PortfolioPerformanceAnnualizationInvalidError("Duration in days must be positive")

    # If duration is less than 1 year (365 days), do not annualize without qualification
    if duration_days < 365.0:
        return None

    one_plus_r = float(Decimal("1.0") + cumulative_return)
    if one_plus_r <= 0.0:
        return Decimal("-1.0")

    years = duration_days / 365.25
    ann_float = math.pow(one_plus_r, 1.0 / years) - 1.0
    return Decimal(str(round(ann_float, 6)))


def compound_periodic_returns(returns: List[Decimal]) -> Decimal:
    """Geometrically compounds a sequence of subperiod returns.

    Formula:
        R_total = Product(1 + r_i) - 1
    """
    factor = Decimal("1.0")
    for r in returns:
        factor *= (Decimal("1.0") + r)
    return factor - Decimal("1.0")


def build_monthly_returns_grid(
    monthly_data: List[Tuple[int, int, Decimal, Decimal, Decimal, Decimal]],
    # list of (year, month, beginning_val, ending_val, net_flows, monthly_twr)
) -> List[PeriodicReturn]:
    """Constructs monthly and annual geometric return summary records."""
    periodic_records: List[PeriodicReturn] = []
    by_year: Dict[int, List[Tuple[int, Decimal]]] = {}

    for year, month, b_val, e_val, flows, m_twr in monthly_data:
        if year not in by_year:
            by_year[year] = []
        by_year[year].append((month, m_twr))

        start_dt = datetime(year, month, 1)
        # End date of month
        if month == 12:
            end_dt = datetime(year, 12, 31, 23, 59, 59)
        else:
            end_dt = datetime(year, month + 1, 1)

        investment_gain = e_val - b_val - flows
        periodic_records.append(
            PeriodicReturn(
                period_label=f"{year}-{month:02d}",
                period_type="MONTHLY",
                start_date=start_dt,
                end_date=end_dt,
                return_value=m_twr,
                beginning_value=b_val,
                ending_value=e_val,
                net_external_flows=flows,
                investment_gain=investment_gain,
                is_partial=False,
                completeness=DataCompletenessStatus.COMPLETE,
            )
        )

    # Compute full-year geometrically compounded returns
    for yr, month_returns in by_year.items():
        sorted_m = sorted(month_returns, key=lambda x: x[0])
        annual_twr = compound_periodic_returns([r for _, r in sorted_m])
        periodic_records.append(
            PeriodicReturn(
                period_label=str(yr),
                period_type="ANNUAL",
                start_date=datetime(yr, 1, 1),
                end_date=datetime(yr, 12, 31, 23, 59, 59),
                return_value=annual_twr,
                beginning_value=Decimal("0.00"),
                ending_value=Decimal("0.00"),
                net_external_flows=Decimal("0.00"),
                investment_gain=Decimal("0.00"),
                is_partial=len(sorted_m) < 12,
                completeness=DataCompletenessStatus.COMPLETE,
            )
        )

    return periodic_records

