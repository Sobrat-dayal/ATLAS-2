import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ResearchDataOrigin(BaseModel):
    provider_id: str = Field(..., description="The unique identifier of the data provider (e.g., 'openalex', 'arxiv').")
    extracted_at: datetime.datetime = Field(..., description="When the data was extracted from the provider.")
    provider_internal_id: Optional[str] = Field(default=None, description="The provider's internal identifier for this research item.")

    model_config = ConfigDict(frozen=True)
