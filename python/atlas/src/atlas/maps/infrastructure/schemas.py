"""Pydantic V2 Request and Response Schemas for Physical Infrastructure (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InfrastructureAssetQuery(BaseModel):
    """Query parameters for asset search."""

    categories: Optional[List[str]] = None
    types: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    company_ids: Optional[List[str]] = None
    operator_ids: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    capacity_metric: Optional[str] = None
    capacity_min: Optional[float] = None
    capacity_max: Optional[float] = None
    historical_as_of: Optional[str] = None
    source_ids: Optional[List[str]] = None
    limit: int = Field(default=200, ge=1, le=1000)


class SpatialQueryRequest(BaseModel):
    """Bounded geographic bounding box query."""

    min_lng: float = Field(..., ge=-180.0, le=180.0)
    min_lat: float = Field(..., ge=-90.0, le=90.0)
    max_lng: float = Field(..., ge=-180.0, le=180.0)
    max_lat: float = Field(..., ge=-90.0, le=90.0)
    sector: Optional[str] = None
    limit: int = Field(default=200, ge=1, le=1000)


class AssetCompareRequest(BaseModel):
    """Payload to compare multiple infrastructure assets."""

    asset_ids: List[str] = Field(..., min_length=1, max_length=10)


class NetworkQueryRequest(BaseModel):
    """Bounded topology traversal request."""

    start_node_id: str
    max_hops: Optional[int] = Field(default=5, ge=1, le=10)
    only_verified: bool = True


class NetworkPathRequest(BaseModel):
    """Point-to-point shortest verified path query."""

    start_node_id: str
    target_node_id: str
    only_verified: bool = True


class H3AggregateRequest(BaseModel):
    """H3 Hexagonal aggregation query."""

    resolution: int = Field(default=7, ge=3, le=10)
    sector: Optional[str] = None
    country: Optional[str] = None


class RegionalSummaryRequest(BaseModel):
    """Regional profile query."""

    region_name: str = "Regional Summary"
    country: Optional[str] = None


class InfrastructureCapacityRecordSchema(BaseModel):
    metric: str
    value: float
    basis: str
    unit_str: str
    reporting_year: Optional[int] = None
    evidence_source: Optional[str] = None
    notes: Optional[str] = None


class InfrastructureEntityLinkSchema(BaseModel):
    entity_id: str
    entity_name: str
    role: str
    ownership_pct: Optional[float] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    evidence_source: Optional[str] = None


class InfrastructureAssetResponse(BaseModel):
    asset_id: str
    name: str
    sector: str
    asset_type: str
    country: str
    region: Optional[str] = None
    latitude: float
    longitude: float
    geometry: Dict[str, Any] = Field(default_factory=dict)
    precision: str
    is_approximate_route: bool
    status: str
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    parent_asset_id: Optional[str] = None
    child_asset_ids: List[str] = Field(default_factory=list)
    capacity_records: List[InfrastructureCapacityRecordSchema] = Field(default_factory=list)
    entity_links: List[InfrastructureEntityLinkSchema] = Field(default_factory=list)
    identifiers: Dict[str, str] = Field(default_factory=dict)
    source_id: str
    source_license: str
    is_private: bool
    tenant_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class InfrastructureAssetListResponse(BaseModel):
    count: int
    total_records: int
    assets: List[Dict[str, Any]]
    query_timestamp: str

