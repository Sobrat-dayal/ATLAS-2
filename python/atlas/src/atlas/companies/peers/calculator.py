"""Statistical Benchmark and Relative Metrics Engine (Stage 87).

Computes cross-sectional peer medians, means, min/max bounds, sample counts,
coverage ratios, percentiles, relative differences, and outlier detection
with strict decimal precision, non-zero denominator safety, and zero silent data loss.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Tuple

from .enums import (
    ComparisonMetricCategory,
    MetricObservationStatus,
    OutlierPolicy,
    SubjectInclusionPolicy,
)
from .models import ComparableMetricObservation, PeerBenchmarkStatistics


def _quantize_decimal(val: Decimal, places: int = 2) -> Decimal:
    """Helper to round Decimal values cleanly."""
    return val.quantize(Decimal("10") ** -places, rounding=ROUND_HALF_UP)


def calculate_median(values: List[Decimal]) -> Optional[Decimal]:
    """Computes exact median over a sorted list of Decimal values."""
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return sorted_vals[mid]
    else:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / Decimal("2")


def calculate_percentiles(values: List[Decimal]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    """Calculates Q1 (25th percentile) and Q3 (75th percentile) for outlier analysis."""
    if len(values) < 4:
        return None, None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    # Simple linear interpolation for quartiles
    q1_idx = int(n * 0.25)
    q3_idx = int(n * 0.75)
    return sorted_vals[q1_idx], sorted_vals[q3_idx]


def calculate_peer_statistics(
    observations: List[ComparableMetricObservation],
    subject_id: str,
    outlier_policy: OutlierPolicy = OutlierPolicy.ALL_VALID_VALUES,
    subject_policy: SubjectInclusionPolicy = SubjectInclusionPolicy.EXCLUDE_SUBJECT,
) -> PeerBenchmarkStatistics:
    """Computes robust cross-sectional benchmark statistics for a group of observations."""
    if not observations:
        return PeerBenchmarkStatistics(
            metric_id="unknown",
            metric_name="Unknown",
            category=ComparisonMetricCategory.PROFITABILITY,
            unit="%",
        )

    first = observations[0]
    metric_id = first.metric_id
    metric_name = first.metric_name
    category = first.category
    unit = first.unit

    total_count = len(observations)
    subject_obs = next((obs for obs in observations if obs.company_id == subject_id), None)
    subject_val = (
        subject_obs.exact_value
        if (subject_obs and subject_obs.status == MetricObservationStatus.AVAILABLE)
        else None
    )

    # Filter eligible observations
    eligible_obs = [
        obs
        for obs in observations
        if obs.status == MetricObservationStatus.AVAILABLE and obs.exact_value is not None
    ]

    # Benchmark pool selection (peer-only vs including subject)
    if subject_policy == SubjectInclusionPolicy.EXCLUDE_SUBJECT:
        benchmark_pool = [obs for obs in eligible_obs if obs.company_id != subject_id]
    else:
        benchmark_pool = list(eligible_obs)

    sample_count = len(benchmark_pool)
    coverage_ratio = round(
        sample_count
        / max(
            total_count - (1 if subject_policy == SubjectInclusionPolicy.EXCLUDE_SUBJECT else 0), 1
        ),
        2,
    )

    if sample_count == 0:
        return PeerBenchmarkStatistics(
            metric_id=metric_id,
            metric_name=metric_name,
            category=category,
            unit=unit,
            total_count=total_count,
            sample_count=0,
            coverage_ratio=0.0,
            subject_value=subject_val,
        )

    # Detect outliers via IQR method
    raw_vals = [obs.exact_value for obs in benchmark_pool if obs.exact_value is not None]
    q1, q3 = calculate_percentiles(raw_vals)
    outliers: List[str] = []

    if q1 is not None and q3 is not None:
        iqr = q3 - q1
        lower_bound = q1 - (Decimal("1.5") * iqr)
        upper_bound = q3 + (Decimal("1.5") * iqr)
        for obs in benchmark_pool:
            if obs.exact_value is not None and (
                obs.exact_value < lower_bound or obs.exact_value > upper_bound
            ):
                outliers.append(obs.company_id)

    # If requested, filter outliers for median/mean computation
    if outlier_policy == OutlierPolicy.EXCLUDE_SELECTED_OUTLIERS and outliers:
        calc_pool = [
            obs.exact_value
            for obs in benchmark_pool
            if obs.company_id not in outliers and obs.exact_value is not None
        ]
        if not calc_pool:  # Fallback if all were flagged
            calc_pool = raw_vals
    else:
        calc_pool = raw_vals

    mean_val = _quantize_decimal(sum(calc_pool) / Decimal(str(len(calc_pool))))
    median_val = _quantize_decimal(calculate_median(calc_pool) or Decimal("0"))
    min_val = min(calc_pool)
    max_val = max(calc_pool)

    # Subject relative difference vs peer median
    diff_pct: Optional[Decimal] = None
    diff_pp: Optional[Decimal] = None
    percentile: Optional[Decimal] = None

    if subject_val is not None and median_val is not None:
        if median_val != Decimal("0"):
            diff_pct = _quantize_decimal(
                ((subject_val - median_val) / abs(median_val)) * Decimal("100")
            )
        diff_pp = _quantize_decimal(subject_val - median_val)

        # Percentile rank in the overall pool
        all_eligible_vals = sorted(
            [obs.exact_value for obs in eligible_obs if obs.exact_value is not None]
        )
        if all_eligible_vals:
            strictly_below = sum(1 for v in all_eligible_vals if v < subject_val)
            equal_to = sum(1 for v in all_eligible_vals if v == subject_val)
            rank = Decimal(str(strictly_below)) + (Decimal(str(equal_to)) * Decimal("0.5"))
            percentile = _quantize_decimal(
                (rank / Decimal(str(len(all_eligible_vals)))) * Decimal("100")
            )

    return PeerBenchmarkStatistics(
        metric_id=metric_id,
        metric_name=metric_name,
        category=category,
        unit=unit,
        mean=mean_val,
        median=median_val,
        min_value=min_val,
        max_value=max_val,
        sample_count=sample_count,
        total_count=total_count,
        coverage_ratio=coverage_ratio,
        subject_value=subject_val,
        subject_diff_vs_median_pct=diff_pct,
        subject_diff_vs_median_pp=diff_pp,
        subject_percentile=percentile,
        outliers_detected=outliers,
    )
