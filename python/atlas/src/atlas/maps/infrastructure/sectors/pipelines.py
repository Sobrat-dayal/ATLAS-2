"""Oil and Gas Physical Infrastructure Model and Adapters (Stage 133)."""

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


def create_pipeline_asset(
    asset_id: str,
    name: str,
    country: str,
    commodity: str,  # "crude_oil", "natural_gas", "refined_products", "lng"
    latitude: float,
    longitude: float,
    is_approximate_route: bool = True,
    asset_type: InfrastructureAssetType = InfrastructureAssetType.PIPELINE_ROUTE,
    diameter_inches: Optional[float] = None,
    length_km: Optional[float] = None,
    throughput_bpd: Optional[float] = None,
    throughput_mmcfd: Optional[float] = None,
    source_id: str = "GEM_PIPELINES",
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED,
) -> InfrastructureAsset:
    """Create a pipeline infrastructure asset with explicit approximate route qualification (Fixture H)."""
    capacity_records: List[InfrastructureCapacityRecord] = []
    if throughput_bpd is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.THROUGHPUT_BPD,
                value=throughput_bpd,
                basis=CapacityBasis.DESIGN,
                unit_str="bpd",
            )
        )
    if throughput_mmcfd is not None:
        capacity_records.append(
            InfrastructureCapacityRecord(
                metric=CapacityMetric.THROUGHPUT_MMCFD,
                value=throughput_mmcfd,
                basis=CapacityBasis.DESIGN,
                unit_str="MMcf/d",
            )
        )

    properties: Dict[str, Any] = {
        "commodity": commodity,
        "diameter_inches": diameter_inches,
        "length_km": length_km,
    }

    precision = (
        GeographicPrecisionClass.ROUTE_CORRIDOR
        if is_approximate_route
        else GeographicPrecisionClass.EXACT_SITE
    )

    return InfrastructureAsset(
        asset_id=asset_id,
        name=name,
        sector=InfrastructureSector.OIL_GAS,
        asset_type=asset_type,
        country=country,
        latitude=latitude,
        longitude=longitude,
        precision=precision,
        is_approximate_route=is_approximate_route,
        status=InfrastructureStatus.OPERATIONAL,
        capacity_records=capacity_records,
        source_id=source_id,
        source_license=source_license,
        properties=properties,
    )

