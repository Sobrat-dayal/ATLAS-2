from atlas.core.exceptions import AtlasError

class CapabilityError(AtlasError):
    pass

class CapabilityNotFoundError(CapabilityError):
    def __init__(self, key: str, version: int | None = None):
        msg = f"Capability '{key}' not found"
        if version is not None:
            msg = f"Capability '{key}' version {version} not found"
        super().__init__(message=msg, code="CAPABILITY_NOT_FOUND", status_code=404)

class CapabilityInputInvalidError(CapabilityError):
    def __init__(self, details: list):
        super().__init__(
            message="Capability input validation failed",
            code="CAPABILITY_INPUT_INVALID",
            status_code=422,
            details=details
        )

class CapabilityForbiddenError(CapabilityError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            code="CAPABILITY_FORBIDDEN",
            status_code=403
        )

class CapabilityConfirmationRequiredError(CapabilityError):
    def __init__(self):
        super().__init__(
            message="Capability execution requires confirmation",
            code="CAPABILITY_CONFIRMATION_REQUIRED",
            status_code=403
        )

class CapabilityOutputInvalidError(CapabilityError):
    def __init__(self, details: list):
        super().__init__(
            message="Capability output validation failed",
            code="CAPABILITY_OUTPUT_INVALID",
            status_code=500,
            details=details
        )

class CapabilityExecutionFailedError(CapabilityError):
    def __init__(self, message: str = "Capability execution failed"):
        super().__init__(
            message=message,
            code="CAPABILITY_EXECUTION_FAILED",
            status_code=500
        )
