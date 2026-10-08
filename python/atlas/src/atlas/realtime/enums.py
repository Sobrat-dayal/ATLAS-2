from enum import Enum


class LiveEventType(str, Enum):
    """
    Taxonomy of supported transport events emitted by the Live Event Pipeline.
    These are not Universal Event models; they are short-retention backend state-transition transports.
    """
    MARKET_QUOTE_UPDATED = "market.quote.updated"
    MARKET_QUOTE_FRESHNESS_UPDATED = "market.quote.freshness.updated"
