"""Spatial Metric Registry and Numeric Aggregation Rules (Stage 131).

Defines canonical metric definitions, per-metric aggregation eligibility,
null value policies, financial precision safeguards, and distinct count rules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from atlas.maps.analytics.domain import (
    NullValuePolicy,
    SpatialAggregationMethod,
    SpatialMetricDefinition,
)
from atlas.maps.analytics.errors import SpatialMetricNotAllowedError


class SpatialMetricRegistry:
    """In-memory registry of approved analytical spatial metrics."""

    def __init__(self):
        self._metrics: Dict[str, SpatialMetricDefinition] = {}
        self._register_canonical_metrics()

    def _register_canonical_metrics(self) -> None:
        """Registers canonical institutional metrics for Stage 129 datasets."""
        # Generic observation count
        self.register(
            SpatialMetricDefinition(
                metric_id="observation_count",
                dataset_id="financial_centers_global",
                display_name="Observation Count",
                description="Raw frequency count of verified geographic observations.",
                unit="observations",
                value_type="integer",
                allowed_aggregations=[
                    SpatialAggregationMethod.COUNT,
                    SpatialAggregationMethod.DENSITY,
                ],
                default_aggregation=SpatialAggregationMethod.COUNT,
                minimum_contributor_threshold=1,
            )
        )

        # Financial market capital intensity
        self.register(
            SpatialMetricDefinition(
                metric_id="market_capital_intensity",
                dataset_id="financial_centers_global",
                display_name="Capital Intensity",
                description="Aggregated monetary capital volume in financial centers.",
                unit="USD",
                value_type="currency",
                currency="USD",
                allowed_aggregations=[
                    SpatialAggregationMethod.SUM,
                    SpatialAggregationMethod.MEAN,
                    SpatialAggregationMethod.WEIGHTED_MEAN,
                    SpatialAggregationMethod.DENSITY,
                ],
                default_aggregation=SpatialAggregationMethod.SUM,
                weight_metric_id="trading_volume_weight",
                null_policy=NullValuePolicy.EXCLUDE,
                minimum_contributor_threshold=3,
                is_temporal=True,
            )
        )

        # Distinct financial entity count
        self.register(
            SpatialMetricDefinition(
                metric_id="distinct_entities",
                dataset_id="financial_centers_global",
                display_name="Distinct Financial Entities",
                description="Count of unique financial institutions / monetary entities.",
                unit="institutions",
                value_type="integer",
                allowed_aggregations=[
                    SpatialAggregationMethod.DISTINCT_COUNT,
                    SpatialAggregationMethod.COUNT,
                ],
                default_aggregation=SpatialAggregationMethod.DISTINCT_COUNT,
                minimum_contributor_threshold=3,
            )
        )

        # Monetary liquidity score
        self.register(
            SpatialMetricDefinition(
                metric_id="liquidity_score",
                dataset_id="financial_centers_global",
                display_name="Liquidity Score",
                description="Normalized monetary market liquidity index [0-100].",
                unit="score",
                value_type="float",
                allowed_aggregations=[
                    SpatialAggregationMethod.MEAN,
                    SpatialAggregationMethod.WEIGHTED_MEAN,
                ],
                default_aggregation=SpatialAggregationMethod.MEAN,
                null_policy=NullValuePolicy.EXCLUDE,
                minimum_contributor_threshold=5,
            )
        )

    def register(self, metric: SpatialMetricDefinition) -> None:
        self._metrics[metric.metric_id] = metric

    def get(self, metric_id: str) -> Optional[SpatialMetricDefinition]:
        return self._metrics.get(metric_id)

    def list_for_dataset(self, dataset_id: str) -> List[SpatialMetricDefinition]:
        return [m for m in self._metrics.values() if m.dataset_id == dataset_id]

    def validate_query(
        self,
        dataset_id: str,
        metric_id: str,
        aggregation: SpatialAggregationMethod,
    ) -> SpatialMetricDefinition:
        """Validates that a metric exists for the dataset and permits the requested aggregation."""
        metric = self.get(metric_id)
        if not metric:
            raise SpatialMetricNotAllowedError(
                metric_id, dataset_id, "Metric not found in registry."
            )

        if metric.dataset_id != dataset_id:
            raise SpatialMetricNotAllowedError(
                metric_id,
                dataset_id,
                f"Metric is registered under dataset '{metric.dataset_id}', not '{dataset_id}'.",
            )

        if not metric.supports_aggregation(aggregation):
            raise SpatialMetricNotAllowedError(
                metric_id,
                dataset_id,
                f"Aggregation method '{aggregation.value}' is not permitted for metric '{metric_id}'. "
                f"Allowed: {[a.value for a in metric.allowed_aggregations]}",
            )

        return metric


def compute_metric_aggregation(
    values: List[Optional[float]],
    aggregation: SpatialAggregationMethod,
    null_policy: NullValuePolicy = NullValuePolicy.EXCLUDE,
    weights: Optional[List[Optional[float]]] = None,
    distinct_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Computes aggregate value and counts adhering to strict null and precision policies.

    Handles:
    - Fixture H: Count vs Distinct Count
    - Fixture I: Missing Values (Value 0, NULL, 10 -> count=2, sum=10, mean=5)
    """
    total_records = len(values)

    # Filter nulls according to policy
    valid_pairs: List[tuple[float, float]] = []  # (value, weight)
    for idx, v in enumerate(values):
        w = 1.0
        if weights and idx < len(weights) and weights[idx] is not None:
            w = float(weights[idx])

        if v is None:
            if null_policy == NullValuePolicy.ZERO:
                valid_pairs.append((0.0, w))
            # if EXCLUDE, simply skip
        else:
            valid_pairs.append((float(v), w))

    non_null_count = len(valid_pairs)

    if aggregation == SpatialAggregationMethod.COUNT:
        return {
            "value": float(total_records),
            "record_count": total_records,
            "non_null_count": non_null_count,
            "distinct_count": len(set(distinct_ids)) if distinct_ids else None,
            "valid_weight_sum": None,
        }

    if aggregation == SpatialAggregationMethod.DISTINCT_COUNT:
        distinct_count = len(set(distinct_ids)) if distinct_ids else 0
        return {
            "value": float(distinct_count),
            "record_count": total_records,
            "non_null_count": non_null_count,
            "distinct_count": distinct_count,
            "valid_weight_sum": None,
        }

    if non_null_count == 0:
        return {
            "value": 0.0,
            "record_count": total_records,
            "non_null_count": 0,
            "distinct_count": 0,
            "valid_weight_sum": 0.0,
        }

    if aggregation == SpatialAggregationMethod.SUM:
        sum_val = sum(pair[0] for pair in valid_pairs)
        return {
            "value": sum_val,
            "record_count": total_records,
            "non_null_count": non_null_count,
            "distinct_count": len(set(distinct_ids)) if distinct_ids else None,
            "valid_weight_sum": None,
        }

    if aggregation == SpatialAggregationMethod.MEAN:
        sum_val = sum(pair[0] for pair in valid_pairs)
        return {
            "value": sum_val / non_null_count,
            "record_count": total_records,
            "non_null_count": non_null_count,
            "distinct_count": len(set(distinct_ids)) if distinct_ids else None,
            "valid_weight_sum": None,
        }

    if aggregation == SpatialAggregationMethod.WEIGHTED_MEAN:
        total_weight = sum(pair[1] for pair in valid_pairs)
        if total_weight > 0:
            weighted_sum = sum(pair[0] * pair[1] for pair in valid_pairs)
            val = weighted_sum / total_weight
        else:
            val = 0.0
        return {
            "value": val,
            "record_count": total_records,
            "non_null_count": non_null_count,
            "distinct_count": len(set(distinct_ids)) if distinct_ids else None,
            "valid_weight_sum": total_weight,
        }

    # Default fallback
    return {
        "value": float(total_records),
        "record_count": total_records,
        "non_null_count": non_null_count,
        "distinct_count": len(set(distinct_ids)) if distinct_ids else None,
        "valid_weight_sum": None,
    }
