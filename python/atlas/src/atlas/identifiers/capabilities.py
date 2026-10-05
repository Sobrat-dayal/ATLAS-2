import uuid
from typing import List

from pydantic import Field
from atlas.capabilities.models import CapabilityInput, CapabilityOutput, CapabilityDefinition, CapabilityContext
from atlas.capabilities.registry import registry
from atlas.identifiers.schemas import EntityIdentifierResponse, IdentifierSchemeResponse
from atlas.identifiers.service import IdentifierService
from atlas.entities.service import EntityService
from fastapi import HTTPException, status

class GetIdentifierSchemesInput(CapabilityInput):
    pass

class GetIdentifierSchemesOutput(CapabilityOutput):
    schemes: List[IdentifierSchemeResponse]

GET_IDENTIFIER_SCHEMES = CapabilityDefinition(
    name="atlas.identifiers.get_schemes.v1",
    description="List all available identifier schemes.",
    input_type=GetIdentifierSchemesInput,
    output_type=GetIdentifierSchemesOutput
)

async def handle_get_identifier_schemes(context: CapabilityContext, input: GetIdentifierSchemesInput) -> GetIdentifierSchemesOutput:
    service = IdentifierService(context.db_session)
    schemes = await service.list_identifier_schemes()
    return GetIdentifierSchemesOutput(schemes=schemes)

registry.register(GET_IDENTIFIER_SCHEMES, handle_get_identifier_schemes)


class GetEntityIdentifiersInput(CapabilityInput):
    entity_id: uuid.UUID
    include_history: bool = False

class GetEntityIdentifiersOutput(CapabilityOutput):
    identifiers: List[EntityIdentifierResponse]

GET_ENTITY_IDENTIFIERS = CapabilityDefinition(
    name="atlas.identifiers.get_entity_identifiers.v1",
    description="Get identifiers for a specific entity.",
    input_type=GetEntityIdentifiersInput,
    output_type=GetEntityIdentifiersOutput
)

async def handle_get_entity_identifiers(context: CapabilityContext, input: GetEntityIdentifiersInput) -> GetEntityIdentifiersOutput:
    entity_service = EntityService(context.db_session)
    identifier_service = IdentifierService(context.db_session)
    
    entity = await entity_service.get_entity(input.entity_id)
    if not entity:
        raise ValueError("Entity not found") # Or use a specific error
        
    identifiers = await identifier_service.get_entity_identifiers(input.entity_id, input.include_history)
    return GetEntityIdentifiersOutput(identifiers=identifiers)

registry.register(GET_ENTITY_IDENTIFIERS, handle_get_entity_identifiers)
