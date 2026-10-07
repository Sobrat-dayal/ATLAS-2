import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.economics.enums import EconomicRevisionPolicy
from atlas.economics.origin import EconomicDataOrigin
from atlas.economics.observations import EconomicObservation, LatestEconomicObservationItem

class EconomicObservationsResponse(BaseModel):
    economic_series_id: uuid.UUID = Field(...)
    origin: EconomicDataOrigin = Field(...)
    revision_policy: EconomicRevisionPolicy = Field(...)
    observations: tuple[EconomicObservation, ...] = Field(...)

    @model_validator(mode="after")
    def validate_observations(self) -> "EconomicObservationsResponse":
        for obs in self.observations:
            if obs.economic_series_id != self.economic_series_id:
                raise ValueError("Observation series ID does not match response series ID.")

        for i in range(1, len(self.observations)):
            prev = self.observations[i - 1]
            curr = self.observations[i]
            
            if curr.period.reference_date < prev.period.reference_date:
                raise ValueError("Observations must be ordered by reference_date ascending.")
            
            if curr.period.reference_date == prev.period.reference_date:
                if curr.vintage_date is not None and prev.vintage_date is not None:
                    if curr.vintage_date < prev.vintage_date:
                        raise ValueError("Observations with same reference date must be ordered by vintage_date ascending.")
                
                if self.revision_policy in (EconomicRevisionPolicy.LATEST_AVAILABLE, EconomicRevisionPolicy.AS_OF):
                    raise ValueError(f"Multiple observations for same reference date not allowed under {self.revision_policy.value} policy.")
                
                if curr == prev:
                    raise ValueError("Exact duplicate observations are not allowed.")

        return self

    model_config = ConfigDict(frozen=True)

class LatestEconomicObservationsResponse(BaseModel):
    origin: EconomicDataOrigin = Field(...)
    items: tuple[LatestEconomicObservationItem, ...] = Field(...)

    model_config = ConfigDict(frozen=True)
