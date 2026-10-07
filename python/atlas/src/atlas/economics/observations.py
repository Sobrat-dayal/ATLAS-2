import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from atlas.economics.enums import EconomicObservationAvailability, EconomicRevisionStatus
from atlas.economics.numeric import CanonicalDecimal
from atlas.economics.periods import EconomicObservationPeriod


class EconomicObservation(BaseModel):
    economic_series_id: uuid.UUID = Field(...)
    period: EconomicObservationPeriod = Field(...)
    availability: EconomicObservationAvailability = Field(...)
    value: Optional[CanonicalDecimal] = Field(default=None)
    revision_status: EconomicRevisionStatus = Field(default=EconomicRevisionStatus.UNKNOWN)
    released_at: Optional[datetime.datetime] = Field(default=None)
    vintage_date: Optional[datetime.date] = Field(default=None)

    @field_validator("released_at", mode="after")
    @classmethod
    def validate_released_at_timezone(cls, v: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
        if v is not None:
            if v.tzinfo is None:
                raise ValueError("released_at must be timezone-aware.")
            return v.astimezone(datetime.timezone.utc)
        return v

    @model_validator(mode="after")
    def validate_availability_and_value(self) -> "EconomicObservation":
        if self.availability == EconomicObservationAvailability.AVAILABLE:
            if self.value is None:
                raise ValueError("value cannot be None when availability is AVAILABLE.")
        elif self.availability == EconomicObservationAvailability.MISSING:
            if self.value is not None:
                raise ValueError("value must be None when availability is MISSING.")
        return self

    model_config = ConfigDict(frozen=True)

class LatestEconomicObservationItem(BaseModel):
    economic_series_id: uuid.UUID = Field(...)
    observation: Optional[EconomicObservation] = Field(default=None)

    @model_validator(mode="after")
    def validate_identity_consistency(self) -> "LatestEconomicObservationItem":
        if self.observation is not None:
            if self.observation.economic_series_id != self.economic_series_id:
                raise ValueError("Observation economic_series_id must match item economic_series_id.")
        return self

    model_config = ConfigDict(frozen=True)
