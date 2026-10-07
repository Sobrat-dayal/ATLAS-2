class ClickHouseError(Exception):
    """Base class for all ClickHouse infrastructure errors."""
    pass


class ClickHouseConfigurationError(ClickHouseError):
    """Raised when ClickHouse configuration is invalid."""
    pass


class ClickHouseUnavailableError(ClickHouseError):
    """Raised when ClickHouse is enabled but cannot be reached."""
    pass


class ClickHouseAuthenticationError(ClickHouseError):
    """Raised when ClickHouse authentication fails."""
    pass
