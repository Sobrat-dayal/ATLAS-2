from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from atlas.entities.types import EntityTypeKey
from atlas.search.enums import GlobalSearchMatchKind


class GlobalSearchEntityResult(BaseModel):
    result_type: str = "entity"
    entity_id: UUID
    entity_type: EntityTypeKey
    canonical_name: str
    display_name: str
    match_kind: GlobalSearchMatchKind
    matched_text: str
    identifier_scheme_key: Optional[str] = None
    alias_type_key: Optional[str] = None
    scope_entity_id: Optional[UUID] = None
    scope_display_name: Optional[str] = None


class GlobalSearchResponse(BaseModel):
    results: List[GlobalSearchEntityResult]
    
    
class GlobalSearchRequest(BaseModel):
    query: str
    entity_types: Optional[List[EntityTypeKey]] = None
    limit: Optional[int] = Field(None, ge=1, le=50)
