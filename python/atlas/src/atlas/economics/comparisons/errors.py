"""Domain Exceptions for Macroeconomic Comparisons & Benchmarking (Stage 93)."""

from typing import List


class MacroComparisonError(Exception):
    """Base exception for all Macroeconomic Comparison operations."""
    def __init__(self, message: str, code: str = "MACRO_COMPARISON_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class MacroComparisonInvalidGeographyError(MacroComparisonError):
    """Raised when an unverified or unknown geography ID is requested."""
    def __init__(self, geography_id: str):
        super().__init__(
            f"Geographic Entity '{geography_id}' is not recognized or not available for comparison.",
            code="MACRO_COMPARISON_INVALID_GEOGRAPHY",
        )
        self.geography_id = geography_id


class MacroComparisonIndicatorUnavailableError(MacroComparisonError):
    """Raised when a comparison metric is not available for a requested country."""
    def __init__(self, metric_name: str, geography_id: str):
        super().__init__(
            f"Metric '{metric_name}' is not published or unavailable for country '{geography_id}'.",
            code="MACRO_COMPARISON_INDICATOR_UNAVAILABLE",
        )
        self.metric_name = metric_name
        self.geography_id = geography_id


class MacroComparisonUnitIncompatibleError(MacroComparisonError):
    """Raised when an invalid mathematical comparison is attempted across incompatible units."""
    def __init__(self, metric_a: str, unit_a: str, metric_b: str, unit_b: str):
        super().__init__(
            f"Cannot compare '{metric_a}' ({unit_a}) with '{metric_b}' ({unit_b}) without valid conversion.",
            code="MACRO_COMPARISON_UNIT_INCOMPATIBLE",
        )
        self.metric_a = metric_a
        self.unit_a = unit_a
        self.metric_b = metric_b
        self.unit_b = unit_b


class MacroComparisonInsufficientSampleError(MacroComparisonError):
    """Raised when a distribution or correlation computation has fewer observations than required."""
    def __init__(self, operation: str, actual_n: int, required_n: int):
        super().__init__(
            f"Insufficient sample size for {operation}: required at least {required_n} observations, found {actual_n}.",
            code="MACRO_COMPARISON_INSUFFICIENT_SAMPLE",
        )
        self.operation = operation
        self.actual_n = actual_n
        self.required_n = required_n


class MacroComparisonPeriodMismatchError(MacroComparisonError):
    """Raised when exact period alignment is enforced but requested series lack common dates."""
    def __init__(self, period: str, missing_geographies: List[str]):
        super().__init__(
            f"Exact reference period '{period}' is missing in countries: {', '.join(missing_geographies)}.",
            code="MACRO_COMPARISON_PERIOD_MISMATCH",
        )
        self.period = period
        self.missing_geographies = missing_geographies


class MacroComparisonZeroVarianceError(MacroComparisonError):
    """Raised when attempting Pearson correlation on a constant time series with zero variance."""
    def __init__(self, series_name: str):
        super().__init__(
            f"Cannot compute Pearson correlation: series '{series_name}' has zero variance (constant values).",
            code="MACRO_COMPARISON_ZERO_VARIANCE",
        )
        self.series_name = series_name


class MacroComparisonQueryLimitExceededError(MacroComparisonError):
    """Raised when requested country or indicator count exceeds performance limits."""
    def __init__(self, entity_type: str, count: int, max_limit: int):
        super().__init__(
            f"Query limit exceeded for {entity_type}: requested {count}, maximum allowed is {max_limit}.",
            code="MACRO_COMPARISON_QUERY_LIMIT_EXCEEDED",
        )
        self.entity_type = entity_type
        self.count = count
        self.max_limit = max_limit


class MacroComparisonGeographicOverlapError(MacroComparisonError):
    """Raised when attempting naive aggregation across overlapping entities (e.g. Euro Area and Germany)."""
    def __init__(self, parent_area: str, member_entities: List[str]):
        super().__init__(
            f"Geographic overlap detected: '{parent_area}' contains {', '.join(member_entities)}. Naive summation causes double counting.",
            code="MACRO_COMPARISON_GEOGRAPHIC_OVERLAP",
        )
        self.parent_area = parent_area
        self.member_entities = member_entities


class MacroComparisonInvalidAggregationError(MacroComparisonError):
    """Raised when attempting invalid mathematical aggregation (e.g. summing GDP growth rates or headline inflation)."""
    def __init__(self, metric_name: str, reason: str):
        super().__init__(
            f"Invalid aggregation for metric '{metric_name}': {reason}",
            code="MACRO_COMPARISON_INVALID_AGGREGATION",
        )
        self.metric_name = metric_name
        self.reason = reason

