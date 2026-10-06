import uuid

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.aliases.repository import AliasRepository
from atlas.aliases.schemas import AliasTypeResponse, EntityAliasResponse
from atlas.aliases.service import AliasService
from atlas.capabilities.context import CapabilityExecutionContext


class AliasTypeListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AliasTypeListOutput(BaseModel):
    types: list[AliasTypeResponse]


class EntityAliasesListInput(BaseModel):
    entity_id: uuid.UUID
    include_history: bool = False
    model_config = ConfigDict(extra="forbid")


class EntityAliasesListOutput(BaseModel):
    aliases: list[EntityAliasResponse]


def alias_type_list_factory(session: AsyncSession):
    repo = AliasRepository(session)
    service = AliasService(repo)

    async def handler(
        context: CapabilityExecutionContext, input_data: AliasTypeListInput
    ) -> AliasTypeListOutput:
        types = await service.list_alias_types()
        return AliasTypeListOutput(types=types)

    return handler


def entity_aliases_list_factory(session: AsyncSession):
    repo = AliasRepository(session)
    service = AliasService(repo)

    async def handler(
        context: CapabilityExecutionContext, input_data: EntityAliasesListInput
    ) -> EntityAliasesListOutput:
        aliases = await service.get_entity_aliases(input_data.entity_id)
        return EntityAliasesListOutput(aliases=aliases)

    return handler
