import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsDataOrigin(BaseModel):
    provider_id: str = Field(..., description="The unique identifier of the data provider (e.g., 'openbb', 'alphavantage').")
    extracted_at: datetime.datetime = Field(..., description="When the data was extracted from the provider.")
    provider_internal_id: Optional[str] = Field(default=None, description="The provider's internal identifier for this news item.")

    model_config = ConfigDict(frozen=True)
