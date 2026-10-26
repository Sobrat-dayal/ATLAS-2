"""Domain Exceptions for Central Bank Intelligence (Stage 91)."""

from typing import Any, Optional


class CentralBankError(Exception):
    """Base exception for central bank intelligence operations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CentralBankNotFoundError(CentralBankError):
    """Raised when a central bank institution cannot be resolved."""

    def __init__(self, identifier: str) -> None:
        message = f"Central bank institution not found: '{identifier}'"
        super().__init__(message)
        self.identifier = identifier


class CentralBankInstrumentNotFoundError(CentralBankError):
    """Raised when a monetary policy instrument is unknown."""

    def __init__(self, instrument_id: str) -> None:
        message = f"Monetary policy instrument not found: '{instrument_id}'"
        super().__init__(message)
        self.instrument_id = instrument_id


class CentralBankDecisionNotFoundError(CentralBankError):
    """Raised when an official policy decision cannot be resolved."""

    def __init__(self, decision_id: str) -> None:
        message = f"Monetary policy decision not found: '{decision_id}'"
        super().__init__(message)
        self.decision_id = decision_id


class CentralBankMeetingNotFoundError(CentralBankError):
    """Raised when an official meeting record cannot be found."""

    def __init__(self, meeting_id: str) -> None:
        message = f"Monetary policy meeting not found: '{meeting_id}'"
        super().__init__(message)
        self.meeting_id = meeting_id


class CentralBankPublicationNotFoundError(CentralBankError):
    """Raised when an official document or statement is unavailable."""

    def __init__(self, document_id: str) -> None:
        message = f"Central bank publication document not found: '{document_id}'"
        super().__init__(message)
        self.document_id = document_id


class CentralBankRateRangeInvalidError(CentralBankError):
    """Raised when a policy rate target range lower bound exceeds upper bound."""

    def __init__(self, message_or_lower: Any, upper: Optional[Any] = None) -> None:
        if upper is not None:
            message = f"Invalid policy rate target range: lower {message_or_lower}% exceeds upper {upper}%"
            self.lower = message_or_lower
            self.upper = upper
        else:
            message = str(message_or_lower)
            self.lower = None
            self.upper = None
        super().__init__(message)


class CentralBankIncompatibleInstrumentError(CentralBankError):
    """Raised when attempting rate change calculations across incompatible instruments."""

    def __init__(self, message_or_inst_a: Any, inst_b: Optional[str] = None) -> None:
        if inst_b is not None:
            message = f"Cannot compute rate change across incompatible instruments: '{message_or_inst_a}' vs '{inst_b}'"
            self.inst_a = str(message_or_inst_a)
            self.inst_b = inst_b
        else:
            message = str(message_or_inst_a)
            self.inst_a = None
            self.inst_b = None
        super().__init__(message)
