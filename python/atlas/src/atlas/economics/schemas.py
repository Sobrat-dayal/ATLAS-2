import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from atlas.economics.types import (
    EconomicFrequency,
    EconomicSeriesKind,
    EconomicValueRepresentation,
    SeasonalAdjustment,
)


class EconomicSeriesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    series_kind: Optional[EconomicSeriesKind] = None
    frequency: Optional[EconomicFrequency] = None
    unit_label: Optional[str] = None
    value_representation: Optional[EconomicValueRepresentation] = None
    seasonal_adjustment: Optional[SeasonalAdjustment] = None
    scope_geographic_entity_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
