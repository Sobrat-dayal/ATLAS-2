"""Bitemporal facility history and as-of point-in-time state evaluation (Stage 132)."""

from __future__ import annotations

import datetime
from typing import Optional

from atlas.maps.corporate.domain import (
    CorporateFacility,
    CorporateFacilityStatus,
    FacilityEntityLink,
    FacilityStatusHistory,
)
from atlas.maps.corporate.errors import InvalidHistoricalAsOfError


def parse_as_of_timestamp(as_of: str | datetime.datetime | None) -> Optional[datetime.datetime]:
    """Parse and validate as-of datetime, ensuring no future look-ahead bias."""
    if as_of is None:
        return None

    dt: datetime.datetime
    if isinstance(as_of, datetime.datetime):
        dt = as_of
    elif isinstance(as_of, str):
        try:
            dt = datetime.datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except ValueError as err:
            raise InvalidHistoricalAsOfError(as_of, f"Malformed ISO timestamp: {err}")
    else:
        raise InvalidHistoricalAsOfError(str(as_of), "Expected ISO string or datetime object")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    if dt > now + datetime.timedelta(minutes=5):  # allow small clock skew
        raise InvalidHistoricalAsOfError(
            dt.isoformat(),
            "Cannot specify historical as-of timestamp in the future (look-ahead bias prohibited).",
        )

    return dt


def filter_links_by_as_of(
    links: list[FacilityEntityLink],
    as_of: datetime.datetime | None,
) -> list[FacilityEntityLink]:
    """Filter entity-facility links active as of the requested historical date."""
    if as_of is None:
        return links

    valid_links: list[FacilityEntityLink] = []
    for link in links:
        valid_from = link.valid_from
        valid_to = link.valid_to

        if valid_from and valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=datetime.timezone.utc)
        if valid_to and valid_to.tzinfo is None:
            valid_to = valid_to.replace(tzinfo=datetime.timezone.utc)

        if valid_from and valid_from > as_of:
            continue
        if valid_to and valid_to < as_of:
            continue

        valid_links.append(link)

    return valid_links


def get_status_as_of(
    facility: CorporateFacility,
    as_of: datetime.datetime | None,
) -> CorporateFacilityStatus:
    """Evaluate historical operational status of a facility as of a given timestamp."""
    if as_of is None or not facility.status_history:
        return facility.facility_status

    # Scan status history for the record covering as_of
    for entry in sorted(facility.status_history, key=lambda x: x.valid_from or datetime.datetime.min, reverse=True):
        valid_from = entry.valid_from
        valid_to = entry.valid_to

        if valid_from and valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=datetime.timezone.utc)
        if valid_to and valid_to.tzinfo is None:
            valid_to = valid_to.replace(tzinfo=datetime.timezone.utc)

        if valid_from and valid_from > as_of:
            continue
        if valid_to and valid_to < as_of:
            continue

        return entry.status

    return facility.facility_status

