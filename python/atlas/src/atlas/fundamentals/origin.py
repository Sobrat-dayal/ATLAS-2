import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FundamentalDataOrigin(BaseModel):
    """
    Represents the origin of a piece of fundamental data.
    """

    provider_key: str = Field(..., description="Stage 28 Provider key")
    upstream_source: Optional[str] = Field(default=None)
    retrieved_at: datetime = Field(...)
    source_document_id: Optional[uuid.UUID] = Field(default=None)
    source_filing_identifier: Optional[str] = Field(default=None)

    model_config = {"frozen": True}
