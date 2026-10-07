from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class NewsProviderOperation(StrEnum):
    GET_LATEST = "get_latest"
    SEARCH = "search"


class NewsProviderCapabilities(BaseModel):
    operations: frozenset[NewsProviderOperation] = Field(default_factory=frozenset)

    model_config = ConfigDict(frozen=True)
