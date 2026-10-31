"""Ports and Maritime Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_port_facility(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    un_locode: Optional[str] = None,
    terminal_code: Optional[str] = None,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.PORT_TERMINAL,
    teu_capacity: Optional[float] = None,
    tonnes_capacity: Optional[float] = None,
    max_draft_meters: Optional[float] = None,
    berth_count: Optional[int] = None,
    parent_asset_id: Optional[str] = None,
    source_id: str = "IMO_GISIS",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a verified port or terminal asset with explicit UN/LOCODE vs Terminal ID separation (Fixture E)."""
    identifiers: Dict[str, str] = {}
    if un_locode:
        identifiers["UN_LOCODE"] = un_locode
    if terminal_code:
        identifiers["TERMINAL_CODE"] = terminal_code

    capacity_records: List[InfrastructureCapacityRecord] = []
    if teu_capacity is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.THROUGHPUT_TEU_YEAR,
                value=teu_capacity,
                basis=CapacityBasis.NAMEPLATE,
                unit_str="TEU/year",
            )
        )
    if tonnes_capacity is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.THROUGHPUT_TONNES_YEAR,
                value=tonnes_capacity,
                basis=CapacityBasis.DESIGN,
                unit_str="tonnes/year",
            )
        )
    if max_draft_meters is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.MAX_DRAFT_METERS,
                value=max_draft_meters,
                basis=CapacityBasis.DESIGN,
                unit_str="meters",
            )
        )
    if berth_count is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.BERTH_COUNT,
                value=float(berth_count),
                basis=CapacityBasis.DESIGN,
                unit_str="berths",
            )
        )

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.PORTS_MARITIME,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=GeographicPrecisionClass.EXACT_SITE,
        status=InfrastructureStatus.OPERATIONAL,
        parent_asset_id=parent_asset_id,
        capacity_records=capacity_records,
        identifiers=identifiers,
        source_id=source_id,
        source_license=source_license,
    )

