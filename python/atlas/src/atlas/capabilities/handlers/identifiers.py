import uuid

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities.context import CapabilityExecutionContext
from atlas.identifiers.schemas import EntityIdentifierResponse, IdentifierSchemeResponse
from atlas.identifiers.service import IdentifierService


class IdentifierSchemeListInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IdentifierSchemeListOutput(BaseModel):
    schemes: list[IdentifierSchemeResponse]


class EntityIdentifiersListInput(BaseModel):
    entity_id: uuid.UUID
    include_history: bool = False
    model_config = ConfigDict(extra="forbid")


class EntityIdentifiersListOutput(BaseModel):
    identifiers: list[EntityIdentifierResponse]


def identifier_scheme_list_factory(session: AsyncSession):
    service = IdentifierService(session)

    async def handler(
        context: CapabilityExecutionContext, input_data: IdentifierSchemeListInput
    ) -> IdentifierSchemeListOutput:
        schemes = await service.list_identifier_schemes()
        return IdentifierSchemeListOutput(schemes=schemes)

    return handler


def entity_identifiers_list_factory(session: AsyncSession):
    service = IdentifierService(session)

    async def handler(
        context: CapabilityExecutionContext, input_data: EntityIdentifiersListInput
    ) -> EntityIdentifiersListOutput:
        identifiers = await service.get_entity_identifiers(
            input_data.entity_id, input_data.include_history
        )
        return EntityIdentifiersListOutput(identifiers=identifiers)

    return handler
