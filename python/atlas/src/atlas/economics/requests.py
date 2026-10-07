import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.economics.enums import EconomicRevisionPolicy

class EconomicRevisionSelection(BaseModel):
    policy: EconomicRevisionPolicy = Field(...)
    as_of_date: Optional[datetime.date] = Field(default=None)

    @model_validator(mode="after")
    def validate_as_of(self) -> "EconomicRevisionSelection":
        if self.policy == EconomicRevisionPolicy.AS_OF:
            if self.as_of_date is None:
                raise ValueError("as_of_date is required when policy is AS_OF.")
        else:
            if self.as_of_date is not None:
                raise ValueError("as_of_date must be None when policy is not AS_OF.")
        return self

    model_config = ConfigDict(frozen=True)

class EconomicObservationsRequest(BaseModel):
    economic_series_id: uuid.UUID = Field(...)
    start_date: Optional[datetime.date] = Field(default=None)
    end_date: Optional[datetime.date] = Field(default=None)
    limit: Optional[int] = Field(default=None)
    revision_selection: EconomicRevisionSelection = Field(
        default_factory=lambda: EconomicRevisionSelection(policy=EconomicRevisionPolicy.LATEST_AVAILABLE)
    )

    @model_validator(mode="after")
    def validate_request_bounds(self) -> "EconomicObservationsRequest":
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("start_date cannot be after end_date.")
        if self.limit is not None:
            if self.limit <= 0 or self.limit > 10000:
                raise ValueError("limit must be between 1 and 10000.")
        
        has_range = self.start_date is not None or self.end_date is not None
        has_limit = self.limit is not None
        if not has_range and not has_limit:
            raise ValueError("Bounded request requires at least a date range or limit.")
        
        return self

    model_config = ConfigDict(frozen=True)

class LatestEconomicObservationsRequest(BaseModel):
    economic_series_ids: tuple[uuid.UUID, ...] = Field(...)
    as_of_date: Optional[datetime.date] = Field(default=None)

    @model_validator(mode="after")
    def validate_batch(self) -> "LatestEconomicObservationsRequest":
        if not self.economic_series_ids:
            raise ValueError("Batch must not be empty.")
        if len(self.economic_series_ids) > 100:
            raise ValueError("Batch limit is 100 series.")
        if len(set(self.economic_series_ids)) != len(self.economic_series_ids):
            raise ValueError("Duplicate economic_series_ids are not allowed.")
        return self

    model_config = ConfigDict(frozen=True)
