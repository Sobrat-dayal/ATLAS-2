"""Capabilities registry and financial qualification rules for Watchlist Alerts V1 (Stage 80)."""

from typing import Dict, List, Set

from atlas.watchlists.alerts.schemas import (
    AlertCapabilitiesResponse,
    AlertCapabilityItem,
    AlertRuleType,
    ComparisonOperator,
    QuoteMeasure,
    ReferenceMethodology,
)

MAX_ACTIVE_ALERTS_PER_USER = 100
MAX_ALERTS_PER_INSTRUMENT = 20

# Eligible measures per asset class to prevent financial category errors
ASSET_CLASS_MEASURE_COMPATIBILITY: Dict[str, Set[QuoteMeasure]] = {
    "equity": {
        QuoteMeasure.LAST,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
        QuoteMeasure.MID,
        QuoteMeasure.OPEN,
        QuoteMeasure.HIGH,
        QuoteMeasure.LOW,
        QuoteMeasure.CLOSE,
    },
    "etf": {
        QuoteMeasure.LAST,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
        QuoteMeasure.MID,
        QuoteMeasure.NAV,
        QuoteMeasure.OPEN,
        QuoteMeasure.HIGH,
        QuoteMeasure.LOW,
        QuoteMeasure.CLOSE,
    },
    "mutual_fund": {
        QuoteMeasure.NAV,
        QuoteMeasure.CLOSE,
    },
    "fx": {
        QuoteMeasure.MID,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
    },
    "crypto": {
        QuoteMeasure.LAST,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
        QuoteMeasure.MID,
    },
    "futures": {
        QuoteMeasure.LAST,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
        QuoteMeasure.MID,
        QuoteMeasure.OPEN,
        QuoteMeasure.HIGH,
        QuoteMeasure.LOW,
        QuoteMeasure.CLOSE,
    },
    "bond": {
        QuoteMeasure.LAST,
        QuoteMeasure.BID,
        QuoteMeasure.ASK,
        QuoteMeasure.MID,
        QuoteMeasure.YIELD,
    },
}

SUPPORTED_CAPABILITIES: List[AlertCapabilityItem] = [
    AlertCapabilityItem(
        rule_type=AlertRuleType.PRICE_ABOVE,
        display_name="Price is Above",
        description="Triggers when the qualified observation exceeds the specified price threshold.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.BID,
            QuoteMeasure.ASK,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
            QuoteMeasure.YIELD,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures", "bond"],
        requires_reference_methodology=False,
        default_comparator=ComparisonOperator.GREATER_THAN,
    ),
    AlertCapabilityItem(
        rule_type=AlertRuleType.PRICE_BELOW,
        display_name="Price is Below",
        description="Triggers when the qualified observation drops below the specified price threshold.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.BID,
            QuoteMeasure.ASK,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
            QuoteMeasure.YIELD,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures", "bond"],
        requires_reference_methodology=False,
        default_comparator=ComparisonOperator.LESS_THAN,
    ),
    AlertCapabilityItem(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        display_name="Price Crosses Above",
        description="Requires verified prior observation <= threshold and subsequent observation > threshold. Does not trigger on initial snapshot.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.BID,
            QuoteMeasure.ASK,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
            QuoteMeasure.YIELD,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures", "bond"],
        requires_reference_methodology=False,
        default_comparator=ComparisonOperator.CROSS_ABOVE,
    ),
    AlertCapabilityItem(
        rule_type=AlertRuleType.CROSSING_BELOW,
        display_name="Price Crosses Below",
        description="Requires verified prior observation >= threshold and subsequent observation < threshold. Does not trigger on initial snapshot.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.BID,
            QuoteMeasure.ASK,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
            QuoteMeasure.YIELD,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures", "bond"],
        requires_reference_methodology=False,
        default_comparator=ComparisonOperator.CROSS_BELOW,
    ),
    AlertCapabilityItem(
        rule_type=AlertRuleType.PERCENTAGE_CHANGE_ABOVE,
        display_name="% Change Crosses Above",
        description="Triggers when qualified percentage change relative to canonical reference price crosses above the threshold percentage.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures"],
        requires_reference_methodology=True,
        default_comparator=ComparisonOperator.CROSS_ABOVE,
    ),
    AlertCapabilityItem(
        rule_type=AlertRuleType.PERCENTAGE_CHANGE_BELOW,
        display_name="% Change Crosses Below",
        description="Triggers when qualified percentage change relative to canonical reference price crosses below the threshold percentage.",
        supported_measures=[
            QuoteMeasure.LAST,
            QuoteMeasure.MID,
            QuoteMeasure.NAV,
        ],
        supported_asset_classes=["equity", "etf", "mutual_fund", "fx", "crypto", "futures"],
        requires_reference_methodology=True,
        default_comparator=ComparisonOperator.CROSS_BELOW,
    ),
]

REFERENCE_METHODOLOGIES = [
    {
        "id": ReferenceMethodology.SESSION_PREVIOUS_CLOSE,
        "name": "Session Previous Close",
        "description": "Standard equity session baseline: (P_t - PrevClose) / PrevClose * 100",
        "supported_asset_classes": ["equity", "etf", "futures"],
    },
    {
        "id": ReferenceMethodology.ROLLING_24H,
        "name": "Rolling 24-Hour Comparison",
        "description": "Crypto and 24/7 OTC markets: (P_t - P_{t-24h}) / P_{t-24h} * 100",
        "supported_asset_classes": ["crypto", "fx"],
    },
    {
        "id": ReferenceMethodology.PREVIOUS_NAV,
        "name": "Previous Valuation NAV",
        "description": "Funds and Mutual Funds: (NAV_t - NAV_{prior}) / NAV_{prior} * 100",
        "supported_asset_classes": ["mutual_fund", "etf"],
    },
]

COOLDOWN_PRESETS = [
    {"label": "None (Instant Re-Arm on Transition)", "seconds": 0},
    {"label": "1 Minute", "seconds": 60},
    {"label": "5 Minutes", "seconds": 300},
    {"label": "15 Minutes", "seconds": 900},
    {"label": "1 Hour", "seconds": 3600},
    {"label": "1 Day", "seconds": 86400},
]


def get_alert_capabilities() -> AlertCapabilitiesResponse:
    """Returns the canonical catalog of alert capabilities."""
    return AlertCapabilitiesResponse(
        capabilities=SUPPORTED_CAPABILITIES,
        reference_methodologies=REFERENCE_METHODOLOGIES,
        cooldown_presets=COOLDOWN_PRESETS,
        max_active_alerts_per_user=MAX_ACTIVE_ALERTS_PER_USER,
        max_alerts_per_instrument=MAX_ALERTS_PER_INSTRUMENT,
    )


def validate_measure_for_asset_class(measure: QuoteMeasure, asset_class: str) -> bool:
    """Validates that a financial measure is compatible with the instrument's asset class."""
    norm_ac = asset_class.lower()
    allowed = ASSET_CLASS_MEASURE_COMPATIBILITY.get(norm_ac, ASSET_CLASS_MEASURE_COMPATIBILITY["equity"])
    return measure in allowed
