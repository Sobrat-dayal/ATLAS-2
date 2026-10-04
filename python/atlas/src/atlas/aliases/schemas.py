import uuid
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AliasTypeResponse(BaseModel):
    key: str
    name: str
    description: Optional[str]
    category: str
    normalization_strategy: str
    is_system: bool
    
    model_config = ConfigDict(from_attributes=True)


class EntityAliasResponse(BaseModel):
    alias_id: uuid.UUID
    alias_type: str
    value: str
    language_code: Optional[str]
    is_current: bool
    valid_from: Optional[datetime.date]
    valid_to: Optional[datetime.date]
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            alias_id=obj.alias_id,
            alias_type=obj.alias_type_key,
            value=obj.value,
            language_code=obj.language_code,
            is_current=obj.is_current,
            valid_from=obj.valid_from,
            valid_to=obj.valid_to,
        )
    
class EntityAliasListResponse(BaseModel):
    aliases: list[EntityAliasResponse]
