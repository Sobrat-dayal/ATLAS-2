import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IdentifierSchemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    category: str
    scope_policy: str
    normalization_strategy: str
    case_sensitive: bool
    max_length: int
    is_system: bool


class EntityIdentifierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    identifier_id: uuid.UUID
    scheme_key: str
    value: str
    scope_entity_id: Optional[uuid.UUID]
    namespace: Optional[str]
    is_current: bool
    valid_from: Optional[date]
    valid_to: Optional[date]
