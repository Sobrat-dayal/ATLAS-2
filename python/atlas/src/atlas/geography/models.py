import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class GeographicEntity(Base):
    __tablename__ = "geographic_entities"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )


class Country(Base):
    __tablename__ = "countries"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("geographic_entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    country_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)


class Facility(Base):
    __tablename__ = "facilities"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("geographic_entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    country_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("countries.entity_id", ondelete="SET NULL"), nullable=True, index=True
    )
    region_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    locality_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    address_text: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    elevation_meters: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_facility_coord_pair",
        ),
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_facility_lat_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_facility_lon_range"),
    )


class Port(Base):
    __tablename__ = "ports"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    port_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)


class Airport(Base):
    __tablename__ = "airports"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    airport_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)


class Exchange(Base):
    __tablename__ = "exchanges"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("geographic_entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    country_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("countries.entity_id", ondelete="SET NULL"), nullable=True, index=True
    )
    exchange_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    timezone_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
