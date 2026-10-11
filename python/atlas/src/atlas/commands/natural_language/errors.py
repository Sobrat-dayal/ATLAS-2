"""Errors for ATLAS Natural-Language Command Interpretation (Stage 48)."""

from typing import Optional


class NaturalLanguageInterpreterError(Exception):
    """Base exception for natural language command interpreter errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "INTERPRETER_ERROR"


class InterpreterUnavailableError(NaturalLanguageInterpreterError):
    """Raised when the configured model endpoint is disabled, unreachable or misconfigured."""

    def __init__(self, message: str = "Natural language interpreter is currently unavailable."):
        super().__init__(message=message, error_code="INTERPRETER_UNAVAILABLE")


class InvalidModelOutputError(NaturalLanguageInterpreterError):
    """Raised when the model emits output that violates schema or is unparseable JSON."""

    def __init__(self, message: str = "Model returned invalid structured output."):
        super().__init__(message=message, error_code="INVALID_MODEL_OUTPUT")


class InterpreterTimeoutError(NaturalLanguageInterpreterError):
    """Raised when model request times out."""

    def __init__(self, message: str = "Command interpretation model request timed out."):
        super().__init__(message=message, error_code="INTERPRETER_TIMEOUT")


class InputTooLongError(NaturalLanguageInterpreterError):
    """Raised when input text exceeds maximum allowed characters."""

    def __init__(self, message: str = "Input text exceeds maximum allowed characters."):
        super().__init__(message=message, error_code="INPUT_TOO_LONG")


# Aliases for transport and validation error handling
NaturalLanguageModelTransportError = InterpreterUnavailableError
NaturalLanguageModelInvalidOutputError = InvalidModelOutputError
