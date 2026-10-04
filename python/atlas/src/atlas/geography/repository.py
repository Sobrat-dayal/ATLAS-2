import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas.entities.models import Entity
from atlas.geography.models import (
    Airport,
    Country,
    Exchange,
    Facility,
    GeographicEntity,
    Port,
)


class GeographicEntityRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_geographic_entity(self, entity_id: uuid.UUID) -> Optional[GeographicEntity]:
        return self.session.get(GeographicEntity, entity_id)

    def get_country(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, Country]]:
        stmt = (
            select(Entity, Country)
            .join(GeographicEntity, Entity.entity_id == GeographicEntity.entity_id)
            .join(Country, GeographicEntity.entity_id == Country.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def get_facility(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, Facility]]:
        stmt = (
            select(Entity, Facility)
            .join(GeographicEntity, Entity.entity_id == GeographicEntity.entity_id)
            .join(Facility, GeographicEntity.entity_id == Facility.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def get_port(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, Facility, Port]]:
        stmt = (
            select(Entity, Facility, Port)
            .join(GeographicEntity, Entity.entity_id == GeographicEntity.entity_id)
            .join(Facility, GeographicEntity.entity_id == Facility.entity_id)
            .join(Port, Facility.entity_id == Port.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def get_airport(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, Facility, Airport]]:
        stmt = (
            select(Entity, Facility, Airport)
            .join(GeographicEntity, Entity.entity_id == GeographicEntity.entity_id)
            .join(Facility, GeographicEntity.entity_id == Facility.entity_id)
            .join(Airport, Facility.entity_id == Airport.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def get_exchange(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, Exchange]]:
        stmt = (
            select(Entity, Exchange)
            .join(GeographicEntity, Entity.entity_id == GeographicEntity.entity_id)
            .join(Exchange, GeographicEntity.entity_id == Exchange.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_geographic_marker(self, entity_id: uuid.UUID) -> GeographicEntity:
        marker = GeographicEntity(entity_id=entity_id)
        self.session.add(marker)
        return marker

    def create_country_specialization(
        self, entity_id: uuid.UUID, country_kind: Optional[str] = None
    ) -> Country:
        country = Country(entity_id=entity_id, country_kind=country_kind)
        self.session.add(country)
        return country

    def create_facility_specialization(
        self,
        entity_id: uuid.UUID,
        country_entity_id: Optional[uuid.UUID] = None,
        region_name: Optional[str] = None,
        locality_name: Optional[str] = None,
        address_text: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        elevation_meters: Optional[float] = None,
    ) -> Facility:
        facility = Facility(
            entity_id=entity_id,
            country_entity_id=country_entity_id,
            region_name=region_name,
            locality_name=locality_name,
            address_text=address_text,
            latitude=latitude,
            longitude=longitude,
            elevation_meters=elevation_meters,
        )
        self.session.add(facility)
        return facility

    def create_port_specialization(
        self, entity_id: uuid.UUID, port_kind: Optional[str] = None
    ) -> Port:
        port = Port(entity_id=entity_id, port_kind=port_kind)
        self.session.add(port)
        return port

    def create_airport_specialization(
        self, entity_id: uuid.UUID, airport_kind: Optional[str] = None
    ) -> Airport:
        airport = Airport(entity_id=entity_id, airport_kind=airport_kind)
        self.session.add(airport)
        return airport

    def create_exchange_specialization(
        self,
        entity_id: uuid.UUID,
        country_entity_id: Optional[uuid.UUID] = None,
        exchange_kind: Optional[str] = None,
        timezone_name: Optional[str] = None,
    ) -> Exchange:
        exchange = Exchange(
            entity_id=entity_id,
            country_entity_id=country_entity_id,
            exchange_kind=exchange_kind,
            timezone_name=timezone_name,
        )
        self.session.add(exchange)
        return exchange
