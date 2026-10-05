from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

from atlas.market_data.validation import validate_utc_datetime

# Canonical timestamp type
# Always timezone-aware, always normalized to UTC, always serialized to ISO8601 with Z.


def _serialize_utc(dt: datetime) -> str:
    # Ensure standard Z format for UTC
    return dt.isoformat().replace("+00:00", "Z")


CanonicalDatetime = Annotated[
    datetime,
    BeforeValidator(validate_utc_datetime),
    PlainSerializer(_serialize_utc, return_type=str, when_used="json"),
]
