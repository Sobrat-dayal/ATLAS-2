"""Geospatial Privacy Controls and Differential Protection (Stage 131).

Implements k-anonymity minimum contributor threshold enforcement, suppression rules,
and drill-down protection to prevent de-anonymization and differential disclosure.
"""

from __future__ import annotations

from typing import Optional

from atlas.maps.analytics.domain import AtlasH3Aggregate
from atlas.maps.analytics.errors import PrivacySuppressionError


class SpatialPrivacyGovernor:
    """Enforces minimum-contributor suppression and drill-down protection."""

    def __init__(self, default_min_threshold: int = 5):
        self.default_min_threshold = default_min_threshold

    def evaluate_aggregate_suppression(
        self,
        aggregate: AtlasH3Aggregate,
        min_threshold: Optional[int] = None,
    ) -> AtlasH3Aggregate:
        """Evaluates whether an H3 cell aggregate must be suppressed for privacy.

        If distinct_count (or record_count) is below the minimum threshold,
        the cell is marked as suppressed and numeric values are shielded.
        """
        threshold = min_threshold if min_threshold is not None else self.default_min_threshold
        count_to_check = (
            aggregate.distinct_count
            if aggregate.distinct_count is not None
            else aggregate.non_null_count
        )

        if count_to_check < threshold:
            aggregate.is_suppressed = True
        else:
            aggregate.is_suppressed = False

        return aggregate

    def check_drill_down_authorization(
        self,
        cell_id: str,
        contributor_count: int,
        min_threshold: Optional[int] = None,
        is_owner_or_admin: bool = False,
    ) -> None:
        """Validates whether a user can inspect individual contributing records for a cell.

        Raises:
            PrivacySuppressionError: If contributor count is below threshold and user is not admin.
        """
        threshold = min_threshold if min_threshold is not None else self.default_min_threshold
        if contributor_count < threshold and not is_owner_or_admin:
            raise PrivacySuppressionError(
                cell_id=cell_id,
                contributor_count=contributor_count,
                threshold=threshold,
            )
