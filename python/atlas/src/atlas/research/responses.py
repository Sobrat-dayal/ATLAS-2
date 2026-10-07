from pydantic import BaseModel, ConfigDict, Field

from atlas.research.metadata import ResearchMetadata
from atlas.research.origin import ResearchDataOrigin


class ResearchResponse(BaseModel):
    origin: ResearchDataOrigin = Field(...)
    documents: tuple[ResearchMetadata, ...] = Field(...)

    model_config = ConfigDict(frozen=True)
