import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas.economics.models import EconomicSeries
from atlas.entities.models import Entity


class EconomicSeriesRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_economic_series(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, EconomicSeries]]:
        stmt = (
            select(Entity, EconomicSeries)
            .join(EconomicSeries, Entity.entity_id == EconomicSeries.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_economic_series_specialization(
        self,
        entity_id: uuid.UUID,
        series_kind: Optional[str] = None,
        frequency: Optional[str] = None,
        unit_label: Optional[str] = None,
        value_representation: Optional[str] = None,
        seasonal_adjustment: Optional[str] = None,
        scope_geographic_entity_id: Optional[uuid.UUID] = None,
    ) -> EconomicSeries:
        series = EconomicSeries(
            entity_id=entity_id,
            series_kind=series_kind,
            frequency=frequency,
            unit_label=unit_label,
            value_representation=value_representation,
            seasonal_adjustment=seasonal_adjustment,
            scope_geographic_entity_id=scope_geographic_entity_id,
        )
        self.session.add(series)
        return series
