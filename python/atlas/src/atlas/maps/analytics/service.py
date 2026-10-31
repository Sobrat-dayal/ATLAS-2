"""Atlas Spatial Analytics Service (Stage 131).

Coordinates analytical capabilities, metric validation, PostGIS spatial queries,
H3 hexagonal aggregations, regional comparisons, cell inspections, and privacy controls.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from atlas.maps.analytics.caching import generate_spatial_analytics_cache_key
from atlas.maps.analytics.domain import (
    MaterializationJob,
    RegionComparisonResult,
    SpatialAggregationMethod,
    SpatialAnalyticsQuery,
    SpatialAnalyticsResult,
    SpatialMetricDefinition,
    SpatialVisualizationType,
)
from atlas.maps.analytics.engines.postgis import PostGISSpatialAggregationEngine
from atlas.maps.analytics.engines.router import SpatialQueryRouter
from atlas.maps.analytics.errors import (
    SourceEntitlementRevokedError,
    UnauthorizedSpatialDatasetError,
)
from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.indexing import (
    cell_to_lat_lng,
    get_cell_resolution,
    is_pentagon,
    validate_cell_id,
)
from atlas.maps.analytics.materialization import MaterializationJobRegistry
from atlas.maps.analytics.metrics import SpatialMetricRegistry
from atlas.maps.analytics.privacy import SpatialPrivacyGovernor
from atlas.maps.domain import GeoBoundingBox


class AtlasSpatialAnalyticsService:
    """Master service providing high-performance spatial analytics over geographic datasets."""

    def __init__(
        self,
        metric_registry: Optional[SpatialMetricRegistry] = None,
        privacy_governor: Optional[SpatialPrivacyGovernor] = None,
        job_registry: Optional[MaterializationJobRegistry] = None,
    ):
        self.metric_registry = metric_registry or SpatialMetricRegistry()
        self.privacy_governor = privacy_governor or SpatialPrivacyGovernor()
        self.job_registry = job_registry or MaterializationJobRegistry()
        self.postgis_engine = PostGISSpatialAggregationEngine(
            self.metric_registry,
            self.privacy_governor,
        )
        self.router = SpatialQueryRouter(self.postgis_engine)

        # In-memory query cache
        self._cache: Dict[str, SpatialAnalyticsResult] = {}

        # Canonical features fixture for tests and default datasets
        self._mock_dataset_features: Dict[str, List[Dict[str, Any]]] = {}
        self._populate_canonical_analytics_features()

        # Source entitlement tracking
        self._revoked_sources: set[str] = set()

    def _populate_canonical_analytics_features(self) -> None:
        """Populates authentic reference financial centers for Stage 131 analytics."""
        self._mock_dataset_features["financial_centers_global"] = [
            {
                "feature_id": "fc-lon",
                "label": "City of London",
                "coordinates": [-0.09, 51.51],
                "properties": {
                    "entity_id": "BOE-001",
                    "observation_count": 1,
                    "market_capital_intensity": 150000000.0,
                    "liquidity_score": 96.5,
                    "trading_volume_weight": 2.5,
                },
                "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0, 0),
            },
            {
                "feature_id": "fc-ny",
                "label": "New York Financial District",
                "coordinates": [-74.01, 40.71],
                "properties": {
                    "entity_id": "FED-NY-001",
                    "observation_count": 1,
                    "market_capital_intensity": 320000000.0,
                    "liquidity_score": 99.0,
                    "trading_volume_weight": 4.0,
                },
                "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0, 0),
            },
            {
                "feature_id": "fc-tokyo",
                "label": "Tokyo Nihonbashi",
                "coordinates": [139.77, 35.68],
                "properties": {
                    "entity_id": "BOJ-001",
                    "observation_count": 1,
                    "market_capital_intensity": 180000000.0,
                    "liquidity_score": 92.0,
                    "trading_volume_weight": 2.0,
                },
                "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0, 0),
            },
            {
                "feature_id": "fc-frankfurt",
                "label": "Frankfurt Bankenviertel",
                "coordinates": [8.67, 50.11],
                "properties": {
                    "entity_id": "ECB-001",
                    "observation_count": 1,
                    "market_capital_intensity": 110000000.0,
                    "liquidity_score": 88.5,
                    "trading_volume_weight": 1.5,
                },
                "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0, 0),
            },
            {
                "feature_id": "fc-singapore",
                "label": "Singapore Marina Bay",
                "coordinates": [103.85, 1.28],
                "properties": {
                    "entity_id": "MAS-001",
                    "observation_count": 1,
                    "market_capital_intensity": 95000000.0,
                    "liquidity_score": 89.0,
                    "trading_volume_weight": 1.2,
                },
                "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0, 0),
            },
        ]

    def revoke_source_entitlement(self, source_id: str) -> None:
        """Revokes a source entitlement and invalidates relevant caches (Fixture L)."""
        self._revoked_sources.add(source_id)
        # Flush cache
        self._cache.clear()

    def get_capabilities(self) -> Dict[str, Any]:
        """Returns supported analytical visualization modes, aggregations, and H3 limits."""
        return {
            "supported_visualizations": [v.value for v in SpatialVisualizationType],
            "supported_aggregations": [a.value for a in SpatialAggregationMethod],
            "h3_min_resolution": 0,
            "h3_max_resolution": 15,
            "h3_recommended_viewport_resolutions": {
                "global": 3,
                "continental": 5,
                "country": 7,
                "metropolitan": 9,
                "neighborhood": 11,
            },
            "default_privacy_threshold": self.privacy_governor.default_min_threshold,
            "gpu_acceleration_supported": True,
        }

    def list_metrics(self, dataset_id: str) -> List[SpatialMetricDefinition]:
        """Lists approved analytical metrics for a given dataset."""
        return self.metric_registry.list_for_dataset(dataset_id)

    def query_analytics(
        self,
        query: SpatialAnalyticsQuery,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> SpatialAnalyticsResult:
        """Executes an authorized spatial analytics query with caching."""
        # 1. Authorization check
        if query.dataset_id.startswith("restricted_tenant_") and query.tenant_id != tenant_id:
            raise UnauthorizedSpatialDatasetError(query.dataset_id, user_id, tenant_id)

        # 2. Source entitlement check
        if query.dataset_id in self._revoked_sources:
            raise SourceEntitlementRevokedError(query.dataset_id, query.dataset_id)

        # 3. Check cache
        cache_key = generate_spatial_analytics_cache_key(
            query=query,
            dataset_version="v1",
            is_public_dataset=not query.dataset_id.startswith("private_"),
        )
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 4. Resolve features
        features = self._mock_dataset_features.get(query.dataset_id, [])

        # 5. Route and execute query
        result = self.router.route_and_execute(
            query=query,
            features=features,
            dataset_version="v1",
        )

        # 6. Store in cache
        self._cache[cache_key] = result
        return result

    def get_cell_details(
        self,
        cell_id: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns geometric, area, and metadata details for a specific H3 cell."""
        validate_cell_id(cell_id)
        res = get_cell_resolution(cell_id)
        area_km2 = get_cell_area_km2(cell_id)
        lat, lng = cell_to_lat_lng(cell_id)
        pentagon = is_pentagon(cell_id)

        return {
            "h3_cell_id": cell_id,
            "resolution": res,
            "cell_area_km2": round(area_km2, 4),
            "centroid": {"latitude": round(lat, 6), "longitude": round(lng, 6)},
            "is_pentagon": pentagon,
            "supported_drill_down": res < 15,
        }

    def compare_regions(
        self,
        dataset_id: str,
        metric_id: str,
        aggregation: SpatialAggregationMethod,
        region_a_name: str,
        region_a_bounds: GeoBoundingBox,
        region_b_name: str,
        region_b_bounds: GeoBoundingBox,
        h3_resolution: int = 6,
    ) -> RegionComparisonResult:
        """Compares spatial analytical statistics across two geographic regions."""
        query_a = SpatialAnalyticsQuery(
            dataset_id=dataset_id,
            metric_id=metric_id,
            aggregation=aggregation,
            visualization_type=SpatialVisualizationType.H3_HEXAGON,
            h3_resolution=h3_resolution,
            bounds=region_a_bounds,
        )
        query_b = SpatialAnalyticsQuery(
            dataset_id=dataset_id,
            metric_id=metric_id,
            aggregation=aggregation,
            visualization_type=SpatialVisualizationType.H3_HEXAGON,
            h3_resolution=h3_resolution,
            bounds=region_b_bounds,
        )

        result_a = self.query_analytics(query_a)
        result_b = self.query_analytics(query_b)

        val_a = result_a.summary.mean_value
        val_b = result_b.summary.mean_value
        abs_diff = round(abs(val_a - val_b), 4)

        rel_diff_pct: Optional[float] = None
        if val_b != 0:
            rel_diff_pct = round(((val_a - val_b) / abs(val_b)) * 100.0, 2)

        higher = region_a_name if val_a > val_b else (region_b_name if val_b > val_a else None)

        # Approximate surface areas of bounding boxes
        area_a = max(
            1.0,
            (region_a_bounds.east - region_a_bounds.west)
            * (region_a_bounds.north - region_a_bounds.south)
            * 111.0
            * 111.0,
        )
        area_b = max(
            1.0,
            (region_b_bounds.east - region_b_bounds.west)
            * (region_b_bounds.north - region_b_bounds.south)
            * 111.0
            * 111.0,
        )

        density_a = round(result_a.summary.sum_value / area_a, 4)
        density_b = round(result_b.summary.sum_value / area_b, 4)

        return RegionComparisonResult(
            region_a_name=region_a_name,
            region_b_name=region_b_name,
            metric_id=metric_id,
            unit=result_a.unit,
            region_a_summary=result_a.summary,
            region_b_summary=result_b.summary,
            absolute_difference=abs_diff,
            relative_difference_pct=rel_diff_pct,
            higher_region=higher,
            area_normalized_a=density_a,
            area_normalized_b=density_b,
        )

    # Job Management
    def create_materialization_job(
        self,
        dataset_id: str,
        metric_id: str,
        h3_resolution: int,
    ) -> MaterializationJob:
        return self.job_registry.create_job(
            dataset_id=dataset_id,
            dataset_revision="v1",
            metric_id=metric_id,
            h3_resolution=h3_resolution,
        )

    def get_job(self, job_id: str) -> MaterializationJob:
        return self.job_registry.get_job(job_id)

    def cancel_job(self, job_id: str) -> MaterializationJob:
        return self.job_registry.cancel_job(job_id)
