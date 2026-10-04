import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ResolutionCandidate(BaseModel):
    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    match_kind: str = Field(description="E.g., identifier, ticker, canonical_name, display_name, alias")
    matched_value: str
    identifier_scheme: Optional[str] = None
    alias_type: Optional[str] = None
    scope_entity_id: Optional[uuid.UUID] = None
    is_historical: bool = False

    model_config = ConfigDict(from_attributes=True)

class EntityResolutionRequest(BaseModel):
    query: str
    entity_type_hints: Optional[List[str]] = None
    identifier_scheme_hint: Optional[str] = None
    scope_entity_id: Optional[uuid.UUID] = None
    namespace: Optional[str] = None
    language_code: Optional[str] = None
    include_historical: bool = False
    max_candidates: int = Field(10, ge=1, le=25)

class EntityResolutionResponse(BaseModel):
    status: str = Field(description="resolved, ambiguous, or not_found")
    query: str
    resolved_entity_id: Optional[uuid.UUID] = None
    candidates: List[ResolutionCandidate]
