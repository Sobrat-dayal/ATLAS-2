import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ResearchSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string.")
    start_date: Optional[datetime.date] = Field(default=None, description="Filter for research published on or after this date.")
    end_date: Optional[datetime.date] = Field(default=None, description="Filter for research published on or before this date.")
    limit: int = Field(default=50, ge=1, le=1000)

    model_config = ConfigDict(frozen=True)


class ResearchMetadataRequest(BaseModel):
    research_document_id: uuid.UUID = Field(..., description="The ID of the Research Document in ATLAS.")

    model_config = ConfigDict(frozen=True)
