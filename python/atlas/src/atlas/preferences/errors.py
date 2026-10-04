from typing import Optional, Any
from atlas.core.exceptions import AtlasError

class PreferenceError(AtlasError):
    pass

class PreferenceNotFoundError(PreferenceError):
    def __init__(self, key: str):
        super().__init__(
            code="PREFERENCE_NOT_FOUND",
            message=f"Preference '{key}' not found."
        )

class InvalidPreferenceKeyError(PreferenceError):
    def __init__(self, key: str):
        super().__init__(
            code="INVALID_PREFERENCE_KEY",
            message=f"Preference key '{key}' is invalid or unsupported."
        )

class InvalidPreferencePayloadError(PreferenceError):
    def __init__(self, message: str = "Invalid preference payload"):
        super().__init__(
            code="INVALID_PREFERENCE_PAYLOAD",
            message=message
        )

class UnsupportedPreferenceVersionError(PreferenceError):
    def __init__(self, version: int):
        super().__init__(
            code="UNSUPPORTED_PREFERENCE_VERSION",
            message=f"Schema version {version} is unsupported."
        )

class PreferenceTooLargeError(PreferenceError):
    def __init__(self):
        super().__init__(
            code="PREFERENCE_TOO_LARGE",
            message="Preference payload exceeds maximum allowed size."
        )

class PreferenceConflictError(PreferenceError):
    def __init__(self, key: str):
        super().__init__(
            code="PREFERENCE_CONFLICT",
            message=f"Conflict updating preference '{key}'. The revision provided does not match the server."
        )
