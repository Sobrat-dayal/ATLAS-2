import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

class RelationshipTypeResponse(BaseModel):
    key: str
    name: str
    description: Optional[str]
    category: str
    inverse_key: Optional[str]
    canonical_key: str
    is_symmetric: bool
    source_policy_key: str
    target_policy_key: str
    allows_self: bool
    is_system: bool

    class Config:
        from_attributes = True


class EntityRelationshipCreate(BaseModel):
    target_entity_id: uuid.UUID
    relationship_type_key: str
    valid_from: Optional[datetime.date] = None
    valid_to: Optional[datetime.date] = None


class EntityRelationshipResponse(BaseModel):
    relationship_id: uuid.UUID
    relationship_type_key: str
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    is_current: bool
    valid_from: Optional[datetime.date]
    valid_to: Optional[datetime.date]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class EntityRelationshipListResponse(BaseModel):
    items: List[EntityRelationshipResponse]
    total: int
