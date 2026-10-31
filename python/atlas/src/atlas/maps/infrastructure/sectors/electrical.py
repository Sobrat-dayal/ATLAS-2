"""Electricity Networks Infrastructure Model and Adapters (Stage 133)."""

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


def create_transmission_substation(
    asset_id: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    voltage_kv: float,
    capacity_mva: Optional[float] = None,
    source_id: str = "OPEN_INFRA_GRID",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a high-voltage electrical transmission substation."""
    capacity_records: List[InfrastructureCapacityRecord] = []
    if capacity_mva is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.POWER_MW,
                value=capacity_mva,
                basis=CapacityBasis.NAMEPLATE,
                unit_str="MVA",
            )
        )

    properties: Dict[str, Any] = {
        "voltage_kv": voltage_kv,
        "current_type": "AC",
    }

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.ELECTRICITY_NETWORKS,
        asset_type=InfrastructureAssetType.TRANSMISSION_SUBSTATION,
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

