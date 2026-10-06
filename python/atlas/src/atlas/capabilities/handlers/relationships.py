import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities.context import CapabilityExecutionContext
from atlas.relationships.schemas import RelationshipTypeResponse
from atlas.relationships.service import RelationshipService


class RelationshipTypeListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RelationshipTypeListOutput(BaseModel):
    types: list[RelationshipTypeResponse]


class EntityRelationshipsListInput(BaseModel):
    entity_id: uuid.UUID
    relationship_type_key: str | None = None
    is_current: bool | None = None
    limit: int = 100
    offset: int = 0
    model_config = ConfigDict(extra="forbid")


class EntityRelationshipsListOutput(BaseModel):
    items: list[Any]
    total: int
    model_config = ConfigDict(extra="allow")


def relationship_type_list_factory(session: AsyncSession):
    service = RelationshipService(session)

    async def handler(
        context: CapabilityExecutionContext, input_data: RelationshipTypeListInput
    ) -> RelationshipTypeListOutput:
        types = await service.get_all_system_types()
        return RelationshipTypeListOutput(types=types)

    return handler


def entity_relationships_list_factory(session: AsyncSession):
    service = RelationshipService(session)

    async def handler(
        context: CapabilityExecutionContext, input_data: EntityRelationshipsListInput
    ) -> EntityRelationshipsListOutput:
        items, total = await service.list_relationships(
            entity_id=input_data.entity_id,
            relationship_type_key=input_data.relationship_type_key,
            is_current=input_data.is_current,
            limit=input_data.limit,
            offset=input_data.offset,
        )
        return EntityRelationshipsListOutput(items=items, total=total)

    return handler
