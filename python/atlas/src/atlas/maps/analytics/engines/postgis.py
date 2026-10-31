"""PostGIS Spatial Aggregation Engine for H3 and Density Layers (Stage 131).

Aggregates PostGIS spatial point/polygon features into H3 hexagon cells,
computes metric statistics, calculates geodesic densities, and applies privacy controls.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from atlas.maps.analytics.domain import (
    AtlasH3Aggregate,
    SpatialAnalyticsQuery,
    SpatialAnalyticsResult,
    SpatialSummaryStatistics,
)
from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.density import compute_density
from atlas.maps.analytics.h3.indexing import lat_lng_to_cell
from atlas.maps.analytics.metrics import SpatialMetricRegistry, compute_metric_aggregation
from atlas.maps.analytics.privacy import SpatialPrivacyGovernor
from atlas.maps.analytics.temporal import filter_by_historical_as_of, get_temporal_bucket_key
from atlas.maps.domain import DataQualityStatus, LicensingPolicy


class PostGISSpatialAggregationEngine:
    """Performs spatial aggregation of geographic features into H3 cells."""

    def __init__(
        self,
        metric_registry: SpatialMetricRegistry,
        privacy_governor: SpatialPrivacyGovernor,
    ):
        self.metric_registry = metric_registry
        self.privacy_governor = privacy_governor

    def execute_query(
        self,
        query: SpatialAnalyticsQuery,
        features: List[Dict[str, Any]],
        dataset_version: str = "v1",
        licensing_policy: LicensingPolicy = LicensingPolicy.OPEN_DATA_CC_BY,
        attribution: str = "",
    ) -> SpatialAnalyticsResult:
        """Executes H3 spatial binning and aggregation over the provided features."""
        start_time = time.perf_counter()
        metric = self.metric_registry.validate_query(
            dataset_id=query.dataset_id,
            metric_id=query.metric_id,
            aggregation=query.aggregation,
        )

        # 1. Historical As-Of filtering (guarantees zero look-ahead bias)
        valid_features = filter_by_historical_as_of(
            features,
            as_of=query.historical_as_of,
            time_key="source_updated_at",
        )

        # 2. Viewport Bounding Box filtering
        if query.bounds:
            b = query.bounds
            filtered_by_bbox: List[Dict[str, Any]] = []
            for f in valid_features:
                coords = f.get("coordinates")
                if coords and len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    if b.west <= lon <= b.east and b.south <= lat <= b.north:
                        filtered_by_bbox.append(f)
            valid_features = filtered_by_bbox

        # 3. Categorical and Numeric filters
        if query.filters:
            filtered_by_attrs: List[Dict[str, Any]] = []
            for f in valid_features:
                props = f.get("properties", {})
                matches = True
                for k, v in query.filters.items():
                    if props.get(k) != v:
                        matches = False
                        break
                if matches:
                    filtered_by_attrs.append(f)
            valid_features = filtered_by_attrs

        # 4. Group by H3 cell (and temporal bucket if requested)
        cell_groups: Dict[str, List[Dict[str, Any]]] = {}
        for f in valid_features:
            coords = f.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            lon = float(coords[0])
            lat = float(coords[1])

            try:
                cell_id = lat_lng_to_cell(lat, lon, query.h3_resolution)
            except Exception:
                continue

            # Temporal bucket partition key if interval specified
            if query.time_bucket and "source_updated_at" in f:
                bucket_key = get_temporal_bucket_key(f["source_updated_at"], query.time_bucket)
                group_key = f"{cell_id}:{bucket_key}"
            else:
                group_key = cell_id

            if group_key not in cell_groups:
                cell_groups[group_key] = []
            cell_groups[group_key].append(f)

        # 5. Compute aggregation per group
        aggregates: List[AtlasH3Aggregate] = []
        all_values: List[float] = []

        for group_key, group_records in cell_groups.items():
            cell_id = group_key.split(":")[0]
            time_bucket = group_key.split(":")[1] if ":" in group_key else None

            # Extract numeric metric values
            raw_vals: List[Optional[float]] = []
            distinct_entities: List[str] = []
            weights: List[Optional[float]] = []

            for r in group_records:
                props = r.get("properties", {})
                val = props.get(query.metric_id)
                if val is not None:
                    try:
                        raw_vals.append(float(val))
                    except (ValueError, TypeError):
                        raw_vals.append(None)
                else:
                    raw_vals.append(None)

                # Entity tracking for distinct count (Fixture H)
                entity_id = props.get("entity_id") or props.get("feature_id") or r.get("feature_id")
                if entity_id:
                    distinct_entities.append(str(entity_id))

                if metric.weight_metric_id:
                    w = props.get(metric.weight_metric_id)
                    weights.append(float(w) if w is not None else 1.0)

            # Compute metric
            agg_result = compute_metric_aggregation(
                values=raw_vals,
                aggregation=query.aggregation,
                null_policy=metric.null_policy,
                weights=weights if weights else None,
                distinct_ids=distinct_entities if distinct_entities else None,
            )

            cell_area = get_cell_area_km2(cell_id)
            val = agg_result["value"]
            density_val = compute_density(val, cell_area)

            # Build aggregate object
            agg = AtlasH3Aggregate(
                h3_cell_id=cell_id,
                h3_resolution=query.h3_resolution,
                metric_id=query.metric_id,
                aggregation_method=query.aggregation,
                value=val,
                record_count=agg_result["record_count"],
                non_null_count=agg_result["non_null_count"],
                distinct_count=agg_result["distinct_count"],
                valid_weight_sum=agg_result["valid_weight_sum"],
                cell_area_km2=cell_area,
                density=density_val,
                unit=metric.unit,
                time_bucket=time_bucket,
                data_quality=DataQualityStatus.VERIFIED,
            )

            # Evaluate privacy suppression (k-anonymity)
            agg = self.privacy_governor.evaluate_aggregate_suppression(
                aggregate=agg,
                min_threshold=query.min_contributors,
            )

            aggregates.append(agg)
            if not agg.is_suppressed:
                all_values.append(agg.value)

        # Truncate if exceeding query limit
        is_truncated = len(aggregates) > query.result_limit
        if is_truncated:
            aggregates = aggregates[: query.result_limit]

        # 6. Compute summary statistics
        total_records = len(valid_features)
        total_cells = len(aggregates)
        suppressed_cells = sum(1 for a in aggregates if a.is_suppressed)

        sum_val = sum(all_values) if all_values else 0.0
        mean_val = (sum_val / len(all_values)) if all_values else 0.0
        min_val = min(all_values) if all_values else 0.0
        max_val = max(all_values) if all_values else 0.0

        summary = SpatialSummaryStatistics(
            total_records=total_records,
            total_cells=total_cells,
            suppressed_cells=suppressed_cells,
            sum_value=round(sum_val, 4),
            mean_value=round(mean_val, 4),
            min_value=round(min_val, 4),
            max_value=round(max_val, 4),
            unit=metric.unit,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return SpatialAnalyticsResult(
            query_id=f"sq-{int(time.time() * 1000)}",
            dataset_id=query.dataset_id,
            dataset_version=dataset_version,
            metric_id=query.metric_id,
            aggregation=query.aggregation,
            visualization_type=query.visualization_type,
            h3_resolution=query.h3_resolution,
            unit=metric.unit,
            aggregates=aggregates,
            summary=summary,
            bounds=query.bounds,
            time_scope={"bucket": query.time_bucket.value} if query.time_bucket else None,
            source_attribution=attribution,
            licensing_policy=licensing_policy,
            is_truncated=is_truncated,
            execution_time_ms=elapsed_ms,
        )
