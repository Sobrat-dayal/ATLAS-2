import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.capabilities.context import CapabilityExecutionContext
from atlas.entities import EntityService, EntityRepository

class EntityGetInput(BaseModel):
    entity_id: uuid.UUID
    model_config = ConfigDict(extra="forbid")

class EntityOutput(BaseModel):
    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EntityTypeListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

class EntityTypeOutput(BaseModel):
    key: str
    name: str
    description: str | None = None
    parent_key: str | None = None
    model_config = ConfigDict(from_attributes=True)

class EntityTypeListOutput(BaseModel):
    types: list[EntityTypeOutput]

def entity_get_factory(session: AsyncSession):
    repo = EntityRepository(session)
    service = EntityService(repo)
    
    async def handler(context: CapabilityExecutionContext, input_data: EntityGetInput) -> EntityOutput:
        entity = await service.get_entity(input_data.entity_id)
        return EntityOutput.model_validate(entity)
        
    return handler

def entity_type_list_factory(session: AsyncSession):
    repo = EntityRepository(session)
    service = EntityService(repo)
    
    async def handler(context: CapabilityExecutionContext, input_data: EntityTypeListInput) -> EntityTypeListOutput:
        types = await service.list_entity_types()
        return EntityTypeListOutput(types=[EntityTypeOutput.model_validate(t) for t in types])
        
    return handler
