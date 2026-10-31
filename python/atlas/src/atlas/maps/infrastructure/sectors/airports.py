"""Airports and Aviation Physical Infrastructure Model and Adapters (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from atlas.maps.infrastructure.domain import (
    CapacityBasis,
    CapacityMetric,
    GeographicPrecisionClass,
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureCapacityRecord,
    InfrastructureSector,
    InfrastructureStatus,
    LicensingClass,
)


def create_airport_facility(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    icao_code: Optional[str] = None,
    iata_code: Optional[str] = None,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.AIRPORT,
    passengers_per_year: Optional[float] = None,
    cargo_tonnes_year: Optional[float] = None,
    runway_count: Optional[int] = None,
    source_id: str = "OURAIRPORTS",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a verified airport asset preserving ICAO vs IATA semantics and missing throughput (Fixture K)."""
    identifiers: Dict[str, str] = {}
    if icao_code:
        identifiers["ICAO"] = icao_code
    if iata_code:
        identifiers["IATA"] = iata_code

    capacity_records: List[InfrastructureCapacityRecord] = []
    if passengers_per_year is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.PASSENGERS_YEAR,
                value=passengers_per_year,
                basis=CapacityBasis.OPERATIONAL_PEAK,
                unit_str="passengers/year",
            )
        )
    if cargo_tonnes_year is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.CARGO_TONNES_YEAR,
                value=cargo_tonnes_year,
                basis=CapacityBasis.DESIGN,
                unit_str="tonnes/year",
            )
        )
    if runway_count is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.RUNWAY_COUNT,
                value=float(runway_count),
                basis=CapacityBasis.DESIGN,
                unit_str="runways",
            )
        )

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.AIRPORTS_AVIATION,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        capacity_records=capacity_records,
        identifiers=identifiers,
        source_id=source_id,
        source_license=source_license,
    )
