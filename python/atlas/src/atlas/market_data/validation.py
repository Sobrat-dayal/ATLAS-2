from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic_core import PydanticCustomError


def validate_finite_decimal(v: Any) -> Decimal:
    """
    Ensures that a value is a finite Decimal.
    Rejects floats.
    """
    if isinstance(v, float):
        raise PydanticCustomError(
            "float_rejected",
            "Binary floats are rejected for canonical financial fields. Pass a string or Decimal instead.",
        )

    if not isinstance(v, Decimal):
        try:
            # We strictly cast using string to ensure no float casting magic unless explicitly done
            if isinstance(v, (int, str)):
                v = Decimal(v)
            else:
                v = Decimal(str(v))
        except Exception:
            raise PydanticCustomError(
                "decimal_invalid", "Value could not be parsed into a Decimal."
            )

    if not v.is_finite():
        raise PydanticCustomError(
            "decimal_non_finite",
            "Canonical financial numbers must be finite (no NaN or Infinity).",
        )
    return v


def validate_non_negative_decimal(v: Any) -> Decimal:
    """
    Ensures that a value is a finite, non-negative Decimal.
    """
    d = validate_finite_decimal(v)
    if d < 0:
        raise PydanticCustomError(
            "decimal_negative",
            "Value must be non-negative.",
        )
    return d


def validate_positive_decimal(v: Any) -> Decimal:
    """
    Ensures that a value is a finite, strictly positive Decimal.
    """
    d = validate_finite_decimal(v)
    if d <= 0:
        raise PydanticCustomError(
            "decimal_non_positive",
            "Value must be strictly positive.",
        )
    return d


def validate_utc_datetime(v: Any) -> datetime:
    """
    Ensures a datetime is timezone-aware and normalizes it to UTC.
    Rejects naive datetimes.
    """
    if isinstance(v, str):
        try:
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise PydanticCustomError(
                "datetime_invalid", "Value must be a valid ISO8601 datetime string."
            )

    if not isinstance(v, datetime):
        raise PydanticCustomError(
            "datetime_invalid", "Value must be a datetime object or valid string."
        )

    if v.tzinfo is None:
        raise PydanticCustomError(
            "datetime_naive",
            "Market data timestamps must be timezone-aware.",
        )

    # Normalize to UTC
    return v.astimezone(timezone.utc)
