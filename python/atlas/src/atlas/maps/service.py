"""Master Service Coordinator for ATLAS Maps V1 (Stage 129).

Coordinates spatial queries, proximity calculations, MVT vector tile generation,
feature inspection, basemap management, and authorization enforcement.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple

from atlas.maps.datasets.registry import dataset_registry
from atlas.maps.domain import (
    GeoFeature,
    LicensingPolicy,
)
from atlas.maps.errors import (
    MapDatasetAccessDeniedError,
    MapFeatureAccessDeniedError,
    MapFeatureNotFoundError,
    MapLayerAccessDeniedError,
    MapLayerNotFoundError,
    MapSpatialQueryTooLargeError,
)
from atlas.maps.layers.registry import layer_registry
from atlas.maps.layers.styles import BASEMAP_ATTRIBUTION, list_basemap_styles
from atlas.maps.spatial.bounding_boxes import (
    bboxes_intersect,
    point_in_bbox,
    validate_bounding_box,
)
from atlas.maps.spatial.coordinates import validate_coordinates
from atlas.maps.spatial.distance import (
    is_within_radius_meters,
)
from atlas.maps.tiles.caching import tile_cache_manager
from atlas.maps.tiles.coordinates import tile_bounds_epsg4326, validate_tile_xyz
from atlas.maps.tiles.mvt import encode_vector_tile_layer

MAX_QUERY_FEATURES_LIMIT = 5000


class AtlasMapsService:
    """Master geospatial service implementing the core platform mapping contracts."""

    def get_runtime_config(self) -> Dict[str, Any]:
        """Returns approved runtime map configuration."""
        return {
            "default_camera": {
                "longitude": 10.0,
                "latitude": 25.0,
                "zoom": 1.8,
                "bearing": 0.0,
                "pitch": 0.0,
                "projection": "mercator",
            },
            "canonical_crs": "EPSG:4326",
            "tile_projection": "EPSG:3857",
            "attribution": BASEMAP_ATTRIBUTION,
            "default_style_id": "atlas-dark",
            "supported_styles": [s.style_id for s in list_basemap_styles()],
            "version": "1.0.0",
        }

    def list_styles(self) -> List[Dict[str, Any]]:
        return [
            {
                "style_id": s.style_id,
                "display_name": s.display_name,
                "provider_id": s.provider_id,
                "style_url": s.style_url,
                "attribution": s.attribution,
                "license_reference": s.license_reference,
                "is_dark": s.is_dark,
                "is_available": s.is_available,
                "max_zoom": s.max_zoom,
            }
            for s in list_basemap_styles()
        ]

    def list_layers(
        self, user_id: Optional[str] = None, tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        layers = layer_registry.list_layers()
        results = []
        for layer in layers:
            ds = dataset_registry.get_dataset(layer.dataset_id)
            if ds and (
                ds.is_public
                or ds.owner_user_id == user_id
                or (tenant_id and ds.tenant_id == tenant_id)
            ):
                results.append(
                    {
                        "layer_id": layer.layer_id,
                        "dataset_id": layer.dataset_id,
                        "layer_name": layer.layer_name,
                        "geometry_type": layer.geometry_type.value,
                        "source_type": layer.source_type,
                        "default_visibility": layer.default_visibility,
                        "default_opacity": layer.default_opacity,
                        "min_zoom": layer.min_zoom,
                        "max_zoom": layer.max_zoom,
                        "display_order": layer.display_order,
                        "category": layer.category,
                        "license_reference": layer.license_reference,
                    }
                )
        return results

    def query_features(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
        dataset_ids: Optional[List[str]] = None,
        layer_ids: Optional[List[str]] = None,
        zoom: float = 2.0,
        limit: int = 500,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Performs bounded spatial query with antimeridian handling and authorization."""
        bbox = validate_bounding_box(west, south, east, north)

        target_datasets = set()
        if dataset_ids:
            target_datasets.update(dataset_ids)
        if layer_ids:
            for lid in layer_ids:
                layer_obj = layer_registry.get_layer(lid)
                if layer_obj:
                    target_datasets.add(layer_obj.dataset_id)

        if not target_datasets:
            # Default to all authorized public datasets
            target_datasets = {
                ds.dataset_id
                for ds in dataset_registry.list_datasets(user_id=user_id, tenant_id=tenant_id)
            }

        matched_features: List[GeoFeature] = []
        source_manifests: List[Dict[str, Any]] = []

        for ds_id in target_datasets:
            ds = dataset_registry.get_dataset(ds_id)
            if not ds:
                continue

            # Check permissions
            if not ds.is_public:
                if ds.owner_user_id != user_id and not (tenant_id and ds.tenant_id == tenant_id):
                    raise MapDatasetAccessDeniedError(ds_id, user_id=user_id)

            features = dataset_registry.list_features(ds_id)
            for f in features:
                # Point containment or Bbox intersection
                if f.bounding_box:
                    if bboxes_intersect(bbox, f.bounding_box):
                        matched_features.append(f)
                else:
                    if point_in_bbox(f.coordinates[0], f.coordinates[1], bbox):
                        matched_features.append(f)

            source_manifests.append(
                {
                    "source_id": ds.source_id,
                    "dataset_id": ds.dataset_id,
                    "version": ds.source_version,
                    "attribution": ds.attribution,
                    "license": ds.licensing_policy.value,
                    "data_quality": ds.data_quality_status.value,
                }
            )

        truncated = len(matched_features) > limit
        if len(matched_features) > MAX_QUERY_FEATURES_LIMIT:
            raise MapSpatialQueryTooLargeError(len(matched_features), MAX_QUERY_FEATURES_LIMIT)

        result_features = matched_features[:limit]

        return {
            "type": "FeatureCollection",
            "features": [f.to_geojson_feature() for f in result_features],
            "result_count": len(result_features),
            "total_matches": len(matched_features),
            "truncated": truncated,
            "bounds": bbox.to_list(),
            "source_manifest": source_manifests,
            "coordinate_reference_system": "EPSG:4326",
            "queried_at": datetime.datetime.utcnow().isoformat() + "Z",
        }

    def query_nearby(
        self,
        center_lon: float,
        center_lat: float,
        radius_meters: float,
        dataset_ids: Optional[List[str]] = None,
        limit: int = 50,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Performs metric proximity query in meters (CRITICAL UNIT RULE: Degrees != Meters)."""
        v_lon, v_lat = validate_coordinates(center_lon, center_lat)

        target_datasets = dataset_ids or ["atlas.reference.financial_centers"]
        results: List[Tuple[GeoFeature, float]] = []

        for ds_id in target_datasets:
            ds = dataset_registry.get_dataset(ds_id)
            if not ds:
                continue

            if not ds.is_public and ds.owner_user_id != user_id:
                if not (tenant_id and ds.tenant_id == tenant_id):
                    raise MapDatasetAccessDeniedError(ds_id, user_id=user_id)

            features = dataset_registry.list_features(ds_id)
            for f in features:
                # Check point distance
                if f.geometry_type.value == "Point":
                    pt_lon, pt_lat = f.coordinates[0], f.coordinates[1]
                    within, dist_m = is_within_radius_meters(
                        pt_lon, pt_lat, v_lon, v_lat, radius_meters
                    )
                    if within:
                        results.append((f, dist_m))

        results.sort(key=lambda x: x[1])
        final_list = []
        for feat, dist in results[:limit]:
            feat_geojson = feat.to_geojson_feature()
            feat_geojson["properties"]["distance_meters"] = dist
            feat_geojson["properties"]["distance_km"] = round(dist / 1000.0, 2)
            final_list.append(feat_geojson)

        return final_list

    def get_feature_detail(
        self,
        feature_id: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves authorized feature metadata with source provenance."""
        feat = dataset_registry.get_feature_by_id(feature_id)
        if not feat:
            raise MapFeatureNotFoundError(feature_id)

        ds = dataset_registry.get_dataset(feat.dataset_id)
        if ds and not ds.is_public:
            if ds.owner_user_id != user_id and not (tenant_id and ds.tenant_id == tenant_id):
                raise MapFeatureAccessDeniedError(feature_id, user_id=user_id)

        return {
            "feature_id": feat.feature_id,
            "dataset_id": feat.dataset_id,
            "label": feat.label,
            "geometry_type": feat.geometry_type.value,
            "coordinates": feat.coordinates,
            "properties": feat.properties,
            "bounding_box": feat.bounding_box.to_list() if feat.bounding_box else None,
            "data_quality": feat.data_quality.value,
            "source_reference": feat.source_reference,
            "dataset_name": ds.dataset_name if ds else "Unknown",
            "attribution": ds.attribution if ds else BASEMAP_ATTRIBUTION,
            "licensing_policy": ds.licensing_policy.value
            if ds
            else LicensingPolicy.OPEN_DATA_CC_BY.value,
            "source_updated_at": feat.source_updated_at.isoformat() + "Z",
        }

    def get_vector_tile(
        self,
        layer_id: str,
        z: int,
        x: int,
        y: int,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> bytes:
        """Retrieves or generates an authorized binary MVT vector tile."""
        validate_tile_xyz(z, x, y)
        layer = layer_registry.get_layer(layer_id)
        if not layer:
            raise MapLayerNotFoundError(layer_id)

        ds = dataset_registry.get_dataset(layer.dataset_id)
        if not ds:
            raise MapLayerNotFoundError(layer_id)

        # Enforce multi-tenant dataset access
        is_public = ds.is_public
        if not is_public:
            if ds.owner_user_id != user_id and not (tenant_id and ds.tenant_id == tenant_id):
                raise MapLayerAccessDeniedError(layer_id, tenant_id=tenant_id)

        # Check tile cache
        cache_key = tile_cache_manager.build_cache_key(
            layer_id=layer_id,
            z=z,
            x=x,
            y=y,
            is_public=is_public,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        cached = tile_cache_manager.get_tile(cache_key)
        if cached is not None:
            return cached

        # Generate tile from intersecting features
        tile_bbox = tile_bounds_epsg4326(z, x, y)
        all_features = dataset_registry.list_features(ds.dataset_id)
        intersecting: List[GeoFeature] = []

        for f in all_features:
            if f.bounding_box:
                if bboxes_intersect(tile_bbox, f.bounding_box):
                    intersecting.append(f)
            else:
                if point_in_bbox(f.coordinates[0], f.coordinates[1], tile_bbox):
                    intersecting.append(f)

        tile_bytes = encode_vector_tile_layer(layer.layer_id, intersecting, z, x, y)
        tile_cache_manager.set_tile(cache_key, tile_bytes)
        return tile_bytes


# Global Master Service instance
atlas_maps_service = AtlasMapsService()
