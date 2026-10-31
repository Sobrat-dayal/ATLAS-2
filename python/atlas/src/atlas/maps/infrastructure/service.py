"""Central Orchestration Service for ATLAS Physical Infrastructure Intelligence (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from atlas.maps.infrastructure.analytics.company_exposure import compute_company_infrastructure_exposure
from atlas.maps.infrastructure.analytics.comparison import compare_infrastructure_assets
from atlas.maps.infrastructure.analytics.h3_infrastructure import aggregate_infrastructure_to_h3
from atlas.maps.infrastructure.analytics.regional import compute_regional_infrastructure_summary
from atlas.maps.infrastructure.assets.registry import asset_registry
from atlas.maps.infrastructure.domain import (
    CapacityMetric,
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureNetwork,
    InfrastructureSector,
    InfrastructureStatus,
)
from atlas.maps.infrastructure.networks.queries import BoundedNetworkQueryEngine
from atlas.maps.infrastructure.networks.registry import network_registry


class AtlasInfrastructureService:
    """Institutional service coordinating physical infrastructure intelligence, topology, and security."""

    def __init__(self) -> None:
        self.asset_registry = asset_registry
        self.network_registry = network_registry

    def get_supported_categories(self) -> Dict[str, Any]:
        """Return taxonomy of supported physical infrastructure sectors and asset types."""
        sectors_info = []
        for sector in InfrastructureSector:
            types_in_sector = [
                at.value for at in InfrastructureAssetType
            ]
            sectors_info.append(
                {
                    "sector": sector.value,
                    "name": sector.value.replace("_", " ").title(),
                }
            )

        return {
            "sectors": sectors_info,
            "total_sectors": len(sectors_info),
        }

    def list_datasets(self) -> List[Dict[str, Any]]:
        """Return registered infrastructure source datasets with licensing metadata."""
        return [
            {
                "source_id": "IMO_GISIS",
                "name": "IMO Global Integrated Shipping Information System",
                "coverage": "Global Ports and Maritime",
                "license": "commercial_allowed",
            },
            {
                "source_id": "OURAIRPORTS",
                "name": "OurAirports Official Global Aviation Registry",
                "coverage": "Worldwide Airports and Runways",
                "license": "commercial_allowed",
            },
            {
                "source_id": "GEM_POWER_US",
                "name": "Global Energy Monitor Power Plant Tracker",
                "coverage": "Utility-scale Power Generation",
                "license": "commercial_allowed",
            },
            {
                "source_id": "GEM_PIPELINES",
                "name": "Global Energy Monitor Oil and Gas Pipeline Tracker",
                "coverage": "Transmission Pipelines",
                "license": "commercial_allowed",
            },
            {
                "source_id": "USGS_MRDS",
                "name": "USGS Mineral Resources Data System",
                "coverage": "Mines and Mineral Processing",
                "license": "commercial_allowed",
            },
            {
                "source_id": "ACADEMIC_RESEARCH_SURVEY",
                "name": "Academic Mineral Reserve Geological Survey",
                "coverage": "Regional Exploration",
                "license": "non_commercial_only",
            },
        ]

    def list_assets(
        self,
        sector: Optional[InfrastructureSector] = None,
        asset_type: Optional[InfrastructureAssetType] = None,
        country: Optional[str] = None,
        company_id: Optional[str] = None,
        operator_id: Optional[str] = None,
        status: Optional[InfrastructureStatus] = None,
        min_capacity: Optional[float] = None,
        max_capacity: Optional[float] = None,
        capacity_metric: Optional[CapacityMetric] = None,
        as_of_date: Optional[str] = None,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        actor_tenant_id: Optional[str] = None,
        is_commercial_context: bool = False,
        limit: int = 200,
    ) -> List[InfrastructureAsset]:
        """Search physical infrastructure assets."""
        return self.asset_registry.list_assets(
            sector=sector,
            asset_type=asset_type,
            country=country,
            company_id=company_id,
            operator_id=operator_id,
            status=status,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            capacity_metric=capacity_metric,
            as_of_date=as_of_date,
            bbox=bbox,
            actor_tenant_id=actor_tenant_id,
            is_commercial_context=is_commercial_context,
            limit=limit,
        )

    def get_asset(
        self,
        asset_id: str,
        actor_tenant_id: Optional[str] = None,
        is_commercial_context: bool = False,
    ) -> InfrastructureAsset:
        """Get individual asset details with security enforcement."""
        return self.asset_registry.get_asset(
            asset_id=asset_id,
            actor_tenant_id=actor_tenant_id,
            is_commercial_context=is_commercial_context,
        )

    def get_asset_history(
        self,
        asset_id: str,
        actor_tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve historical state transitions for an asset."""
        asset = self.get_asset(asset_id, actor_tenant_id=actor_tenant_id)
        return [h.to_dict() for h in asset.status_history]

    def get_asset_relationships(
        self,
        asset_id: str,
        actor_tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve verified corporate entity links for an asset."""
        asset = self.get_asset(asset_id, actor_tenant_id=actor_tenant_id)
        return [l.to_dict() for l in asset.entity_links]

    def spatial_query(
        self,
        min_lng: float,
        min_lat: float,
        max_lng: float,
        max_lat: float,
        sector: Optional[InfrastructureSector] = None,
        actor_tenant_id: Optional[str] = None,
        limit: int = 200,
    ) -> List[InfrastructureAsset]:
        """Perform bounded bounding box query."""
        return self.list_assets(
            sector=sector,
            bbox=(min_lng, min_lat, max_lng, max_lat),
            actor_tenant_id=actor_tenant_id,
            limit=limit,
        )

    def compare_assets(
        self,
        asset_ids: List[str],
        actor_tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compare multiple assets side-by-side."""
        assets = [self.get_asset(aid, actor_tenant_id=actor_tenant_id) for aid in asset_ids]
        return compare_infrastructure_assets(assets)

    def list_networks(
        self,
        sector: Optional[InfrastructureSector] = None,
        country: Optional[str] = None,
        actor_tenant_id: Optional[str] = None,
    ) -> List[InfrastructureNetwork]:
        """List networks visible to the actor."""
        return self.network_registry.list_networks(
            sector=sector,
            country=country,
            actor_tenant_id=actor_tenant_id,
        )

    def get_network(
        self,
        network_id: str,
        actor_tenant_id: Optional[str] = None,
    ) -> InfrastructureNetwork:
        """Get network metadata and topology."""
        return self.network_registry.get_network(
            network_id=network_id,
            actor_tenant_id=actor_tenant_id,
        )

    def query_network_subgraph(
        self,
        network_id: str,
        start_node_id: str,
        max_hops: Optional[int] = None,
        only_verified: bool = True,
        actor_tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query bounded reachable subgraph."""
        network = self.get_network(network_id, actor_tenant_id=actor_tenant_id)
        engine = BoundedNetworkQueryEngine(network)
        result = engine.get_reachable_subgraph(
            start_node_id=start_node_id,
            max_hops=max_hops,
            only_verified=only_verified,
        )
        # Convert nodes and edges to dicts
        result["nodes"] = [n.to_dict() for n in result["nodes"]]
        result["edges"] = [e.to_dict() for e in result["edges"]]
        return result

    def find_network_path(
        self,
        network_id: str,
        start_node_id: str,
        target_node_id: str,
        only_verified: bool = True,
        actor_tenant_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find verified path between two nodes."""
        network = self.get_network(network_id, actor_tenant_id=actor_tenant_id)
        engine = BoundedNetworkQueryEngine(network)
        result = engine.find_shortest_path(
            start_node_id=start_node_id,
            target_node_id=target_node_id,
            only_verified=only_verified,
        )
        if result and "path_edges" in result:
            result["path_edges"] = [e.to_dict() for e in result["path_edges"]]
        return result

    def aggregate_h3(
        self,
        resolution: int = 7,
        sector: Optional[InfrastructureSector] = None,
        country: Optional[str] = None,
        actor_tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Aggregate infrastructure assets to H3 cells."""
        assets = self.list_assets(
            sector=sector,
            country=country,
            actor_tenant_id=actor_tenant_id,
            limit=5000,
        )
        return aggregate_infrastructure_to_h3(
            assets=assets,
            resolution=resolution,
            revoked_sources=self.asset_registry._revoked_source_ids,
        )

    def get_company_infrastructure(
        self,
        company_id: str,
        actor_tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze corporate infrastructure exposure."""
        all_assets = self.list_assets(actor_tenant_id=actor_tenant_id, limit=5000)
        return compute_company_infrastructure_exposure(company_id=company_id, assets=all_assets)

    def get_regional_summary(
        self,
        region_name: str = "Global Infrastructure Overview",
        country: Optional[str] = None,
        actor_tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Aggregate regional profile across sectors."""
        assets = self.list_assets(country=country, actor_tenant_id=actor_tenant_id, limit=5000)
        return compute_regional_infrastructure_summary(assets=assets, region_name=region_name)


infrastructure_service = AtlasInfrastructureService()
