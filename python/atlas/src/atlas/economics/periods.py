import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EconomicObservationPeriod(BaseModel):
    reference_date: datetime.date = Field(...)
    period_start: Optional[datetime.date] = Field(default=None)
    period_end: Optional[datetime.date] = Field(default=None)

    @model_validator(mode="after")
    def validate_period_boundaries(self) -> "EconomicObservationPeriod":
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("period_start and period_end must both be present or both be absent.")
        if self.period_start is not None and self.period_end is not None:
            if self.period_start > self.period_end:
                raise ValueError("period_start cannot be after period_end.")
        return self

    model_config = ConfigDict(frozen=True)
