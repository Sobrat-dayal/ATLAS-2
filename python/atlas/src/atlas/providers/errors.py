

class ProviderError(Exception):
    """Base class for all provider-specific errors."""

    pass


class ProviderNotRegisteredError(ProviderError):
    """Raised when an unknown provider key is requested."""

    pass


class ProviderDomainUnsupportedError(ProviderError):
    """Raised when a provider does not support the required domain."""

    pass


class ProviderFactoryInvalidError(ProviderError):
    """Raised when a provider factory fails to construct an adapter."""

    pass


class ProviderAdapterInvalidError(ProviderError):
    """Raised when a constructed provider adapter does not match its registration."""

    pass


class ProviderOperationUnsupportedError(ProviderError):
    """Raised when a provider adapter does not support a specific capability operation."""

    pass


class ProviderConfigurationRequiredError(ProviderError):
    """Raised when a provider requires configuration (e.g. API keys) before it can be used."""

    pass


class ProviderAuthenticationFailedError(ProviderError):
    """Raised when a provider rejects credentials."""

    pass


class ProviderAuthorizationFailedError(ProviderError):
    """Raised when a provider denies access to a requested resource/operation."""

    pass


class ProviderRateLimitedError(ProviderError):
    """Raised when a provider enforces a rate limit."""

    pass


class ProviderTimeoutError(ProviderError):
    """Raised when a provider fails to respond in time."""

    pass


class ProviderUpstreamUnavailableError(ProviderError):
    """Raised when a provider's upstream service is offline or unreachable."""

    pass


class ProviderInvalidResponseError(ProviderError):
    """Raised when a provider returns unparseable or invalid data."""

    pass


class ProviderExecutionFailedError(ProviderError):
    """Raised when a provider operation fails generally, after being sanitized from a vendor exception."""

    pass


def sanitize_provider_error(error: Exception) -> ProviderError:
    """
    Translates raw vendor exceptions into sanitized ATLAS ProviderErrors.
    Ensures credentials or raw stack traces do not leak to the user.
    """
    if isinstance(error, ProviderError):
        return error
    # Log original exception safely here if logging is set up
    return ProviderExecutionFailedError("Provider execution failed with an upstream error.")
