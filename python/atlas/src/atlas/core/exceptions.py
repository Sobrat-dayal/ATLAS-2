class AtlasError(Exception):
    """Base class for all domain-related errors."""
    def __init__(self, message: str, code: str = "ATLAS_ERROR", status_code: int = 400, details: dict | list | None = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
