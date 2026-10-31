"""Address normalization and precision-qualified geocoding (Stage 132)."""

from __future__ import annotations

import re
from typing import Any

from atlas.maps.corporate.domain import GeographicPrecisionClass


def normalize_address(address_text: str | None) -> str:
    """Normalize address string by lowercasing, stripping punctuation, and standardizing street abbreviations."""
    if not address_text:
        return ""
    text = address_text.lower()
    text = re.sub(r"[,\.#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    replacements = {
        " street": " st",
        " avenue": " ave",
        " boulevard": " blvd",
        " road": " rd",
        " drive": " dr",
        " lane": " ln",
        " highway": " hwy",
        " building": " bldg",
        " suite": " ste",
        " floor": " fl",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)

    return text


def evaluate_geocoding_precision(
    address_text: str,
    has_street_number: bool,
    has_street_name: bool,
    has_locality: bool,
    has_country: bool,
) -> GeographicPrecisionClass:
    """Evaluate coordinate precision based on provided address granularity.

    Guarantees:
    - If only city/locality is provided, resolves to LOCALITY_CENTROID.
    - If only country is known, resolves to COUNTRY_ONLY.
    - Full street address with building/number resolves to VERIFIED_STREET_ADDRESS.
    """
    if has_street_number and has_street_name:
        return GeographicPrecisionClass.VERIFIED_STREET_ADDRESS
    if has_street_name and has_locality:
        return GeographicPrecisionClass.GEOCODED_ADDRESS_APPROXIMATE
    if has_locality:
        return GeographicPrecisionClass.LOCALITY_CENTROID
    if has_country:
        return GeographicPrecisionClass.COUNTRY_ONLY
    return GeographicPrecisionClass.LOCATION_UNRESOLVED

