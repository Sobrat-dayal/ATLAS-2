import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EconomicDataOrigin(BaseModel):
    provider_key: str = Field(...)
    upstream_source: str = Field(...)
    retrieved_at: datetime.datetime = Field(...)
    source_reference: Optional[str] = Field(default=None)

    @field_validator("retrieved_at", mode="after")
    @classmethod
    def validate_retrieved_at_timezone(cls, v: datetime.datetime) -> datetime.datetime:
        if v.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware.")
        return v.astimezone(datetime.timezone.utc)

    model_config = ConfigDict(frozen=True)
