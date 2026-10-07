from typing import Protocol

from atlas.news.capabilities import NewsProviderCapabilities
from atlas.news.requests import NewsLatestRequest, NewsSearchRequest
from atlas.news.responses import NewsResponse


class NewsProvider(Protocol):
    @property
    def news_capabilities(self) -> NewsProviderCapabilities:
        ...

    async def get_latest_news(self, request: NewsLatestRequest) -> NewsResponse:
        ...

    async def search_news(self, request: NewsSearchRequest) -> NewsResponse:
        ...
