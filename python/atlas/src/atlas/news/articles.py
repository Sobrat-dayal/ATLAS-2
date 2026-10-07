import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from atlas.news.origin import NewsDataOrigin


class NewsArticle(BaseModel):
    """
    A canonical, immutable representation of a News Article.
    Note: This is distinctly different from a News Event Entity which represents
    a real-world event (e.g., 'M&A Announcement') that is described by articles.
    """
    title: str = Field(..., description="The headline or title of the news article.")
    publisher: str = Field(..., description="The publisher or source of the article (e.g., 'Bloomberg', 'Reuters').")
    published_at: datetime.datetime = Field(..., description="The exact timestamp when the article was published.")
    url: Optional[HttpUrl] = Field(default=None, description="The URL to the original article.")
    summary: Optional[str] = Field(default=None, description="A brief summary or snippet of the article content.")
    authors: tuple[str, ...] = Field(default_factory=tuple, description="Authors of the article.")
    tags: tuple[str, ...] = Field(default_factory=tuple, description="Tags, keywords, or topics associated with the article.")
    origin: NewsDataOrigin = Field(..., description="The provenance information of the article data.")

    model_config = ConfigDict(frozen=True)
