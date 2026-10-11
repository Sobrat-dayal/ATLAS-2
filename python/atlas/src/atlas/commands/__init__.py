"""ATLAS Command Language v1 package.

Provides deterministic, side-effect free lexing, syntactic parsing, semantic binding,
and target entity resolution for structured commands and recognized shorthand.
"""

from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus, AtlasCommandSourceKind
from .models import (
    AmbiguityCandidate,
    AtlasCommandParseRequest,
    AtlasCommandParseResult,
    ResolvedTargetSummary,
)
from .service import AtlasCommandParsingService

__all__ = [
    "AtlasCommandSourceKind",
    "AtlasCommandParseStatus",
    "AtlasCommandErrorCode",
    "AtlasCommandParseRequest",
    "AtlasCommandParseResult",
    "ResolvedTargetSummary",
    "AmbiguityCandidate",
    "AtlasCommandParsingService",
]
