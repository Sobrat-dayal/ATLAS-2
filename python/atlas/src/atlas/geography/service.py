import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.geography.errors import (
    CountryNotFoundError,
    GeographicEntityDataInconsistentError,
    GeographicEntityNotFoundError,
    InvalidAirportKindError,
    InvalidCountryKindError,
    InvalidExchangeKindError,
    InvalidPortKindError,
)
from atlas.geography.repository import GeographicEntityRepository
from atlas.geography.schemas import (
    AirportResponse,
    CountryResponse,
    ExchangeResponse,
    FacilityResponse,
    PortResponse,
)
from atlas.geography.types import AirportKind, CountryKind, ExchangeKind, PortKind
from atlas.geography.validation import validate_coordinates, validate_timezone


class GeographicEntityService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = GeographicEntityRepository(session)
        self.entity_repository = EntityRepository(session)
        self.entity_service = EntityService(session)

    def _validate_country_exists(self, country_entity_id: Optional[uuid.UUID]):
        if country_entity_id is not None:
            country = self.repository.get_country(country_entity_id)
            if not country:
                raise CountryNotFoundError(f"Country {country_entity_id} not found.")

    def create_country(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        country_kind: Optional[str] = None,
    ) -> CountryResponse:
        if country_kind is not None:
            try:
                CountryKind(country_kind)
            except ValueError:
                raise InvalidCountryKindError(f"Invalid country_kind: {country_kind}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.COUNTRY,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            self.repository.create_geographic_marker(entity.entity_id)
            country = self.repository.create_country_specialization(
                entity.entity_id, country_kind=country_kind
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return CountryResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            country_kind=country.country_kind,
        )

    def create_facility(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        country_entity_id: Optional[uuid.UUID] = None,
        region_name: Optional[str] = None,
        locality_name: Optional[str] = None,
        address_text: Optional[str] = None,
        latitude: Optional[Decimal] = None,
        longitude: Optional[Decimal] = None,
        elevation_meters: Optional[Decimal] = None,
    ) -> FacilityResponse:
        latitude, longitude = validate_coordinates(latitude, longitude)
        self._validate_country_exists(country_entity_id)

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.FACILITY,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            self.repository.create_geographic_marker(entity.entity_id)
            facility = self.repository.create_facility_specialization(
                entity_id=entity.entity_id,
                country_entity_id=country_entity_id,
                region_name=region_name,
                locality_name=locality_name,
                address_text=address_text,
                latitude=latitude,
                longitude=longitude,
                elevation_meters=elevation_meters,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return FacilityResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            country_entity_id=facility.country_entity_id,
            region_name=facility.region_name,
            locality_name=facility.locality_name,
            address_text=facility.address_text,
            latitude=facility.latitude,
            longitude=facility.longitude,
            elevation_meters=facility.elevation_meters,
        )

    def create_port(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        country_entity_id: Optional[uuid.UUID] = None,
        region_name: Optional[str] = None,
        locality_name: Optional[str] = None,
        address_text: Optional[str] = None,
        latitude: Optional[Decimal] = None,
        longitude: Optional[Decimal] = None,
        elevation_meters: Optional[Decimal] = None,
        port_kind: Optional[str] = None,
    ) -> PortResponse:
        latitude, longitude = validate_coordinates(latitude, longitude)
        self._validate_country_exists(country_entity_id)

        if port_kind is not None:
            try:
                PortKind(port_kind)
            except ValueError:
                raise InvalidPortKindError(f"Invalid port_kind: {port_kind}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.PORT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            self.repository.create_geographic_marker(entity.entity_id)
            facility = self.repository.create_facility_specialization(
                entity_id=entity.entity_id,
                country_entity_id=country_entity_id,
                region_name=region_name,
                locality_name=locality_name,
                address_text=address_text,
                latitude=latitude,
                longitude=longitude,
                elevation_meters=elevation_meters,
            )
            port = self.repository.create_port_specialization(
                entity_id=entity.entity_id, port_kind=port_kind
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return PortResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            country_entity_id=facility.country_entity_id,
            region_name=facility.region_name,
            locality_name=facility.locality_name,
            address_text=facility.address_text,
            latitude=facility.latitude,
            longitude=facility.longitude,
            elevation_meters=facility.elevation_meters,
            port_kind=port.port_kind,
        )

    def create_airport(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        country_entity_id: Optional[uuid.UUID] = None,
        region_name: Optional[str] = None,
        locality_name: Optional[str] = None,
        address_text: Optional[str] = None,
        latitude: Optional[Decimal] = None,
        longitude: Optional[Decimal] = None,
        elevation_meters: Optional[Decimal] = None,
        airport_kind: Optional[str] = None,
    ) -> AirportResponse:
        latitude, longitude = validate_coordinates(latitude, longitude)
        self._validate_country_exists(country_entity_id)

        if airport_kind is not None:
            try:
                AirportKind(airport_kind)
            except ValueError:
                raise InvalidAirportKindError(f"Invalid airport_kind: {airport_kind}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.AIRPORT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            self.repository.create_geographic_marker(entity.entity_id)
            facility = self.repository.create_facility_specialization(
                entity_id=entity.entity_id,
                country_entity_id=country_entity_id,
                region_name=region_name,
                locality_name=locality_name,
                address_text=address_text,
                latitude=latitude,
                longitude=longitude,
                elevation_meters=elevation_meters,
            )
            airport = self.repository.create_airport_specialization(
                entity_id=entity.entity_id, airport_kind=airport_kind
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return AirportResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            country_entity_id=facility.country_entity_id,
            region_name=facility.region_name,
            locality_name=facility.locality_name,
            address_text=facility.address_text,
            latitude=facility.latitude,
            longitude=facility.longitude,
            elevation_meters=facility.elevation_meters,
            airport_kind=airport.airport_kind,
        )

    def create_exchange(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        country_entity_id: Optional[uuid.UUID] = None,
        exchange_kind: Optional[str] = None,
        timezone_name: Optional[str] = None,
    ) -> ExchangeResponse:
        self._validate_country_exists(country_entity_id)
        timezone_name = validate_timezone(timezone_name)

        if exchange_kind is not None:
            try:
                ExchangeKind(exchange_kind)
            except ValueError:
                raise InvalidExchangeKindError(f"Invalid exchange_kind: {exchange_kind}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.EXCHANGE,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            self.repository.create_geographic_marker(entity.entity_id)
            exchange = self.repository.create_exchange_specialization(
                entity_id=entity.entity_id,
                country_entity_id=country_entity_id,
                exchange_kind=exchange_kind,
                timezone_name=timezone_name,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return ExchangeResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            country_entity_id=exchange.country_entity_id,
            exchange_kind=exchange.exchange_kind,
            timezone_name=exchange.timezone_name,
        )

    def get_geographic_entity(
        self, entity_id: uuid.UUID
    ) -> CountryResponse | FacilityResponse | PortResponse | AirportResponse | ExchangeResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise GeographicEntityNotFoundError(f"Entity {entity_id} not found.")

        # Ensure it has geographic marker
        geo_marker = self.repository.get_geographic_entity(entity_id)
        if not geo_marker:
            raise GeographicEntityNotFoundError(f"Entity {entity_id} is not geographic.")

        if entity.entity_type == EntityTypeKey.COUNTRY:
            country_tuple = self.repository.get_country(entity_id)
            if not country_tuple:
                raise GeographicEntityDataInconsistentError(
                    f"Country {entity_id} specialization missing."
                )
            _, country = country_tuple
            return CountryResponse.model_validate(
                {**entity.__dict__, "country_kind": country.country_kind}
            )

        elif entity.entity_type == EntityTypeKey.FACILITY:
            facility_tuple = self.repository.get_facility(entity_id)
            if not facility_tuple:
                raise GeographicEntityDataInconsistentError(
                    f"Facility {entity_id} specialization missing."
                )
            _, facility = facility_tuple
            return FacilityResponse.model_validate(
                {
                    **entity.__dict__,
                    "country_entity_id": facility.country_entity_id,
                    "region_name": facility.region_name,
                    "locality_name": facility.locality_name,
                    "address_text": facility.address_text,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude,
                    "elevation_meters": facility.elevation_meters,
                }
            )

        elif entity.entity_type == EntityTypeKey.PORT:
            port_tuple = self.repository.get_port(entity_id)
            if not port_tuple:
                raise GeographicEntityDataInconsistentError(
                    f"Port {entity_id} specialization missing."
                )
            _, facility, port = port_tuple
            return PortResponse.model_validate(
                {
                    **entity.__dict__,
                    "country_entity_id": facility.country_entity_id,
                    "region_name": facility.region_name,
                    "locality_name": facility.locality_name,
                    "address_text": facility.address_text,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude,
                    "elevation_meters": facility.elevation_meters,
                    "port_kind": port.port_kind,
                }
            )

        elif entity.entity_type == EntityTypeKey.AIRPORT:
            airport_tuple = self.repository.get_airport(entity_id)
            if not airport_tuple:
                raise GeographicEntityDataInconsistentError(
                    f"Airport {entity_id} specialization missing."
                )
            _, facility, airport = airport_tuple
            return AirportResponse.model_validate(
                {
                    **entity.__dict__,
                    "country_entity_id": facility.country_entity_id,
                    "region_name": facility.region_name,
                    "locality_name": facility.locality_name,
                    "address_text": facility.address_text,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude,
                    "elevation_meters": facility.elevation_meters,
                    "airport_kind": airport.airport_kind,
                }
            )

        elif entity.entity_type == EntityTypeKey.EXCHANGE:
            exchange_tuple = self.repository.get_exchange(entity_id)
            if not exchange_tuple:
                raise GeographicEntityDataInconsistentError(
                    f"Exchange {entity_id} specialization missing."
                )
            _, exchange = exchange_tuple
            return ExchangeResponse.model_validate(
                {
                    **entity.__dict__,
                    "country_entity_id": exchange.country_entity_id,
                    "exchange_kind": exchange.exchange_kind,
                    "timezone_name": exchange.timezone_name,
                }
            )

        raise GeographicEntityNotFoundError(
            f"Entity {entity_id} type {entity.entity_type} not supported as geographic."
        )
