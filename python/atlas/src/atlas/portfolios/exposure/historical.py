"""
Historical Allocation and Exposure Drift Engine.

Calculates time-series allocation trajectories, point-in-time exposure comparisons,
and date-to-date allocation drift (Δw = w_t2 - w_t1) across all canonical dimensions.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from atlas.portfolios.exposure.enums import (
    ExposureBasis,
    ExposureDimension,
    GeographyPolicy,
)
from atlas.portfolios.exposure.models import (
    AllocationChangeItem,
    ExposureDimensionResult,
    HistoricalAllocationPoint,
    PortfolioExposureRun,
)


class HistoricalAllocationEngine:
    """Engine for historical allocation analysis, drift calculations, and time-series snapshots."""

    @staticmethod
    def calculate_allocation_changes(
        start_result: ExposureDimensionResult,
        end_result: ExposureDimensionResult,
        start_date: date,
        end_date: date,
    ) -> List[AllocationChangeItem]:
        """
        Calculate date-to-date allocation change (Δw = w_t2 - w_t1) between two points in time.
        
        Change is reported in percentage points (start_weight, end_weight) and basis points (bps).
        All categories appearing in either start or end snapshot are included.
        """
        dimension = start_result.dimension
        start_map: Dict[str, Any] = {row.category_id: row for row in start_result.categories}
        end_map: Dict[str, Any] = {row.category_id: row for row in end_result.categories}

        all_category_ids = sorted(list(set(start_map.keys()) | set(end_map.keys())))
        changes: List[AllocationChangeItem] = []

        for cat_id in all_category_ids:
            start_row = start_map.get(cat_id)
            end_row = end_map.get(cat_id)

            label = end_row.category_label if end_row else (start_row.category_label if start_row else cat_id)
            start_weight = start_row.weight if start_row else Decimal("0.000000")
            end_weight = end_row.weight if end_row else Decimal("0.000000")
            start_val = start_row.base_value if start_row else Decimal("0.00")
            end_val = end_row.base_value if end_row else Decimal("0.00")

            weight_change = end_weight - start_weight
            weight_change_bps = int(round(weight_change * Decimal("10000")))
            value_change = end_val - start_val

            changes.append(
                AllocationChangeItem(
                    dimension=dimension,
                    category_id=cat_id,
                    category_label=label,
                    start_date=start_date,
                    end_date=end_date,
                    start_weight=start_weight,
                    end_weight=end_weight,
                    weight_change_pct=weight_change,
                    weight_change_bps=weight_change_bps,
                    start_value=start_val,
                    end_value=end_val,
                    value_change=value_change,
                )
            )

        # Sort descending by absolute weight change
        changes.sort(key=lambda x: abs(x.weight_change_pct), reverse=True)
        return changes

    @staticmethod
    def extract_time_series(
        historical_runs: List[PortfolioExposureRun],
        dimension: ExposureDimension,
    ) -> List[HistoricalAllocationPoint]:
        """
        Extract flat time-series points from a sequence of dated exposure runs for a given dimension.
        """
        points: List[HistoricalAllocationPoint] = []

        for run in sorted(historical_runs, key=lambda r: r.as_of_date):
            dim_res: Optional[ExposureDimensionResult] = None
            if dimension == ExposureDimension.ASSET_CLASS:
                dim_res = run.asset_classes
            elif dimension == ExposureDimension.SECTOR:
                dim_res = run.sectors
            elif dimension == ExposureDimension.INDUSTRY:
                dim_res = run.industries
            elif dimension == ExposureDimension.COUNTRY:
                dim_res = run.countries
            elif dimension == ExposureDimension.CURRENCY:
                dim_res = run.currencies

            if not dim_res:
                continue

            for row in dim_res.categories:
                points.append(
                    HistoricalAllocationPoint(
                        as_of_date=run.as_of_date,
                        dimension=dimension,
                        category_id=row.category_id,
                        category_label=row.category_label,
                        weight=row.weight,
                        base_value=row.base_value,
                        base_currency=run.base_currency,
                    )
                )

        return points

