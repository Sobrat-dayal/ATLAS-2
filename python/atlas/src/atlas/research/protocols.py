from typing import Protocol

from atlas.research.capabilities import ResearchProviderCapabilities
from atlas.research.requests import ResearchMetadataRequest, ResearchSearchRequest
from atlas.research.responses import ResearchResponse


class ResearchProvider(Protocol):
    @property
    def research_capabilities(self) -> ResearchProviderCapabilities:
        ...

    async def get_research_metadata(self, request: ResearchMetadataRequest) -> ResearchResponse:
        ...

    async def search_research(self, request: ResearchSearchRequest) -> ResearchResponse:
        ...
