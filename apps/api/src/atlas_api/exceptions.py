class AtlasError(Exception):
    """Base exception for all intentional ATLAS errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | list | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
