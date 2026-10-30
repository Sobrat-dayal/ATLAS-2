"""Saved Globe View Management and Concurrency Control (Stage 130).

Handles persistence, revision locking, and tenant-isolated retrieval of 3D globe views.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from atlas.maps.domain import GeoCameraState
from atlas.maps.globe.domain import AtlasGlobeCamera, RendererMode, UserGlobeView
from atlas.maps.globe.errors import (
    GlobeViewAccessDeniedError,
    GlobeViewNotFoundError,
    GlobeViewRevisionConflictError,
)

PRESEEDED_GLOBE_VIEWS: list[UserGlobeView] = [
    UserGlobeView(
        view_id="view-globe-london-core",
        tenant_id="default-tenant",
        owner_user_id="system-user",
        name="London Financial District 3D",
        description="Institutional perspective over Bank of England and London financial core.",
        renderer_mode=RendererMode.GLOBE_3D,
        cesium_camera=AtlasGlobeCamera(
            longitude=-0.0885,
            latitude=51.5138,
            height_meters=1850.0,
            heading_radians=0.35,
            pitch_radians=-0.785,  # 45 deg tilt
            roll_radians=0.0,
        ),
        maplibre_camera=GeoCameraState(
            longitude=-0.0885,
            latitude=51.5138,
            zoom=14.5,
            pitch=45.0,
            bearing=20.0,
        ),
        imagery_provider_id="natural-earth",
        terrain_provider_id="ellipsoid",
        visible_layer_references=["atlas.layer.financial_centers"],
        selected_feature_id="fc-london",
        quality_profile="high",
        revision=1,
    ),
    UserGlobeView(
        view_id="view-globe-tokyo-night",
        tenant_id="default-tenant",
        owner_user_id="system-user",
        name="Tokyo Financial Hub 3D",
        description="High-altitude nocturnal overview of Tokyo Stock Exchange and Marunouchi.",
        renderer_mode=RendererMode.GLOBE_3D,
        cesium_camera=AtlasGlobeCamera(
            longitude=139.7714,
            latitude=35.6812,
            height_meters=4500.0,
            heading_radians=0.0,
            pitch_radians=-1.1,
            roll_radians=0.0,
        ),
        maplibre_camera=GeoCameraState(
            longitude=139.7714,
            latitude=35.6812,
            zoom=13.0,
            pitch=30.0,
            bearing=0.0,
        ),
        imagery_provider_id="carto-dark",
        terrain_provider_id="ellipsoid",
        visible_layer_references=["atlas.layer.financial_centers"],
        selected_feature_id="fc-tokyo",
        quality_profile="balanced",
        revision=1,
    ),
]


class AtlasGlobeViewService:
    """Manages UserGlobeView records with tenant isolation and optimistic concurrency control."""

    def __init__(self) -> None:
        self._views: dict[str, UserGlobeView] = {v.view_id: v for v in PRESEEDED_GLOBE_VIEWS}

    def list_views(self, tenant_id: str, owner_user_id: str | None = None) -> list[UserGlobeView]:
        """List views belonging to the given tenant."""
        views: list[UserGlobeView] = []
        for view in self._views.values():
            if view.tenant_id == tenant_id:
                if owner_user_id is None or view.owner_user_id == owner_user_id:
                    views.append(view)
        return views

    def get_view(self, view_id: str, tenant_id: str) -> UserGlobeView:
        """Retrieve view by ID with tenant verification."""
        view = self._views.get(view_id)
        if not view:
            raise GlobeViewNotFoundError(view_id)
        if view.tenant_id != tenant_id:
            raise GlobeViewAccessDeniedError(view_id, tenant_id)
        return view

    def create_view(
        self,
        tenant_id: str,
        owner_user_id: str,
        name: str,
        cesium_camera: AtlasGlobeCamera,
        description: str = "",
        renderer_mode: RendererMode = RendererMode.GLOBE_3D,
        maplibre_camera: GeoCameraState | None = None,
        imagery_provider_id: str = "natural-earth",
        terrain_provider_id: str = "ellipsoid",
        visible_layer_references: list[str] | None = None,
        selected_feature_id: str | None = None,
        quality_profile: str = "balanced",
    ) -> UserGlobeView:
        """Create a new saved 3D globe view."""
        view_id = f"view-globe-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        view = UserGlobeView(
            view_id=view_id,
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            name=name,
            description=description,
            renderer_mode=renderer_mode,
            cesium_camera=cesium_camera,
            maplibre_camera=maplibre_camera,
            imagery_provider_id=imagery_provider_id,
            terrain_provider_id=terrain_provider_id,
            visible_layer_references=list(visible_layer_references or []),
            selected_feature_id=selected_feature_id,
            quality_profile=quality_profile,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        self._views[view_id] = view
        return view

    def update_view(
        self,
        view_id: str,
        tenant_id: str,
        expected_revision: int,
        owner_user_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        cesium_camera: AtlasGlobeCamera | None = None,
        maplibre_camera: GeoCameraState | None = None,
        imagery_provider_id: str | None = None,
        terrain_provider_id: str | None = None,
        visible_layer_references: list[str] | None = None,
        selected_feature_id: str | None = None,
        quality_profile: str | None = None,
    ) -> UserGlobeView:
        """Update an existing view, enforcing optimistic revision locking."""
        view = self.get_view(view_id, tenant_id)

        # Enforce optimistic concurrency revision lock
        if view.revision != expected_revision:
            raise GlobeViewRevisionConflictError(
                view_id=view_id,
                expected_rev=expected_revision,
                current_rev=view.revision,
            )

        if owner_user_id and view.owner_user_id != owner_user_id:
            raise GlobeViewAccessDeniedError(view_id, owner_user_id)

        if name is not None:
            view.name = name
        if description is not None:
            view.description = description
        if cesium_camera is not None:
            view.cesium_camera = cesium_camera
        if maplibre_camera is not None:
            view.maplibre_camera = maplibre_camera
        if imagery_provider_id is not None:
            view.imagery_provider_id = imagery_provider_id
        if terrain_provider_id is not None:
            view.terrain_provider_id = terrain_provider_id
        if visible_layer_references is not None:
            view.visible_layer_references = list(visible_layer_references)
        if selected_feature_id is not None:
            view.selected_feature_id = selected_feature_id
        if quality_profile is not None:
            view.quality_profile = quality_profile

        view.revision += 1
        view.updated_at = datetime.now(timezone.utc)
        return view

    def delete_view(self, view_id: str, tenant_id: str, owner_user_id: str | None = None) -> bool:
        """Delete an existing view."""
        view = self.get_view(view_id, tenant_id)
        if owner_user_id and view.owner_user_id != owner_user_id:
            raise GlobeViewAccessDeniedError(view_id, owner_user_id)
        del self._views[view_id]
        return True
