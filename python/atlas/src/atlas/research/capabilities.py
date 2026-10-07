from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ResearchProviderOperation(StrEnum):
    GET_METADATA = "get_metadata"
    SEARCH = "search"


class ResearchProviderCapabilities(BaseModel):
    operations: frozenset[ResearchProviderOperation] = Field(default_factory=frozenset)

    model_config = ConfigDict(frozen=True)
