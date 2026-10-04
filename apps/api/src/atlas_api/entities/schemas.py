import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class EntityTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    description: Optional[str] = None
    parent_key: Optional[str] = None


class EntityTypeListResponse(BaseModel):
    types: List[EntityTypeResponse]


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
