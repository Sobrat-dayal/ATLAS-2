from atlas.core.exceptions import AtlasError


class AliasError(AtlasError):
    """Base error for alias operations."""

    pass


class UnknownAliasTypeError(AliasError):
    """Raised when an alias type is not found."""

    def __init__(self, key: str):
        super().__init__(f"Unknown alias type: {key}")
        self.key = key


class InvalidAliasError(AliasError):
    """Raised when an alias value is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
