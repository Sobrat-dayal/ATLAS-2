"""Institutional Research Analysis, Calculations & Engine Package (Stage 106)."""

from atlas.research.analysis.calculations import (
    SafeExpressionEvaluator,
    calculate_mean,
    calculate_median,
    calculate_pearson_correlation,
    calculate_quartiles,
    calculate_standard_deviation,
    compute_absolute_change,
    compute_cagr,
    compute_percentage_growth,
    quantize_value,
)
from atlas.research.analysis.engine import (
    CANONICAL_COMPANY_FUNDAMENTALS,
    CANONICAL_MACRO_SERIES,
    CANONICAL_PEER_GROUPS,
    ResearchAnalysisEngine,
)

__all__ = [
    "SafeExpressionEvaluator",
    "calculate_mean",
    "calculate_median",
    "calculate_pearson_correlation",
    "calculate_quartiles",
    "calculate_standard_deviation",
    "compute_absolute_change",
    "compute_cagr",
    "compute_percentage_growth",
    "quantize_value",
    "ResearchAnalysisEngine",
    "CANONICAL_COMPANY_FUNDAMENTALS",
    "CANONICAL_PEER_GROUPS",
    "CANONICAL_MACRO_SERIES",
]
