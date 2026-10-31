"""Data Center Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_data_center_asset(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    it_load_mw: Optional[float] = None,
    total_power_mw: Optional[float] = None,
    gross_sqft: Optional[float] = None,
    white_space_sqft: Optional[float] = None,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.DATA_CENTER_FACILITY,
    parent_asset_id: Optional[str] = None,
    source_id: str = "DATACENTER_MAP",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a data center asset with strict distinction between IT load and total power."""
    capacity_records: List[InfrastructureCapacityRecord] = []

    # IT Equipment load
    if it_load_mw is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.DATA_CENTER_IT_LOAD_MW,
                value=it_load_mw,
                basis=CapacityBasis.DESIGN,
                unit_str="MW",
            )
        )

    # Total facility power (including cooling, PDU losses, etc.)
    if total_power_mw is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.DATA_CENTER_TOTAL_POWER_MW,
                value=total_power_mw,
                basis=CapacityBasis.NAMEPLATE,
                unit_str="MW",
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

    if white_space_sqft is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.WHITE_SPACE_SQFT,
                value=white_space_sqft,
                basis=CapacityBasis.DESIGN,
                unit_str="sqft",
            )
        )

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.DATA_CENTERS,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        parent_asset_id=parent_asset_id,
        capacity_records=capacity_records,
        source_id=source_id,
        source_license=source_license,
    )

