"""Data Quality Validation and Pre-Flight Checks for Historical Backtesting (Stage 143)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from atlas.trading.backtesting.domain import HistoricalDatasetManifest
from atlas.trading.backtesting.errors import (
    BacktestDatasetIneligibleError,
    BacktestLookAheadError,
)


class DataQualityValidator:
    """Pre-flight dataset validation engine ensuring clean historical data inputs."""

    @staticmethod
    def validate_price_records(
        records: List[Dict[str, Any]],
        symbol: str,
        max_gap_days: int = 7,
    ) -> List[str]:
        """Validate bar/tick sequence, returning quality warning strings."""
        warnings: List[str] = []
        if not records:
            raise BacktestDatasetIneligibleError(
                dataset_id=symbol,
                reason="Dataset contains zero records.",
            )

        last_date: Optional[str] = None
        for i, rec in enumerate(records):
            # Check price validity
            for p_field in ["open", "high", "low", "close"]:
                if p_field in rec and float(rec[p_field]) <= 0:
                    raise BacktestDatasetIneligibleError(
                        dataset_id=symbol,
                        reason=f"Non-positive price encountered on {rec.get('date')}: {p_field}={rec[p_field]}.",
                    )

            # High/Low logic check
            if "high" in rec and "low" in rec:
                h = float(rec["high"])
                l = float(rec["low"])
                if h < l:
                    raise BacktestDatasetIneligibleError(
                        dataset_id=symbol,
                        reason=f"Invalid OHLC bar: High {h} < Low {l} on {rec.get('date')}.",
                    )

        return warnings

    @staticmethod
    def validate_survivorship_bias_policy(
        manifest: HistoricalDatasetManifest,
        strategy_requests_all_listed: bool = True,
    ) -> None:
        """
        Enforce Rule XVIII & Test H:
        Historical equity strategies must not filter out companies that delisted after the test period.
        """
        if strategy_requests_all_listed and not manifest.is_delisted_inclusive:
            raise BacktestDatasetIneligibleError(
                dataset_id=manifest.dataset_id,
                reason=(
                    "Dataset suffers from survivorship bias (excludes delisted companies). "
                    "Unbiased institutional backtesting requires delisted-inclusive point-in-time constituent data."
                ),
            )
