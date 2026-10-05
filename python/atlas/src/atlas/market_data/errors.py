class MarketDataError(Exception):
    """Base exception for Market Data errors."""

    pass


class MarketDataInvalidRequestError(MarketDataError):
    """Raised when a Market Data request is structurally invalid or violates constraints."""

    pass


class MarketDataOperationUnsupportedError(MarketDataError):
    """Raised when a requested Market Data operation is not supported."""

    pass


class MarketDataIntervalUnsupportedError(MarketDataError):
    """Raised when a requested BarInterval is not supported by the provider."""

    pass


class MarketDataAdjustmentUnsupportedError(MarketDataError):
    """Raised when a requested PriceAdjustment is not supported by the provider."""

    pass
