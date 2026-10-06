from atlas.core.exceptions import AtlasError


class InstrumentError(AtlasError):
    """Base error for financial instrument operations."""

    def __init__(self, message: str, code: str = "INSTRUMENT_ERROR", status_code: int = 400):
        super().__init__(message, code=code, status_code=status_code)


class InstrumentNotFoundError(InstrumentError):
    def __init__(self, entity_id: str):
        super().__init__(
            f"Financial instrument not found: {entity_id}",
            code="INSTRUMENT_NOT_FOUND",
            status_code=404,
        )


class EntityNotFinancialInstrumentError(InstrumentError):
    def __init__(self, entity_id: str, actual_type: str):
        super().__init__(
            f"Entity {entity_id} is a {actual_type}, not a financial instrument.",
            code="ENTITY_NOT_FINANCIAL_INSTRUMENT",
            status_code=404,
        )


class InstrumentDataInconsistentError(InstrumentError):
    def __init__(self, entity_id: str, expected_type: str, actual_type: str):
        super().__init__(
            f"Data inconsistency for {entity_id}: expected specialization {expected_type}, found base type {actual_type}.",
            code="INSTRUMENT_DATA_INCONSISTENT",
            status_code=500,
        )


class InvalidUnderlyingError(InstrumentError):
    def __init__(self, underlying_id: str):
        super().__init__(
            f"Invalid underlying entity: {underlying_id}. Must be a valid financial instrument.",
            code="INVALID_UNDERLYING",
            status_code=400,
        )


class InvalidCurrencyError(InstrumentError):
    def __init__(self, currency_id: str):
        super().__init__(
            f"Invalid currency entity: {currency_id}. Must be a valid currency.",
            code="INVALID_CURRENCY",
            status_code=400,
        )
