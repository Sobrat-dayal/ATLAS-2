"""Command Abstract Syntax Tree (AST) definitions for ATLAS Command Language v1."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from .enums import AtlasCommandSourceKind


@dataclass
class AtlasCommandAst:
    """Syntactic representation of a parsed ATLAS command.

    Maintains clean separation from semantic binding and execution plans.
    """

    source_kind: AtlasCommandSourceKind
    raw_text: str
    command_name: Optional[str] = None
    action: Optional[str] = None
    target: Optional[str] = None
    parameters: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"AtlasCommandAst(source_kind={self.source_kind.value}, "
            f"name={self.command_name!r}, action={self.action!r}, "
            f"target={self.target!r}, params={self.parameters})"
        )
