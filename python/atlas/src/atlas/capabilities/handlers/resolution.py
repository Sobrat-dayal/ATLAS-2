from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.capabilities.context import CapabilityExecutionContext
from atlas.resolution.schemas import EntityResolutionRequest, EntityResolutionResponse
from atlas.resolution.service import EntityResolutionService

def entity_resolve_factory(session: AsyncSession):
    service = EntityResolutionService(session)
    
    async def handler(context: CapabilityExecutionContext, input_data: EntityResolutionRequest) -> EntityResolutionResponse:
        return await service.resolve_entity(input_data)
        
    return handler
