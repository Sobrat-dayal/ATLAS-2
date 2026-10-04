import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas.economics.errors import (
    EconomicSeriesDataInconsistentError,
    EconomicSeriesNotFoundError,
    InvalidEconomicFrequencyError,
    InvalidEconomicScopeError,
    InvalidEconomicSeriesKindError,
    InvalidSeasonalAdjustmentError,
    InvalidValueRepresentationError,
)
from atlas.economics.repository import EconomicSeriesRepository
from atlas.economics.schemas import EconomicSeriesResponse
from atlas.economics.types import (
    EconomicFrequency,
    EconomicSeriesKind,
    EconomicValueRepresentation,
    SeasonalAdjustment,
)
from atlas.economics.validation import validate_unit_label
from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.geography.repository import GeographicEntityRepository


class EconomicSeriesService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = EconomicSeriesRepository(session)
        self.entity_service = EntityService(session)
        self.entity_repository = EntityRepository(session)
        self.geo_repository = GeographicEntityRepository(session)

    def create_economic_series(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        series_kind: Optional[str] = None,
        frequency: Optional[str] = None,
        unit_label: Optional[str] = None,
        value_representation: Optional[str] = None,
        seasonal_adjustment: Optional[str] = None,
        scope_geographic_entity_id: Optional[uuid.UUID] = None,
    ) -> EconomicSeriesResponse:
        
        if series_kind is not None:
            try:
                EconomicSeriesKind(series_kind)
            except ValueError:
                raise InvalidEconomicSeriesKindError(f"Invalid series_kind: {series_kind}")

        if frequency is not None:
            try:
                EconomicFrequency(frequency)
            except ValueError:
                raise InvalidEconomicFrequencyError(f"Invalid frequency: {frequency}")

        if value_representation is not None:
            try:
                EconomicValueRepresentation(value_representation)
            except ValueError:
                raise InvalidValueRepresentationError(
                    f"Invalid value_representation: {value_representation}"
                )

        if seasonal_adjustment is not None:
            try:
                SeasonalAdjustment(seasonal_adjustment)
            except ValueError:
                raise InvalidSeasonalAdjustmentError(
                    f"Invalid seasonal_adjustment: {seasonal_adjustment}"
                )

        unit_label = validate_unit_label(unit_label)

        if scope_geographic_entity_id is not None:
            geo_entity = self.geo_repository.get_geographic_entity(scope_geographic_entity_id)
            if not geo_entity:
                raise InvalidEconomicScopeError(
                    f"Geographic scope {scope_geographic_entity_id} not found."
                )

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.ECONOMIC_SERIES,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            series = self.repository.create_economic_series_specialization(
                entity_id=entity.entity_id,
                series_kind=series_kind,
                frequency=frequency,
                unit_label=unit_label,
                value_representation=value_representation,
                seasonal_adjustment=seasonal_adjustment,
                scope_geographic_entity_id=scope_geographic_entity_id,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return EconomicSeriesResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            series_kind=series.series_kind,
            frequency=series.frequency,
            unit_label=series.unit_label,
            value_representation=series.value_representation,
            seasonal_adjustment=series.seasonal_adjustment,
            scope_geographic_entity_id=series.scope_geographic_entity_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def get_economic_series(self, entity_id: uuid.UUID) -> EconomicSeriesResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise EconomicSeriesNotFoundError(f"Economic Series {entity_id} not found.")

        if entity.entity_type != EntityTypeKey.ECONOMIC_SERIES:
            raise EconomicSeriesNotFoundError(f"Entity {entity_id} is not an Economic Series.")

        series_tuple = self.repository.get_economic_series(entity_id)
        if not series_tuple:
            raise EconomicSeriesDataInconsistentError(
                f"Economic Series {entity_id} missing specialization row."
            )

        _, series = series_tuple
        
        return EconomicSeriesResponse.model_validate(
            {
                **entity.__dict__,
                "series_kind": series.series_kind,
                "frequency": series.frequency,
                "unit_label": series.unit_label,
                "value_representation": series.value_representation,
                "seasonal_adjustment": series.seasonal_adjustment,
                "scope_geographic_entity_id": series.scope_geographic_entity_id,
            }
        )
