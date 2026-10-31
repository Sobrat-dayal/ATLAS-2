"""Metrics and structured logging for Corporate Geography operations (Stage 132)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("atlas.maps.corporate")


def log_footprint_query(
    company_id: str,
    facilities_count: int,
    distinct_count: int,
    duration_ms: float,
    tenant_id: str | None = None,
) -> None:
    """Log corporate footprint query performance without leaking private addresses."""
    logger.info(
        "corporate_footprint_query_completed",
        extra={
            "company_id": company_id,
            "facilities_count": facilities_count,
            "distinct_count": distinct_count,
            "duration_ms": round(duration_ms, 2),
            "tenant_id": tenant_id or "public",
        },
    )


def log_deduplication_event(
    candidate_id: str,
    matched_id: str,
    reason: str,
) -> None:
    """Log deduplication match event."""
    logger.info(
        "corporate_facility_deduplicated",
        extra={
            "candidate_id": candidate_id,
            "matched_id": matched_id,
            "reason": reason,
        },
    )

