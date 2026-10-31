"""Historical Point-in-Time Infrastructure State Evaluation (Stage 133)."""

from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from atlas.maps.infrastructure.domain import (
    InfrastructureAsset,
    InfrastructureStatus,
    InfrastructureStatusHistory,
)
from atlas.maps.infrastructure.errors import InvalidHistoricalAsOfError


def validate_historical_as_of_date(as_of_date_str: str) -> datetime.date:
    """Validate that historical as-of date is well-formed YYYY-MM-DD and not in future."""
    try:
        dt = datetime.date.fromisoformat(as_of_date_str)
    except ValueError as exc:
        raise InvalidHistoricalAsOfError(f"Malformed date '{as_of_date_str}'. Expected format YYYY-MM-DD.") from exc

    today = datetime.date.today()
    if dt > today:
        raise InvalidHistoricalAsOfError(f"As-of date '{as_of_date_str}' is in the future. Prohibited.")

    return dt


def get_asset_state_at(
    asset: InfrastructureAsset,
    as_of_date_str: str,
) -> InfrastructureStatus:
    """Retrieve verified historical operational status as of a specific date (Fixture J)."""
    validate_historical_as_of_date(as_of_date_str)
    return asset.get_status_as_of(as_of_date_str)

