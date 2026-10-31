"""Mining Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_mining_asset(
    asset_id: str,
    name: str,
    country: str,
    commodity: str,
    latitude: float,
    longitude: float,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.OPEN_PIT_MINE,
    rom_tonnes_year: Optional[float] = None,
    refined_tonnes_year: Optional[float] = None,
    proved_reserves_tonnes: Optional[float] = None,
    source_id: str = "USGS_MRDS",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a mining asset preserving distinct reserves vs resources and run-of-mine metrics."""
    capacity_records: List[InfrastructureCapacityRecord] = []

    if rom_tonnes_year is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.RUN_OF_MINE_TONNES_YEAR,
                value=rom_tonnes_year,
                basis=CapacityBasis.NAMEPLATE,
                unit_str="tonnes/year",
            )
        )
    if refined_tonnes_year is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.REFINED_OUTPUT_TONNES_YEAR,
                value=refined_tonnes_year,
                basis=CapacityBasis.DESIGN,
                unit_str="tonnes/year",
            )
        )
    if proved_reserves_tonnes is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.PROVED_RESERVES_TONNES,
                value=proved_reserves_tonnes,
                basis=CapacityBasis.PERMITTED,
                unit_str="tonnes",
            )
        )

    properties: Dict[str, Any] = {
        "commodity": commodity,
    }

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.MINING,
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
