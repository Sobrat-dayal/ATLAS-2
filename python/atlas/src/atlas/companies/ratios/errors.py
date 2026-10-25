"""Typed Exception Classes for Company Financial Ratios (Stage 83)."""


class RatioError(Exception):
    """Base exception for financial ratio operations."""

    def __init__(self, message: str, code: str = "RATIO_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class RatioNotFoundError(RatioError):
    def __init__(self, ratio_id: str):
        super().__init__(f"Financial ratio '{ratio_id}' not found in registry", code="RATIO_NOT_FOUND")
        self.ratio_id = ratio_id


class MethodologyNotSupportedError(RatioError):
    def __init__(self, ratio_id: str, methodology: str):
        super().__init__(
            f"Methodology '{methodology}' not supported for ratio '{ratio_id}'",
            code="METHODOLOGY_NOT_SUPPORTED",
        )
        self.ratio_id = ratio_id
        self.methodology = methodology


class IncompatibleInputsError(RatioError):
    def __init__(self, message: str):
        super().__init__(message, code="INCOMPATIBLE_INPUTS")


class RatioCalculationLimitExceededError(RatioError):
    def __init__(self, requested: int, limit: int):
        super().__init__(
            f"Requested {requested} ratios exceeds limit of {limit}",
            code="RATIO_CALCULATION_LIMIT_EXCEEDED",
        )
