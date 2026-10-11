"""Data models and API schemas for ATLAS Command Language v1."""

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import AtlasCommandParseStatus, AtlasCommandSourceKind


class ResolvedTargetSummary(BaseModel):
    """Identifying metadata for a uniquely resolved entity target."""

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    matched_value: str
    match_kind: str
    scope_entity_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class AmbiguityCandidate(BaseModel):
    """Candidate entity summary returned when a target is ambiguous."""

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    matched_value: str
    match_kind: str
    scope_entity_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class AtlasCommandParseRequest(BaseModel):
    """Request payload for command parsing."""

    text: str = Field(..., max_length=512, description="Raw command text to parse")


class AtlasCommandParseResult(BaseModel):
    """Response payload containing parsed command plan and readiness status."""

    command_language_version: int = Field(default=1, description="Protocol version (v1)")
    status: AtlasCommandParseStatus
    source_kind: Optional[AtlasCommandSourceKind] = None
    normalized_command: str = ""
    command_id: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    raw_target: Optional[str] = None
    resolved_target: Optional[ResolvedTargetSummary] = None
    arguments: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    ambiguity_candidates: Optional[List[AmbiguityCandidate]] = None
    execution_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
