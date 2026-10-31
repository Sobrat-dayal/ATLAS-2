"""FastAPI Router for ATLAS Maps V1 Geospatial Endpoints (Stage 129).

Prefix: /api/v1/maps
Provides runtime config, styles, layer catalog, bounded spatial queries,
proximity queries, feature inspection, binary MVT vector tiles, geographic search,
and persistent map views.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.maps.datasets.registry import dataset_registry
from atlas.maps.domain import GeoBoundingBox, GeoCameraState
from atlas.maps.errors import (
    MapBoundsInvalidError,
    MapCoordinatesInvalidError,
    MapDatasetAccessDeniedError,
    MapFeatureAccessDeniedError,
    MapFeatureNotFoundError,
    MapLayerAccessDeniedError,
    MapLayerNotFoundError,
    MapSpatialQueryTooLargeError,
    MapTileCoordinatesInvalidError,
    MapViewAccessDeniedError,
    MapViewNotFoundError,
    MapViewRevisionConflictError,
)
from atlas.maps.layers.registry import layer_registry
from atlas.maps.schemas import (
    FeatureDetailResponse,
    GeographicSearchResultDTO,
    MapConfigResponse,
    MapDatasetDTO,
    MapLayerDTO,
    MapStyleDTO,
    SaveMapViewRequest,
    SpatialNearbyRequest,
    SpatialQueryRequest,
    UpdateMapViewRequest,
    UserMapViewResponse,
)
from atlas.maps.search.service import geographic_search_service
from atlas.maps.service import atlas_maps_service
from atlas.maps.views.service import map_view_service
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..auth.dependencies import get_current_user
from .maps_analytics import router as analytics_router
from .maps_corporate import router as corporate_router
from .maps_globe import globe_router

router = APIRouter(prefix="/maps", tags=["maps"])
router.include_router(globe_router)
router.include_router(analytics_router)
router.include_router(corporate_router)


@router.get("/config", response_model=MapConfigResponse)
async def get_map_config() -> MapConfigResponse:
    """Returns approved runtime map configuration, CRS info, and attribution."""
    cfg = atlas_maps_service.get_runtime_config()
    return MapConfigResponse(**cfg)


@router.get("/styles", response_model=List[MapStyleDTO])
async def list_map_styles() -> List[MapStyleDTO]:
    """Returns list of available licensed map styles with attribution."""
    return [MapStyleDTO(**s) for s in atlas_maps_service.list_styles()]


@router.get("/layers", response_model=List[MapLayerDTO])
async def list_map_layers(
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[MapLayerDTO]:
    """Returns authorized visual layers catalog."""
    user_id = current_user.sub if current_user else None
    layers = atlas_maps_service.list_layers(user_id=user_id)
    return [MapLayerDTO(**layer) for layer in layers]


@router.get("/layers/{layer_id}", response_model=MapLayerDTO)
async def get_map_layer(
    layer_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MapLayerDTO:
    """Returns layer metadata."""
    layer = layer_registry.get_layer(layer_id)
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Layer '{layer_id}' not found"
        )
    return MapLayerDTO(
        layer_id=layer.layer_id,
        dataset_id=layer.dataset_id,
        layer_name=layer.layer_name,
        geometry_type=layer.geometry_type.value,
        source_type=layer.source_type,
        default_visibility=layer.default_visibility,
        default_opacity=layer.default_opacity,
        min_zoom=layer.min_zoom,
        max_zoom=layer.max_zoom,
        display_order=layer.display_order,
        category=layer.category,
        license_reference=layer.license_reference,
    )


@router.get("/datasets", response_model=List[MapDatasetDTO])
async def list_map_datasets(
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[MapDatasetDTO]:
    """Returns authorized spatial dataset catalog."""
    user_id = current_user.sub if current_user else None
    datasets = dataset_registry.list_datasets(user_id=user_id)
    return [
        MapDatasetDTO(
            dataset_id=ds.dataset_id,
            dataset_name=ds.dataset_name,
            description=ds.description,
            dataset_type=ds.dataset_type.value,
            geometry_types=[gt.value for gt in ds.geometry_types],
            feature_count=ds.feature_count,
            attribution=ds.attribution,
            licensing_policy=ds.licensing_policy.value,
            is_public=ds.is_public,
        )
        for ds in datasets
    ]


@router.get("/datasets/{dataset_id}", response_model=MapDatasetDTO)
async def get_map_dataset(
    dataset_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MapDatasetDTO:
    """Returns dataset metadata."""
    ds = dataset_registry.get_dataset(dataset_id)
    if not ds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset '{dataset_id}' not found"
        )

    user_id = current_user.sub if current_user else None
    if not ds.is_public and ds.owner_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to private dataset"
        )

    return MapDatasetDTO(
        dataset_id=ds.dataset_id,
        dataset_name=ds.dataset_name,
        description=ds.description,
        dataset_type=ds.dataset_type.value,
        geometry_types=[gt.value for gt in ds.geometry_types],
        feature_count=ds.feature_count,
        attribution=ds.attribution,
        licensing_policy=ds.licensing_policy.value,
        is_public=ds.is_public,
    )


@router.post("/features/query")
async def query_features(
    req: SpatialQueryRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Dict[str, Any]:
    """Performs bounded spatial query in EPSG:4326 with antimeridian normalization."""
    user_id = current_user.sub if current_user else None
    try:
        return atlas_maps_service.query_features(
            west=req.west,
            south=req.south,
            east=req.east,
            north=req.north,
            dataset_ids=req.dataset_ids,
            layer_ids=req.layer_ids,
            zoom=req.zoom,
            limit=req.limit,
            user_id=user_id,
        )
    except MapBoundsInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except MapDatasetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except MapSpatialQueryTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=e.message)


@router.post("/features/nearby")
async def query_nearby(
    req: SpatialNearbyRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Performs metric proximity query in meters (CRITICAL UNIT RULE: Degrees != Meters)."""
    user_id = current_user.sub if current_user else None
    try:
        return atlas_maps_service.query_nearby(
            center_lon=req.longitude,
            center_lat=req.latitude,
            radius_meters=req.radius_meters,
            dataset_ids=req.dataset_ids,
            limit=req.limit,
            user_id=user_id,
        )
    except MapCoordinatesInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except MapDatasetAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/features/{feature_id}", response_model=FeatureDetailResponse)
async def get_feature_detail(
    feature_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> FeatureDetailResponse:
    """Returns detailed feature attributes, coordinates, and provenance."""
    user_id = current_user.sub if current_user else None
    try:
        detail = atlas_maps_service.get_feature_detail(feature_id, user_id=user_id)
        return FeatureDetailResponse(**detail)
    except MapFeatureNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Feature '{feature_id}' not found"
        )
    except MapFeatureAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to protected feature"
        )


@router.get("/tiles/{layer_id}/{z}/{x}/{y}.pbf")
async def get_vector_tile(
    layer_id: str,
    z: int,
    x: int,
    y: int,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Response:
    """Returns binary Mapbox Vector Tile (MVT) protobuf bytes."""
    user_id = current_user.sub if current_user else None
    try:
        tile_bytes = atlas_maps_service.get_vector_tile(
            layer_id=layer_id,
            z=z,
            x=x,
            y=y,
            user_id=user_id,
        )
        return Response(
            content=tile_bytes,
            media_type="application/x-protobuf",
            headers={
                "Cache-Control": "public, max-age=3600"
                if user_id is None
                else "private, max-age=60",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except MapTileCoordinatesInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except MapLayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Layer '{layer_id}' not found"
        )
    except MapLayerAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to layer tiles"
        )


@router.get("/search", response_model=List[GeographicSearchResultDTO])
async def search_places(
    q: str = Query(..., min_length=1, max_length=256),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[GeographicSearchResultDTO]:
    """Resolves geographic search queries across countries, regions, and coordinates."""
    results = geographic_search_service.search(query=q, limit=limit)
    return [
        GeographicSearchResultDTO(
            result_id=r.result_id,
            label=r.label,
            place_type=r.place_type,
            coordinates=r.coordinates,
            bounding_box=r.bounding_box.to_list() if r.bounding_box else None,
            source_dataset_id=r.source_dataset_id,
            disambiguation=r.disambiguation,
            relevance_score=r.relevance_score,
        )
        for r in results
    ]


@router.get("/views", response_model=List[UserMapViewResponse])
async def list_map_views(
    workspace_id: Optional[str] = Query(None),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[UserMapViewResponse]:
    """Returns list of persisted user map views."""
    user_id = current_user.sub or "user_default"
    views = map_view_service.list_views(user_id=user_id, workspace_id=workspace_id)
    return [
        UserMapViewResponse(
            map_view_id=v.map_view_id,
            owner_user_id=v.owner_user_id,
            name=v.name,
            camera=v.camera.to_dict(),
            basemap_style_id=v.basemap_style_id,
            visible_layers=v.visible_layers,
            layer_configurations=v.layer_configurations,
            selected_feature_id=v.selected_feature_id,
            workspace_id=v.workspace_id,
            tenant_id=v.tenant_id,
            revision=v.revision,
            map_schema_version=v.map_schema_version,
            created_at=v.created_at.isoformat() + "Z",
            updated_at=v.updated_at.isoformat() + "Z",
        )
        for v in views
    ]


@router.post("/views", response_model=UserMapViewResponse)
async def save_map_view(
    req: SaveMapViewRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserMapViewResponse:
    """Saves current map view configuration for Saved and Workspace integration."""
    user_id = current_user.sub or "user_default"
    camera_state = GeoCameraState(
        longitude=req.camera.longitude,
        latitude=req.camera.latitude,
        zoom=req.camera.zoom,
        bearing=req.camera.bearing,
        pitch=req.camera.pitch,
        bounds=GeoBoundingBox(*req.camera.bounds)
        if req.camera.bounds and len(req.camera.bounds) == 4
        else None,
        projection=req.camera.projection,
        revision=req.camera.revision,
    )
    v = map_view_service.save_view(
        owner_user_id=user_id,
        name=req.name,
        camera=camera_state,
        basemap_style_id=req.basemap_style_id,
        visible_layers=req.visible_layers,
        layer_configurations=req.layer_configurations,
        selected_feature_id=req.selected_feature_id,
        workspace_id=req.workspace_id,
    )
    return UserMapViewResponse(
        map_view_id=v.map_view_id,
        owner_user_id=v.owner_user_id,
        name=v.name,
        camera=v.camera.to_dict(),
        basemap_style_id=v.basemap_style_id,
        visible_layers=v.visible_layers,
        layer_configurations=v.layer_configurations,
        selected_feature_id=v.selected_feature_id,
        workspace_id=v.workspace_id,
        tenant_id=v.tenant_id,
        revision=v.revision,
        map_schema_version=v.map_schema_version,
        created_at=v.created_at.isoformat() + "Z",
        updated_at=v.updated_at.isoformat() + "Z",
    )


@router.get("/views/{view_id}", response_model=UserMapViewResponse)
async def get_map_view(
    view_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserMapViewResponse:
    """Restores saved map view configuration."""
    user_id = current_user.sub or "user_default"
    try:
        v = map_view_service.get_view(view_id=view_id, user_id=user_id)
        return UserMapViewResponse(
            map_view_id=v.map_view_id,
            owner_user_id=v.owner_user_id,
            name=v.name,
            camera=v.camera.to_dict(),
            basemap_style_id=v.basemap_style_id,
            visible_layers=v.visible_layers,
            layer_configurations=v.layer_configurations,
            selected_feature_id=v.selected_feature_id,
            workspace_id=v.workspace_id,
            tenant_id=v.tenant_id,
            revision=v.revision,
            map_schema_version=v.map_schema_version,
            created_at=v.created_at.isoformat() + "Z",
            updated_at=v.updated_at.isoformat() + "Z",
        )
    except MapViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"View '{view_id}' not found"
        )
    except MapViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to saved map view"
        )


@router.patch("/views/{view_id}", response_model=UserMapViewResponse)
async def update_map_view(
    view_id: str,
    req: UpdateMapViewRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserMapViewResponse:
    """Updates saved map view with optimistic concurrency revision check."""
    user_id = current_user.sub or "user_default"
    camera_state = None
    if req.camera:
        camera_state = GeoCameraState(
            longitude=req.camera.longitude,
            latitude=req.camera.latitude,
            zoom=req.camera.zoom,
            bearing=req.camera.bearing,
            pitch=req.camera.pitch,
            bounds=GeoBoundingBox(*req.camera.bounds)
            if req.camera.bounds and len(req.camera.bounds) == 4
            else None,
            projection=req.camera.projection,
            revision=req.camera.revision,
        )

    try:
        v = map_view_service.update_view(
            view_id=view_id,
            user_id=user_id,
            expected_revision=req.expected_revision,
            name=req.name,
            camera=camera_state,
            basemap_style_id=req.basemap_style_id,
            visible_layers=req.visible_layers,
            layer_configurations=req.layer_configurations,
            selected_feature_id=req.selected_feature_id,
        )
        return UserMapViewResponse(
            map_view_id=v.map_view_id,
            owner_user_id=v.owner_user_id,
            name=v.name,
            camera=v.camera.to_dict(),
            basemap_style_id=v.basemap_style_id,
            visible_layers=v.visible_layers,
            layer_configurations=v.layer_configurations,
            selected_feature_id=v.selected_feature_id,
            workspace_id=v.workspace_id,
            tenant_id=v.tenant_id,
            revision=v.revision,
            map_schema_version=v.map_schema_version,
            created_at=v.created_at.isoformat() + "Z",
            updated_at=v.updated_at.isoformat() + "Z",
        )
    except MapViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"View '{view_id}' not found"
        )
    except MapViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to saved map view"
        )
    except MapViewRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.delete("/views/{view_id}")
async def delete_map_view(
    view_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Dict[str, bool]:
    """Deletes saved map view."""
    user_id = current_user.sub or "user_default"
    try:
        map_view_service.delete_view(view_id=view_id, user_id=user_id)
        return {"success": True}
    except MapViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"View '{view_id}' not found"
        )
    except MapViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to saved map view"
        )
