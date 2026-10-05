from atlas.providers.errors import ProviderError

class OpenBBError(ProviderError):
    """Base class for OpenBB provider errors."""
    pass

class OpenBBRuntimeUnavailableError(OpenBBError):
    """Raised when the OpenBB runtime cannot be loaded."""
    def __init__(self, message: str = "OpenBB runtime is unavailable."):
        super().__init__(message)

class OpenBBVersionUnsupportedError(OpenBBError):
    """Raised when the installed OpenBB version is unsupported."""
    def __init__(self, message: str = "Unsupported OpenBB version."):
        super().__init__(message)

class OpenBBCoverageUnavailableError(OpenBBError):
    """Raised when OpenBB coverage inspection fails."""
    def __init__(self, message: str = "OpenBB coverage inspection failed."):
        super().__init__(message)
