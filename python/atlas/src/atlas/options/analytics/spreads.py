"""Bid-Ask spread and midpoint analytics for options contracts (Stage 141).

Enforces execution disclaimers and handles zero bids or crossed quotes.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple


def calculate_spread_metrics(
    bid: Optional[float],
    ask: Optional[float],
) -> Dict[str, Optional[float]]:
    """Compute absolute spread, midpoint and relative spread.

    Note: Midpoint is strictly an indicative reference and does not guarantee fill price.
    """
    if bid is None or ask is None:
        return {"spread": None, "midpoint": None, "relative_spread": None}

    spread = round(ask - bid, 4)
    midpoint = round((bid + ask) / 2.0, 4)

    rel_spread = None
    if midpoint > 0.0:
        rel_spread = round(spread / midpoint, 4)

    return {
        "spread": spread,
        "midpoint": midpoint,
        "relative_spread": rel_spread,
    }

