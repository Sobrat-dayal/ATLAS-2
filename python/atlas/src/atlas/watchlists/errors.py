"""Typed domain exceptions for Watchlists V1 (Stage 76)."""


class WatchlistError(Exception):
    """Base exception for all watchlist operations."""

    def __init__(self, message: str, code: str = "WATCHLIST_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class WatchlistNotFoundError(WatchlistError):
    """Raised when a watchlist is not found or not owned by user."""

    def __init__(self, message: str = "Watchlist not found"):
        super().__init__(message, code="WATCHLIST_NOT_FOUND")


class WatchlistNameConflictError(WatchlistError):
    """Raised when a user already has a watchlist with the same normalized name."""

    def __init__(self, message: str = "A watchlist with this name already exists"):
        super().__init__(message, code="WATCHLIST_NAME_CONFLICT")


class WatchlistQuotaExceededError(WatchlistError):
    """Raised when the maximum number of watchlists per user (50) is reached."""

    def __init__(self, message: str = "Watchlist quota exceeded (maximum 50 watchlists per user)"):
        super().__init__(message, code="WATCHLIST_LIMIT_EXCEEDED")


class WatchlistItemQuotaExceededError(WatchlistError):
    """Raised when the maximum number of items in a watchlist (250) is reached."""

    def __init__(
        self, message: str = "Watchlist item quota exceeded (maximum 250 items per watchlist)"
    ):
        super().__init__(message, code="ITEM_LIMIT_EXCEEDED")


class InstrumentNotFoundError(WatchlistError):
    """Raised when the target financial instrument UUID is not found in the catalog."""

    def __init__(self, message: str = "Financial instrument not found"):
        super().__init__(message, code="INSTRUMENT_NOT_FOUND")


class InvalidMarketSeriesError(WatchlistError):
    """Raised when the requested market series is invalid or unsupported."""

    def __init__(self, message: str = "Invalid market series specification"):
        super().__init__(message, code="INVALID_MARKET_SERIES")


class DuplicateWatchlistItemError(WatchlistError):
    """Raised when adding an instrument/series that is already in the watchlist."""

    def __init__(self, message: str = "Instrument is already in this watchlist"):
        super().__init__(message, code="DUPLICATE_WATCHLIST_ITEM")


class WatchlistItemNotFoundError(WatchlistError):
    """Raised when a watchlist membership item is not found."""

    def __init__(self, message: str = "Watchlist item not found"):
        super().__init__(message, code="ITEM_NOT_FOUND")


class WatchlistRevisionConflictError(WatchlistError):
    """Raised when an operation encounters an optimistic concurrency revision mismatch."""

    def __init__(self, message: str = "Watchlist has been modified concurrently. Please refresh."):
        super().__init__(message, code="REVISION_CONFLICT")


class InvalidReorderRequestError(WatchlistError):
    """Raised when reordering list of item IDs is invalid (missing, duplicate, or foreign IDs)."""

    def __init__(self, message: str = "Invalid reorder request payload"):
        super().__init__(message, code="INVALID_REORDER")


class InvalidWatchlistNameError(WatchlistError):
    """Raised when a watchlist name is empty, whitespace-only, too long, or invalid."""

    def __init__(self, message: str = "Invalid watchlist name"):
        super().__init__(message, code="INVALID_NAME")


class NotEntitledError(WatchlistError):
    """Raised when a user is not authorized or entitled to access a watchlist."""

    def __init__(self, message: str = "User is not entitled to this resource"):
        super().__init__(message, code="NOT_ENTITLED")
