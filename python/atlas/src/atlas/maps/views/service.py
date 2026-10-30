"""Persistent User Map Views Service for Stage 119 Saved and Stage 120 Workspaces.

Persists full camera state, basemap styles, layer states, and selections.
Enforces tenant isolation, revision concurrency, and authorized restoration.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional

from atlas.maps.domain import GeoCameraState, UserMapView
from atlas.maps.errors import (
    MapViewAccessDeniedError,
    MapViewNotFoundError,
    MapViewRevisionConflictError,
)


class AtlasMapViewService:
    """Manages creation, restoration, update, and deletion of user map views."""

    def __init__(self):
        self._views: Dict[str, UserMapView] = {}

    def save_view(
        self,
        owner_user_id: str,
        name: str,
        camera: GeoCameraState,
        basemap_style_id: str,
        visible_layers: List[str],
        layer_configurations: Dict[str, Dict[str, Any]],
        selected_feature_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        view_id: Optional[str] = None,
    ) -> UserMapView:
        vid = view_id or f"map_view_{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.utcnow()

        view = UserMapView(
            map_view_id=vid,
            owner_user_id=owner_user_id,
            name=name,
            camera=camera,
            basemap_style_id=basemap_style_id,
            visible_layers=visible_layers,
            layer_configurations=layer_configurations,
            selected_feature_id=selected_feature_id,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        self._views[vid] = view
        return view

    def get_view(
        self,
        view_id: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> UserMapView:
        view = self._views.get(view_id)
        if not view:
            raise MapViewNotFoundError(view_id)

        # Check tenant and user authorization
        if user_id and view.owner_user_id != user_id:
            if not (tenant_id and view.tenant_id == tenant_id):
                raise MapViewAccessDeniedError(view_id, user_id=user_id)

        return view

    def list_views(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[UserMapView]:
        results: List[UserMapView] = []
        for v in self._views.values():
            if v.owner_user_id == user_id or (tenant_id and v.tenant_id == tenant_id):
                if workspace_id is None or v.workspace_id == workspace_id:
                    results.append(v)
        return sorted(results, key=lambda v: v.updated_at, reverse=True)

    def update_view(
        self,
        view_id: str,
        user_id: str,
        expected_revision: int,
        tenant_id: Optional[str] = None,
        name: Optional[str] = None,
        camera: Optional[GeoCameraState] = None,
        basemap_style_id: Optional[str] = None,
        visible_layers: Optional[List[str]] = None,
        layer_configurations: Optional[Dict[str, Dict[str, Any]]] = None,
        selected_feature_id: Optional[str] = None,
    ) -> UserMapView:
        view = self.get_view(view_id, user_id=user_id, tenant_id=tenant_id)

        # Optimistic concurrency revision check
        if view.revision != expected_revision:
            raise MapViewRevisionConflictError(view_id, view.revision, expected_revision)

        if name is not None:
            view.name = name
        if camera is not None:
            view.camera = camera
        if basemap_style_id is not None:
            view.basemap_style_id = basemap_style_id
        if visible_layers is not None:
            view.visible_layers = visible_layers
        if layer_configurations is not None:
            view.layer_configurations = layer_configurations
        if selected_feature_id is not None:
            view.selected_feature_id = selected_feature_id

        view.revision += 1
        view.updated_at = datetime.datetime.utcnow()
        return view

    def delete_view(
        self,
        view_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        view = self.get_view(view_id, user_id=user_id, tenant_id=tenant_id)
        del self._views[view.map_view_id]
        return True


# Global Singleton instance
map_view_service = AtlasMapViewService()

