"""FastAPI Router for ATLAS Global Physical Infrastructure Intelligence (Stage 133).

Provides endpoints for infrastructure asset directories, capacity queries, network topology,
bounded graph traversals, spatial queries, H3 hexagonal aggregations, and regional summaries.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, List, Optional

from atlas.maps.infrastructure.domain import (
    CapacityMetric,
    InfrastructureAssetType,
    InfrastructureSector,
    InfrastructureStatus,
)
from atlas.maps.infrastructure.errors import (
    AssetNotFoundError,
    CommercialUseProhibitedError,
    CycleDetectedInNetworkError,
    EntitlementRevokedError,
    IncompatibleCapacityUnitError,
    InfrastructureDomainError,
    InvalidHistoricalAsOfError,
    InvalidTopologyError,
    NetworkNotFoundError,
    SensitiveAssetAccessDeniedError,
    TraversalDepthExceededError,
)
from atlas.maps.infrastructure.schemas import (
    AssetCompareRequest,
    H3AggregateRequest,
    InfrastructureAssetQuery,
    NetworkPathRequest,
    NetworkQueryRequest,
    RegionalSummaryRequest,
    SpatialQueryRequest,
)
from atlas.maps.infrastructure.service import infrastructure_service
from fastapi import APIRouter, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infrastructure", tags=["Maps Physical Infrastructure"])


@router.get("/categories")
async def get_infrastructure_categories() -> Dict[str, Any]:
    """Retrieve supported infrastructure sectors and categories."""
    return infrastructure_service.get_supported_categories()


@router.get("/datasets")
async def get_infrastructure_datasets() -> List[Dict[str, Any]]:
    """Retrieve registered infrastructure datasets with licensing terms."""
    return infrastructure_service.list_datasets()


@router.get("/assets")
async def list_infrastructure_assets(
    sector: Optional[str] = Query(None, description="Filter by sector enum"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    country: Optional[str] = Query(None, description="ISO country code"),
    company_id: Optional[str] = Query(None, description="Linked company ID"),
    operator_id: Optional[str] = Query(None, description="Operating entity ID"),
    status: Optional[str] = Query(None, description="Operational status"),
    min_capacity: Optional[float] = Query(None, description="Minimum capacity"),
    max_capacity: Optional[float] = Query(None, description="Maximum capacity"),
    capacity_metric: Optional[str] = Query(None, description="Specific capacity metric"),
    historical_as_of: Optional[str] = Query(None, description="Point-in-time date YYYY-MM-DD"),
    actor_tenant_id: Optional[str] = Query(None, description="Tenant context"),
    is_commercial: bool = Query(False, description="Whether query runs in commercial context"),
    limit: int = Query(200, ge=1, le=1000),
) -> Dict[str, Any]:
    """Search global infrastructure assets with multi-parameter filtering."""
    try:
        sector_enum = InfrastructureSector(sector) if sector else None
        type_enum = InfrastructureAssetType(asset_type) if asset_type else None
        status_enum = InfrastructureStatus(status) if status else None
        metric_enum = CapacityMetric(capacity_metric) if capacity_metric else None

        assets = infrastructure_service.list_assets(
            sector=sector_enum,
            asset_type=type_enum,
            country=country,
            company_id=company_id,
            operator_id=operator_id,
            status=status_enum,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            capacity_metric=metric_enum,
            as_of_date=historical_as_of,
            actor_tenant_id=actor_tenant_id,
            is_commercial_context=is_commercial,
            limit=limit,
        )

        return {
            "count": len(assets),
            "assets": [a.to_dict() for a in assets],
            "query_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    except InvalidHistoricalAsOfError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/assets/{asset_id}")
async def get_infrastructure_asset(
    asset_id: str,
    actor_tenant_id: Optional[str] = Query(None),
    is_commercial: bool = Query(False),
) -> Dict[str, Any]:
    """Retrieve details for a single infrastructure asset."""
    try:
        asset = infrastructure_service.get_asset(
            asset_id=asset_id,
            actor_tenant_id=actor_tenant_id,
            is_commercial_context=is_commercial,
        )
        return asset.to_dict()
    except AssetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except EntitlementRevokedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except CommercialUseProhibitedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.get("/assets/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    actor_tenant_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """Retrieve historical status revisions for an asset."""
    try:
        return infrastructure_service.get_asset_history(asset_id=asset_id, actor_tenant_id=actor_tenant_id)
    except AssetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.get("/assets/{asset_id}/sources")
async def get_asset_sources(
    asset_id: str,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Retrieve evidence sources and licensing details for an asset."""
    try:
        asset = infrastructure_service.get_asset(asset_id=asset_id, actor_tenant_id=actor_tenant_id)
        return {
            "asset_id": asset.asset_id,
            "source_id": asset.source_id,
            "source_license": asset.source_license.value,
            "precision": asset.precision.value,
            "is_approximate_route": asset.is_approximate_route,
            "identifiers": asset.identifiers,
        }
    except AssetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.get("/assets/{asset_id}/relationships")
async def get_asset_relationships(
    asset_id: str,
    actor_tenant_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """Retrieve verified corporate linkages (owners, operators) for an asset."""
    try:
        return infrastructure_service.get_asset_relationships(asset_id=asset_id, actor_tenant_id=actor_tenant_id)
    except AssetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.post("/assets/spatial-query")
async def spatial_query_assets(
    req: SpatialQueryRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Perform bounded spatial bounding box search."""
    try:
        sector_enum = InfrastructureSector(req.sector) if req.sector else None
        assets = infrastructure_service.spatial_query(
            min_lng=req.min_lng,
            min_lat=req.min_lat,
            max_lng=req.max_lng,
            max_lat=req.max_lat,
            sector=sector_enum,
            actor_tenant_id=actor_tenant_id,
            limit=req.limit,
        )
        return {
            "count": len(assets),
            "assets": [a.to_dict() for a in assets],
            "bbox": [req.min_lng, req.min_lat, req.max_lng, req.max_lat],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/assets/compare")
async def compare_assets(
    req: AssetCompareRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Compare multiple infrastructure assets side-by-side."""
    try:
        return infrastructure_service.compare_assets(
            asset_ids=req.asset_ids,
            actor_tenant_id=actor_tenant_id,
        )
    except AssetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.get("/networks")
async def list_networks(
    sector: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    actor_tenant_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List infrastructure networks available to actor."""
    sector_enum = InfrastructureSector(sector) if sector else None
    networks = infrastructure_service.list_networks(
        sector=sector_enum,
        country=country,
        actor_tenant_id=actor_tenant_id,
    )
    return [n.to_dict() for n in networks]


@router.get("/networks/{network_id}")
async def get_network(
    network_id: str,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Retrieve network metadata, nodes, and edges."""
    try:
        network = infrastructure_service.get_network(
            network_id=network_id,
            actor_tenant_id=actor_tenant_id,
        )
        data = network.to_dict()
        data["nodes"] = [n.to_dict() for n in network.nodes]
        data["edges"] = [e.to_dict() for e in network.edges]
        return data
    except NetworkNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except EntitlementRevokedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.post("/networks/{network_id}/query")
async def query_network(
    network_id: str,
    req: NetworkQueryRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Traverse bounded reachable subgraph from a starting node."""
    try:
        return infrastructure_service.query_network_subgraph(
            network_id=network_id,
            start_node_id=req.start_node_id,
            max_hops=req.max_hops,
            only_verified=req.only_verified,
            actor_tenant_id=actor_tenant_id,
        )
    except NetworkNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except TraversalDepthExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except InvalidTopologyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.post("/networks/{network_id}/connections")
async def find_network_connection(
    network_id: str,
    req: NetworkPathRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Find verified path between two nodes in a network."""
    try:
        path_result = infrastructure_service.find_network_path(
            network_id=network_id,
            start_node_id=req.start_node_id,
            target_node_id=req.target_node_id,
            only_verified=req.only_verified,
            actor_tenant_id=actor_tenant_id,
        )
        if not path_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No verified connection found between '{req.start_node_id}' and '{req.target_node_id}'.",
            )
        return path_result
    except NetworkNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except SensitiveAssetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.post("/aggregates")
async def get_h3_aggregates(
    req: H3AggregateRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Aggregate physical infrastructure to H3 hexagonal cells."""
    try:
        sector_enum = InfrastructureSector(req.sector) if req.sector else None
        cells = infrastructure_service.aggregate_h3(
            resolution=req.resolution,
            sector=sector_enum,
            country=req.country,
            actor_tenant_id=actor_tenant_id,
        )
        return {
            "resolution": req.resolution,
            "cell_count": len(cells),
            "cells": cells,
        }
    except EntitlementRevokedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/companies/{company_id}/assets")
async def get_company_infrastructure(
    company_id: str,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Retrieve corporate infrastructure portfolio and exposure."""
    return infrastructure_service.get_company_infrastructure(
        company_id=company_id,
        actor_tenant_id=actor_tenant_id,
    )


@router.post("/regional-summary")
async def get_regional_summary(
    req: RegionalSummaryRequest,
    actor_tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Retrieve regional infrastructure summary."""
    return infrastructure_service.get_regional_summary(
        region_name=req.region_name,
        country=req.country,
        actor_tenant_id=actor_tenant_id,
    )
