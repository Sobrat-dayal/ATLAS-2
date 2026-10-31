"""Railways Infrastructure Model and Adapters (Stage 133)."""

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


def create_rail_asset(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.INTERMODAL_RAIL_YARD,
    track_length_km: Optional[float] = None,
    gauge_mm: int = 1435,  # Standard gauge default
    electrified: bool = True,
    annual_freight_tonnes: Optional[float] = None,
    source_id: str = "OPEN_RAILWAY_MAP",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a railway infrastructure asset with explicit gauge and track length."""
    capacity_records: List[InfrastructureCapacityRecord] = []
    if track_length_km is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.TRACK_LENGTH_KM,
                value=track_length_km,
                basis=CapacityBasis.DESIGN,
                unit_str="km",
            )
        )
    if annual_freight_tonnes is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.ANNUAL_FREIGHT_TONNES,
                value=annual_freight_tonnes,
                basis=CapacityBasis.OPERATIONAL_PEAK,
                unit_str="tonnes/year",
            )
        )

    properties: Dict[str, Any] = {
        "gauge_mm": gauge_mm,
        "electrified": electrified,
    }

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.RAILWAYS,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        capacity_records=capacity_records,
        source_id=source_id,
        source_license=source_license,
        properties=properties,
    )

