class ValkeyError(Exception):
    """Base class for all Valkey infrastructure errors."""
    pass


class ValkeyConfigurationError(ValkeyError):
    """Raised when Valkey configuration is invalid."""
    pass


class ValkeyUnavailableError(ValkeyError):
    """Raised when Valkey is enabled but cannot be reached."""
    pass


class ValkeyAuthenticationError(ValkeyError):
    """Raised when Valkey authentication fails."""
    pass
