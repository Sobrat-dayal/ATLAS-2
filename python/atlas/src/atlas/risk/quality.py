"""ATLAS Financial Risk Foundation — Data Quality and Governance Engine (Stage 115).

Verifies observation completeness, tracks data gaps, checks staleness,
and produces auditable data coverage records.
"""

from datetime import datetime
from typing import List, Optional
from .enums import DataCoverageStatus
from .models import RiskDataCoverage


class RiskDataQualityEngine:
    """Evaluates data completeness and provenance without silent winsorization or synthetic interpolation."""

    @staticmethod
    def evaluate_coverage(
        required_count: int,
        available_count: int,
        matched_count: int,
        stale_count: int = 0,
        unsupported_instruments: Optional[List[str]] = None,
        missing_intervals: Optional[List[str]] = None,
    ) -> RiskDataCoverage:
        """Computes factual observation coverage metrics and classification status."""
        unsupported = unsupported_instruments or []
        intervals = missing_intervals or []

        if required_count > 0:
            ratio = float(matched_count) / float(required_count)
        else:
            ratio = 1.0 if matched_count > 0 else 0.0

        ratio = max(0.0, min(1.0, ratio))

        if matched_count < 2 or ratio < 0.20:
            status = DataCoverageStatus.INSUFFICIENT_HISTORY
        elif ratio < 0.95:
            status = DataCoverageStatus.PARTIAL_COVERAGE
        else:
            status = DataCoverageStatus.FULL_COVERAGE

        return RiskDataCoverage(
            required_observations=required_count,
            available_observations=available_count,
            matched_observations=matched_count,
            coverage_ratio=ratio,
            missing_intervals=intervals,
            stale_observations=stale_count,
            unsupported_instruments=unsupported,
            status=status,
        )

