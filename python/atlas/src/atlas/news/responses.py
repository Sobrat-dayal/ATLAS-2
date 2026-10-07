from pydantic import BaseModel, ConfigDict, Field

from atlas.news.articles import NewsArticle
from atlas.news.origin import NewsDataOrigin


class NewsResponse(BaseModel):
    origin: NewsDataOrigin = Field(...)
    articles: tuple[NewsArticle, ...] = Field(...)

    model_config = ConfigDict(frozen=True)
