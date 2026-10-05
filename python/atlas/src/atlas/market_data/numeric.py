from decimal import Decimal
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

from atlas.market_data.validation import (
    validate_finite_decimal,
    validate_non_negative_decimal,
    validate_positive_decimal,
)

# Canonical numeric types
# Serialized as string to preserve precision when dumping to JSON


def _serialize_decimal(d: Decimal) -> str:
    return format(d, "f")


CanonicalDecimal = Annotated[
    Decimal,
    BeforeValidator(validate_finite_decimal),
    PlainSerializer(_serialize_decimal, return_type=str, when_used="json"),
]

NonNegativeCanonicalDecimal = Annotated[
    Decimal,
    BeforeValidator(validate_non_negative_decimal),
    PlainSerializer(_serialize_decimal, return_type=str, when_used="json"),
]

PositiveCanonicalDecimal = Annotated[
    Decimal,
    BeforeValidator(validate_positive_decimal),
    PlainSerializer(_serialize_decimal, return_type=str, when_used="json"),
]
