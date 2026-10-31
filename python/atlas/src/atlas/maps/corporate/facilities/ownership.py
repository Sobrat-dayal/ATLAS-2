"""Facility ownership equity percentage and validation rules (Stage 132)."""

from __future__ import annotations

from typing import Optional


def validate_ownership_percentage(percentage: Optional[float]) -> Optional[float]:
    """Validate that ownership percentage is within [0.0, 100.0] or explicitly None if unverified.

    Never invent synthetic or default 100% equity assumptions without documented evidence.
    """
    if percentage is None:
        return None

    if not isinstance(percentage, (int, float)):
        return None

    val = float(percentage)
    if val < 0.0 or val > 100.0:
        raise ValueError(f"Ownership percentage {val} out of bounds [0.0, 100.0]")

    return round(val, 2)

