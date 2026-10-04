from decimal import Decimal
from typing import Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from atlas.geography.errors import InvalidCoordinatesError, InvalidTimezoneError


def validate_coordinates(
    latitude: Optional[Decimal], longitude: Optional[Decimal]
) -> tuple[Optional[Decimal], Optional[Decimal]]:
    if (latitude is None) != (longitude is None):
        raise InvalidCoordinatesError(
            "Latitude and longitude must both be provided, or both be NULL."
        )

    if latitude is not None and longitude is not None:
        if not (-90 <= latitude <= 90):
            raise InvalidCoordinatesError("Latitude must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise InvalidCoordinatesError("Longitude must be between -180 and 180.")

    return latitude, longitude


def validate_timezone(timezone_name: Optional[str]) -> Optional[str]:
    if not timezone_name:
        return None

    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        raise InvalidTimezoneError(f"Invalid IANA timezone name: {timezone_name}")

    return timezone_name
