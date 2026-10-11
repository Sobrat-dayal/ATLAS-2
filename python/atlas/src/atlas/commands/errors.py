"""Custom exceptions for ATLAS Command Language parsing."""

from typing import Optional

from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus


class AtlasCommandError(Exception):
    """Base exception for all command parsing errors."""

    def __init__(
        self,
        error_code: AtlasCommandErrorCode,
        message: str,
        status: AtlasCommandParseStatus = AtlasCommandParseStatus.INVALID,
        raw_token: Optional[str] = None,
        position: Optional[int] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status = status
        self.raw_token = raw_token
        self.position = position


class AtlasCommandLexerError(AtlasCommandError):
    """Raised during tokenization of raw command text."""

    pass


class AtlasCommandParserError(AtlasCommandError):
    """Raised during syntactic AST construction."""

    pass


class AtlasCommandBinderError(AtlasCommandError):
    """Raised during semantic binding and validation."""

    pass
