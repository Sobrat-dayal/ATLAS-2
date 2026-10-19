"""Domain exceptions for Watchlist Columns (Stage 77)."""


class WatchlistColumnError(Exception):
    """Base exception for all watchlist column domain errors."""

    def __init__(self, message: str, code: str = "WATCHLIST_COLUMN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ColumnNotFoundError(WatchlistColumnError):
    """Raised when a requested column ID does not exist in the Column Registry."""

    def __init__(self, message: str = "Column not found in registry."):
        super().__init__(message, code="COLUMN_NOT_FOUND")


class ColumnUnsupportedError(WatchlistColumnError):
    """Raised when an operation is requested on an unsupported column."""

    def __init__(self, message: str = "Column is not supported for this instrument or operation."):
        super().__init__(message, code="COLUMN_UNSUPPORTED")


class ColumnNotSortableError(WatchlistColumnError):
    """Raised when a sort request targets a non-sortable column."""

    def __init__(self, message: str = "Target column does not support sorting."):
        super().__init__(message, code="COLUMN_NOT_SORTABLE")


class IncompatibleSortUnitsError(WatchlistColumnError):
    """Raised when numeric sorting fails across incompatible currencies or measures."""

    def __init__(
        self, message: str = "Cannot sort values with incompatible quotation units or currencies."
    ):
        super().__init__(message, code="INCOMPATIBLE_SORT_UNITS")


class InvalidColumnOrderError(WatchlistColumnError):
    """Raised when column ordering payload contains unknown or duplicate column IDs."""

    def __init__(self, message: str = "Invalid column ordering specification."):
        super().__init__(message, code="INVALID_COLUMN_ORDER")


class RequiredColumnHiddenError(WatchlistColumnError):
    """Raised when a request attempts to hide a mandatory column (e.g. instrument.symbol)."""

    def __init__(self, message: str = "Required identifying column cannot be hidden."):
        super().__init__(message, code="REQUIRED_COLUMN_HIDDEN")


class InvalidColumnWidthError(WatchlistColumnError):
    """Raised when a column width violates minimum or maximum width constraints."""

    def __init__(
        self, message: str = "Column width violates minimum or maximum boundary constraints."
    ):
        super().__init__(message, code="INVALID_COLUMN_WIDTH")


class InvalidPinConfigurationError(WatchlistColumnError):
    """Raised when pinned columns exceed bounds or attempt to pin non-pinnable columns."""

    def __init__(self, message: str = "Invalid pinned column configuration."):
        super().__init__(message, code="INVALID_PIN_CONFIGURATION")


class ColumnLimitExceededError(WatchlistColumnError):
    """Raised when visible column count exceeds configured maximum."""

    def __init__(self, message: str = "Visible column count exceeds maximum limit (20)."):
        super().__init__(message, code="COLUMN_LIMIT_EXCEEDED")


class ColumnConfigRevisionConflictError(WatchlistColumnError):
    """Raised when updating column preferences with a stale expected_revision."""

    def __init__(self, message: str = "Column configuration revision conflict."):
        super().__init__(message, code="COLUMN_CONFIG_REVISION_CONFLICT")


class UnsupportedConfigVersionError(WatchlistColumnError):
    """Raised when column configuration schema version is unsupported."""

    def __init__(self, message: str = "Unsupported column configuration schema version."):
        super().__init__(message, code="UNSUPPORTED_CONFIG_VERSION")
