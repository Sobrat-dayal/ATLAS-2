class AuthorizationError(Exception):
    """Base class for all authorization-related errors."""
    def __init__(self, message: str, code: str = "AUTHORIZATION_ERROR", status_code: int = 400, details: dict | list | None = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class PermissionDeniedError(AuthorizationError):
    """Raised when a user lacks the required permission for an action."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message, code="PERMISSION_DENIED", status_code=403)

class AuthorizationUnavailableError(AuthorizationError):
    """Raised when the authorization subsystem is unavailable (e.g., DB down)."""
    def __init__(self, message: str = "Authorization service is currently unavailable."):
        super().__init__(message, code="AUTHORIZATION_UNAVAILABLE", status_code=503)

class InvalidRoleError(AuthorizationError):
    """Raised when an invalid role is referenced."""
    def __init__(self, role_key: str):
        super().__init__(f"Invalid role: {role_key}", code="INVALID_ROLE", status_code=400)

class UnknownPermissionError(AuthorizationError):
    """Raised when an unknown permission is requested."""
    def __init__(self, permission_code: str):
        super().__init__(f"Unknown permission: {permission_code}", code="UNKNOWN_PERMISSION", status_code=500)

