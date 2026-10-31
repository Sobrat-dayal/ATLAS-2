"""Power Generation Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_power_plant(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    primary_fuel: str,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.POWER_PLANT,
    capacity_mw: Optional[float] = None,
    capacity_basis: CapacityBasis = CapacityBasis.NAMEPLATE,
    storage_mwh: Optional[float] = None,
    parent_asset_id: Optional[str] = None,
    child_asset_ids: Optional[List[str]] = None,
    source_id: str = "GEM_POWER",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a power generation facility or unit with strict MW vs MWh dimensional separation (Fixtures A & B)."""
    capacity_records: List[InfrastructureCapacityRecord] = []

    if capacity_mw is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.POWER_MW,
                value=capacity_mw,
                basis=capacity_basis,
                unit_str="MW",
            )
        )

    # Store battery / hydro storage capacity strictly as Energy (MWh), never added to Power (MW) (Fixture B)
    if storage_mwh is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.ENERGY_MWH,
                value=storage_mwh,
                basis=capacity_basis,
                unit_str="MWh",
            )
        )

    properties: Dict[str, Any] = {
        "primary_fuel": primary_fuel,
    }

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.POWER_GENERATION,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        parent_asset_id=parent_asset_id,
        child_asset_ids=child_asset_ids or [],
        capacity_records=capacity_records,
        source_id=source_id,
        source_license=source_license,
        properties=properties,
    )
