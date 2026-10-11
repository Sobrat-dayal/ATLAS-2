"""Token definitions for ATLAS Command Language v1."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Lexical token types recognized by AtlasCommandLexer."""

    SLASH = auto()
    WORD = auto()
    STRING = auto()
    PARAM_NAME = auto()
    EQUALS = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """Immutable representation of a lexical token."""

    type: TokenType
    value: str
    position: int
    raw_length: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"
