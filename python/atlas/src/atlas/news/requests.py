import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsLatestRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=1000)

    model_config = ConfigDict(frozen=True)


class NewsSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string.")
    start_date: Optional[datetime.datetime] = Field(default=None, description="Filter for articles published on or after this timestamp.")
    end_date: Optional[datetime.datetime] = Field(default=None, description="Filter for articles published on or before this timestamp.")
    limit: int = Field(default=50, ge=1, le=1000)

    model_config = ConfigDict(frozen=True)
