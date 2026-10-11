from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities.context import CapabilityExecutionContext
from atlas.search.models import GlobalSearchRequest, GlobalSearchResponse
from atlas.search.service import GlobalSearchService
from atlas.search.repository import GlobalSearchRepository
from atlas.search.settings import GlobalSearchSettings


def search_entities_factory(session: AsyncSession):
    settings = GlobalSearchSettings()
    repo = GlobalSearchRepository(session, settings)
    service = GlobalSearchService(repo, settings)

    async def handler(
        context: CapabilityExecutionContext, input_data: GlobalSearchRequest
    ) -> GlobalSearchResponse:
        return await service.search_entities(input_data)

    return handler
