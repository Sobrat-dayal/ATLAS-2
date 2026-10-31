"""Logistics and Industrial Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_logistics_asset(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.DISTRIBUTION_CENTER,
    warehouse_volume_m3: Optional[float] = None,
    gross_sqft: Optional[float] = None,
    source_id: str = "GLOBAL_LOGISTICS_REGISTRY",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a logistics distribution center or bonded warehouse asset."""
    capacity_records: List[InfrastructureCapacityRecord] = []
    if warehouse_volume_m3 is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.WAREHOUSE_VOLUME_M3,
                value=warehouse_volume_m3,
                basis=CapacityBasis.DESIGN,
                unit_str="m3",
            )
        )
    if gross_sqft is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.GROSS_FLOOR_AREA_SQFT,
                value=gross_sqft,
                basis=CapacityBasis.DESIGN,
                unit_str="sqft",
            )
        )

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.LOGISTICS_INDUSTRIAL,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        capacity_records=capacity_records,
        source_id=source_id,
        source_license=source_license,
    )

