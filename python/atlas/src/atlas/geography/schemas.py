import datetime
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from atlas.geography.types import AirportKind, CountryKind, ExchangeKind, PortKind


class BaseGeographicEntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CountryResponse(BaseGeographicEntityResponse):
    country_kind: Optional[CountryKind] = None


class FacilityResponse(BaseGeographicEntityResponse):
    country_entity_id: Optional[uuid.UUID] = None
    region_name: Optional[str] = None
    locality_name: Optional[str] = None
    address_text: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    elevation_meters: Optional[Decimal] = None


class PortResponse(FacilityResponse):
    port_kind: Optional[PortKind] = None


class AirportResponse(FacilityResponse):
    airport_kind: Optional[AirportKind] = None


class ExchangeResponse(BaseGeographicEntityResponse):
    country_entity_id: Optional[uuid.UUID] = None
    exchange_kind: Optional[ExchangeKind] = None
    timezone_name: Optional[str] = None
