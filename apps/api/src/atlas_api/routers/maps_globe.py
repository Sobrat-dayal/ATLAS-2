"""FastAPI Router for ATLAS 3D God's Eye Globe Endpoints (Stage 130).

Prefix: /maps/globe (mounted under /api/v1/maps)
Provides runtime configuration, imagery and terrain provider catalogs,
OGC 3D Tileset authorization, 2D/3D camera interoperability, and persistent globe views.
"""

from __future__ import annotations

from typing import Any, Dict, List

from atlas.auth import AuthPrincipal
from atlas.maps.domain import GeoBoundingBox, GeoCameraState
from atlas.maps.globe.domain import (
    AtlasGlobeCamera,
    RendererMode,
)
from atlas.maps.globe.errors import (
    GlobeCameraInvalidError,
    GlobeTilesetAccessDeniedError,
    GlobeTilesetNotFoundError,
    GlobeViewAccessDeniedError,
    GlobeViewNotFoundError,
    GlobeViewRevisionConflictError,
)
from atlas.maps.globe.interop import (
    cesium_to_maplibre_camera,
    maplibre_to_cesium_camera,
)
from atlas.maps.globe.schemas import (
    Atlas3DTilesetSourceDTO,
    CameraConversionRequest,
    CameraConversionResponse,
    GlobeCameraDTO,
    GlobeFeaturesQueryRequest,
    GlobeImageryProviderDTO,
    GlobeRuntimeConfigDTO,
    GlobeTerrainProviderDTO,
    MapLibreCameraDTO,
    SaveGlobeViewRequest,
    UpdateGlobeViewRequest,
    UserGlobeViewDTO,
)
from atlas.maps.globe.service import globe_service
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth.dependencies import get_current_user

globe_router = APIRouter(prefix="/globe", tags=["maps_globe"])


@globe_router.get("/config", response_model=GlobeRuntimeConfigDTO)
async def get_globe_config(
    current_user: AuthPrincipal = Depends(get_current_user),
) -> GlobeRuntimeConfigDTO:
    """Retrieve runtime globe capabilities, default camera, and WebGL configuration."""
    tenant_id = current_user.tenant_id or "default-tenant"
    user_id = current_user.sub or "user_default"
    cfg = globe_service.get_runtime_config(tenant_id=tenant_id, user_id=user_id)
    return GlobeRuntimeConfigDTO(
        default_imagery_provider_id=cfg.default_imagery_provider_id,
        default_terrain_provider_id=cfg.default_terrain_provider_id,
        ion_configured=cfg.ion_configured,
        supported_modes=cfg.supported_modes,
        max_active_viewers=cfg.max_active_viewers,
        default_camera=GlobeCameraDTO(**cfg.default_camera.to_dict()),
    )


@globe_router.get("/imagery", response_model=List[GlobeImageryProviderDTO])
async def list_imagery_providers(
    include_restricted: bool = Query(False),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[GlobeImageryProviderDTO]:
    """Retrieve approved imagery providers with attribution."""
    tenant_id = current_user.tenant_id or "default-tenant"
    providers = globe_service.list_imagery_providers(
        tenant_id=tenant_id, include_restricted=include_restricted
    )
    return [GlobeImageryProviderDTO(**p.to_dict()) for p in providers]


@globe_router.get("/terrain", response_model=List[GlobeTerrainProviderDTO])
async def list_terrain_providers(
    include_restricted: bool = Query(False),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[GlobeTerrainProviderDTO]:
    """Retrieve approved terrain providers with elevation capabilities."""
    tenant_id = current_user.tenant_id or "default-tenant"
    providers = globe_service.list_terrain_providers(
        tenant_id=tenant_id, include_restricted=include_restricted
    )
    return [GlobeTerrainProviderDTO(**p.to_dict()) for p in providers]


@globe_router.get("/tilesets", response_model=List[Atlas3DTilesetSourceDTO])
async def list_3d_tilesets(
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[Atlas3DTilesetSourceDTO]:
    """Retrieve authorized 3D Tilesets accessible to the authenticated tenant."""
    tenant_id = current_user.tenant_id or "default-tenant"
    tilesets = globe_service.list_tilesets(tenant_id=tenant_id)
    return [Atlas3DTilesetSourceDTO(**t.to_dict()) for t in tilesets]


@globe_router.get("/tilesets/{tileset_id}", response_model=Atlas3DTilesetSourceDTO)
async def get_3d_tileset(
    tileset_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Atlas3DTilesetSourceDTO:
    """Retrieve metadata for a specific 3D Tileset, verifying tenant authorization."""
    tenant_id = current_user.tenant_id or "default-tenant"
    try:
        tileset = globe_service.get_tileset(tileset_id=tileset_id, tenant_id=tenant_id)
        return Atlas3DTilesetSourceDTO(**tileset.to_dict())
    except GlobeTilesetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"3D Tileset '{tileset_id}' not found",
        )
    except GlobeTilesetAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to private 3D Tileset '{tileset_id}'",
        )


@globe_router.post("/features/query")
async def query_globe_features(
    req: GlobeFeaturesQueryRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Dict[str, Any]:
    """Query spatial features within a bounding box for 3D globe display."""
    tenant_id = current_user.tenant_id or "default-tenant"
    bbox = GeoBoundingBox(
        west=req.bounding_box[0],
        south=req.bounding_box[1],
        east=req.bounding_box[2],
        north=req.bounding_box[3],
    )
    features = globe_service.query_features(bbox=bbox, layer_ids=req.layer_ids, tenant_id=tenant_id)
    return {
        "type": "FeatureCollection",
        "features": [f.to_geojson_feature() for f in features],
    }


@globe_router.post("/camera/convert", response_model=CameraConversionResponse)
async def convert_camera(
    req: CameraConversionRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> CameraConversionResponse:
    """Convert bidirectionally between 2D MapLibre and 3D Cesium camera states."""
    if req.from_mode == "2D":
        if not req.maplibre_camera:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="maplibre_camera required when converting from 2D",
            )
        try:
            c3d = maplibre_to_cesium_camera(
                center_lon=req.maplibre_camera.center[0],
                center_lat=req.maplibre_camera.center[1],
                zoom=req.maplibre_camera.zoom,
                bearing_deg=req.maplibre_camera.bearing,
                pitch_deg=req.maplibre_camera.pitch,
            )
            return CameraConversionResponse(cesium_camera=GlobeCameraDTO(**c3d.to_dict()))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion error: {e}",
            )
    elif req.from_mode == "3D":
        if not req.cesium_camera:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cesium_camera required when converting from 3D",
            )
        try:
            cam = AtlasGlobeCamera(
                longitude=req.cesium_camera.longitude,
                latitude=req.cesium_camera.latitude,
                height_meters=req.cesium_camera.height_meters,
                heading_radians=req.cesium_camera.heading_radians,
                pitch_radians=req.cesium_camera.pitch_radians,
                roll_radians=req.cesium_camera.roll_radians,
            )
            c2d = cesium_to_maplibre_camera(cam)
            return CameraConversionResponse(
                maplibre_camera=MapLibreCameraDTO(
                    center=c2d.center,
                    zoom=c2d.zoom,
                    pitch=c2d.pitch,
                    bearing=c2d.bearing,
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversion error: {e}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown from_mode '{req.from_mode}'; expected '2D' or '3D'",
        )


@globe_router.get("/views", response_model=List[UserGlobeViewDTO])
async def list_globe_views(
    current_user: AuthPrincipal = Depends(get_current_user),
) -> List[UserGlobeViewDTO]:
    """Retrieve saved 3D globe views for the authenticated tenant."""
    tenant_id = current_user.tenant_id or "default-tenant"
    views = globe_service.list_views(tenant_id=tenant_id)
    return [UserGlobeViewDTO(**v.to_dict()) for v in views]


@globe_router.post("/views", response_model=UserGlobeViewDTO, status_code=status.HTTP_201_CREATED)
async def create_globe_view(
    req: SaveGlobeViewRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserGlobeViewDTO:
    """Save a 3D globe view with genuine camera orientation and source references."""
    tenant_id = current_user.tenant_id or "default-tenant"
    user_id = current_user.sub or "user_default"

    try:
        cam = AtlasGlobeCamera(
            longitude=req.cesium_camera.longitude,
            latitude=req.cesium_camera.latitude,
            height_meters=req.cesium_camera.height_meters,
            heading_radians=req.cesium_camera.heading_radians,
            pitch_radians=req.cesium_camera.pitch_radians,
            roll_radians=req.cesium_camera.roll_radians,
        )
    except GlobeCameraInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    maplibre_cam = None
    if req.maplibre_camera:
        maplibre_cam = GeoCameraState(
            longitude=req.maplibre_camera.center[0],
            latitude=req.maplibre_camera.center[1],
            zoom=req.maplibre_camera.zoom,
            pitch=req.maplibre_camera.pitch,
            bearing=req.maplibre_camera.bearing,
        )

    view = globe_service.save_view(
        tenant_id=tenant_id,
        owner_user_id=user_id,
        name=req.name,
        cesium_camera=cam,
        description=req.description,
        renderer_mode=RendererMode.GLOBE_3D if req.renderer_mode == "3D" else RendererMode.MAP_2D,
        maplibre_camera=maplibre_cam,
        imagery_provider_id=req.imagery_provider_id,
        terrain_provider_id=req.terrain_provider_id,
        visible_layer_references=req.visible_layer_references,
        selected_feature_id=req.selected_feature_id,
        quality_profile=req.quality_profile,
    )
    return UserGlobeViewDTO(**view.to_dict())


@globe_router.get("/views/{view_id}", response_model=UserGlobeViewDTO)
async def get_globe_view(
    view_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserGlobeViewDTO:
    """Retrieve saved 3D globe view by ID."""
    tenant_id = current_user.tenant_id or "default-tenant"
    try:
        view = globe_service.get_view(view_id=view_id, tenant_id=tenant_id)
        return UserGlobeViewDTO(**view.to_dict())
    except GlobeViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Globe view '{view_id}' not found",
        )
    except GlobeViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to globe view '{view_id}'",
        )


@globe_router.patch("/views/{view_id}", response_model=UserGlobeViewDTO)
async def update_globe_view(
    view_id: str,
    req: UpdateGlobeViewRequest,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> UserGlobeViewDTO:
    """Update saved 3D globe view, verifying optimistic concurrency revision."""
    tenant_id = current_user.tenant_id or "default-tenant"
    user_id = current_user.sub or "user_default"

    cam = None
    if req.cesium_camera:
        try:
            cam = AtlasGlobeCamera(
                longitude=req.cesium_camera.longitude,
                latitude=req.cesium_camera.latitude,
                height_meters=req.cesium_camera.height_meters,
                heading_radians=req.cesium_camera.heading_radians,
                pitch_radians=req.cesium_camera.pitch_radians,
                roll_radians=req.cesium_camera.roll_radians,
            )
        except GlobeCameraInvalidError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    maplibre_cam = None
    if req.maplibre_camera:
        maplibre_cam = GeoCameraState(
            longitude=req.maplibre_camera.center[0],
            latitude=req.maplibre_camera.center[1],
            zoom=req.maplibre_camera.zoom,
            pitch=req.maplibre_camera.pitch,
            bearing=req.maplibre_camera.bearing,
        )

    try:
        updated = globe_service.update_view(
            view_id=view_id,
            tenant_id=tenant_id,
            expected_revision=req.expected_revision,
            owner_user_id=user_id,
            name=req.name,
            description=req.description,
            cesium_camera=cam,
            maplibre_camera=maplibre_cam,
            imagery_provider_id=req.imagery_provider_id,
            terrain_provider_id=req.terrain_provider_id,
            visible_layer_references=req.visible_layer_references,
            selected_feature_id=req.selected_feature_id,
            quality_profile=req.quality_profile,
        )
        return UserGlobeViewDTO(**updated.to_dict())
    except GlobeViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Globe view '{view_id}' not found",
        )
    except GlobeViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to globe view '{view_id}'",
        )
    except GlobeViewRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@globe_router.delete("/views/{view_id}")
async def delete_globe_view(
    view_id: str,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> Dict[str, bool]:
    """Delete saved 3D globe view."""
    tenant_id = current_user.tenant_id or "default-tenant"
    user_id = current_user.sub or "user_default"
    try:
        globe_service.delete_view(view_id=view_id, tenant_id=tenant_id, owner_user_id=user_id)
        return {"success": True}
    except GlobeViewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Globe view '{view_id}' not found",
        )
    except GlobeViewAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to globe view '{view_id}'",
        )
