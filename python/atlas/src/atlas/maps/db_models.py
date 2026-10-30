"""SQLAlchemy Database Models for PostGIS / PostgreSQL Geospatial Tables (Stage 129).

Tracks spatial datasets, geographic features, map layers, saved user views,
source manifests, and audit events.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from atlas.database.base import Base


class GeoDatasetModel(Base):
    __tablename__ = "geo_datasets"

    dataset_id = Column(String(128), primary_key=True)
    dataset_name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False, default="")
    dataset_type = Column(String(64), nullable=False)
    source_id = Column(String(128), nullable=False)
    source_version = Column(String(64), nullable=False, default="1.0.0")
    geometry_types = Column(JSONB, nullable=False, default=list)
    srid = Column(Integer, nullable=False, default=4326)
    bounding_box = Column(JSONB, nullable=True)
    feature_count = Column(Integer, nullable=False, default=0)
    attribution = Column(Text, nullable=False, default="")
    licensing_policy = Column(String(64), nullable=False, default="cc_by_4.0")
    is_public = Column(Boolean, nullable=False, default=True)
    owner_user_id = Column(String(128), nullable=True, index=True)
    tenant_id = Column(String(128), nullable=True, index=True)
    data_quality_status = Column(String(64), nullable=False, default="verified")
    published_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    ingested_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)


class GeoFeatureModel(Base):
    __tablename__ = "geo_features"

    feature_id = Column(String(128), primary_key=True)
    dataset_id = Column(
        String(128),
        ForeignKey("geo_datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label = Column(String(256), nullable=False)
    geometry_type = Column(String(64), nullable=False)
    coordinates = Column(JSONB, nullable=False)
    properties = Column(JSONB, nullable=False, default=dict)
    bounding_box = Column(JSONB, nullable=True)
    source_reference = Column(String(512), nullable=False, default="")
    data_quality = Column(String(64), nullable=False, default="verified")
    source_updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)


class MapLayerModel(Base):
    __tablename__ = "map_layers"

    layer_id = Column(String(128), primary_key=True)
    dataset_id = Column(
        String(128),
        ForeignKey("geo_datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    layer_name = Column(String(256), nullable=False)
    geometry_type = Column(String(64), nullable=False)
    source_type = Column(String(64), nullable=False, default="vector")
    style_definition = Column(JSONB, nullable=False, default=dict)
    default_visibility = Column(Boolean, nullable=False, default=True)
    default_opacity = Column(Float, nullable=False, default=1.0)
    min_zoom = Column(Float, nullable=False, default=0.0)
    max_zoom = Column(Float, nullable=False, default=22.0)
    display_order = Column(Integer, nullable=False, default=100)
    category = Column(String(128), nullable=False, default="Boundaries")
    required_permissions = Column(JSONB, nullable=False, default=list)
    license_reference = Column(String(256), nullable=False, default="")
    version = Column(Integer, nullable=False, default=1)


class UserMapViewModel(Base):
    __tablename__ = "user_map_views"

    map_view_id = Column(String(128), primary_key=True)
    owner_user_id = Column(String(128), nullable=False, index=True)
    tenant_id = Column(String(128), nullable=True, index=True)
    workspace_id = Column(String(128), nullable=True, index=True)
    name = Column(String(256), nullable=False)
    camera = Column(JSONB, nullable=False)
    basemap_style_id = Column(String(128), nullable=False, default="atlas-dark")
    visible_layers = Column(JSONB, nullable=False, default=list)
    layer_configurations = Column(JSONB, nullable=False, default=dict)
    selected_feature_id = Column(String(128), nullable=True)
    revision = Column(Integer, nullable=False, default=1)
    map_schema_version = Column(String(32), nullable=False, default="1.0.0")
    renderer_mode = Column(String(32), nullable=False, default="2D")
    cesium_camera = Column(JSONB, nullable=True)
    imagery_provider_id = Column(String(128), nullable=True)
    terrain_provider_id = Column(String(128), nullable=True)
    quality_profile = Column(String(64), nullable=True, default="balanced")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)


class GlobeTilesetSourceModel(Base):
    __tablename__ = "globe_tileset_sources"

    tileset_id = Column(String(128), primary_key=True)
    dataset_id = Column(String(128), nullable=False, index=True)
    source_type = Column(String(64), nullable=False, default="OGC_3D_TILES")
    source_reference = Column(String(512), nullable=False)
    bounding_volume = Column(JSONB, nullable=False, default=dict)
    attribution = Column(Text, nullable=False, default="")
    licensing_policy = Column(String(64), nullable=False, default="open_source_compliant")
    tenant_id = Column(String(128), nullable=True, index=True)
    is_available = Column(Boolean, nullable=False, default=True)
    data_quality = Column(String(64), nullable=False, default="verified")
    description = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)


class MapAuditEventModel(Base):
    __tablename__ = "map_audit_events"

    event_id = Column(String(128), primary_key=True)
    user_id = Column(String(128), nullable=False, index=True)
    tenant_id = Column(String(128), nullable=True, index=True)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=False)
    details = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
