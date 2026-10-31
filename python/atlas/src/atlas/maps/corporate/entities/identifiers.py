"""Identifier validation and normalization for Corporate Geography (Stage 132).

Validates LEI (ISO 17442), CIK (SEC 10-digit), ISIN (ISO 6166), and national entity identifiers.
"""

from __future__ import annotations

import re


def validate_lei(lei: str | None) -> bool:
    """Validate ISO 17442 Legal Entity Identifier (20 characters alphanumeric, modulo 97 check)."""
    if not lei:
        return False
    clean = lei.strip().upper()
    if len(clean) != 20:
        return False
    if not re.match(r"^[0-9A-Z]{20}$", clean):
        return False

    # ISO 7064 Mod 97-10 check digits
    # Convert letters to digits: A=10, B=11, ..., Z=35
    num_str = ""
    for ch in clean:
        if ch.isdigit():
            num_str += ch
        else:
            num_str += str(ord(ch) - 55)

    try:
        remainder = int(num_str) % 97
        return remainder == 1
    except (ValueError, OverflowError):
        return False


def validate_cik(cik: str | None) -> bool:
    """Validate SEC Central Index Key (1 to 10 digits)."""
    if not cik:
        return False
    clean = cik.strip()
    return bool(re.match(r"^\d{1,10}$", clean))


def normalize_cik(cik: str) -> str:
    """Format CIK as 10-digit zero-padded string."""
    return cik.strip().zfill(10)


def validate_isin(isin: str | None) -> bool:
    """Validate ISO 6166 International Securities Identification Number."""
    if not isin:
        return False
    clean = isin.strip().upper()
    if len(clean) != 12:
        return False
    if not re.match(r"^[A-Z]{2}[0-9A-Z]{9}[0-9]$", clean):
        return False

    # Luhn algorithm check digit
    digits = ""
    for ch in clean[:-1]:
        if ch.isdigit():
            digits += ch
        else:
            digits += str(ord(ch) - 55)

    # Luhn double-add from right
    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        val = int(d)
        if i % 2 == 0:
            val *= 2
            if val > 9:
                val -= 9
        total += val

    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(clean[-1])

