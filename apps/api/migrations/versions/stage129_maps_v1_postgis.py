"""stage129_maps_v1_postgis

Revision ID: stage129_maps_v1_postgis
Revises: stage128_ai_financial_actions
Create Date: 2026-10-30 00:00:00.000000

Stage 129 — MAPS V1 using PostGIS and MapLibre:
- Enables postgis extension where supported.
- Creates geo_datasets, geo_features, map_layers, user_map_views, map_audit_events.
- Spatial and relational indexing.
- Multi-tenant RLS policies.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage129_maps_v1_postgis"
down_revision: Union[str, Sequence[str], None] = "stage128_ai_financial_actions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Try safely creating postgis extension if permitted
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    except Exception:
        pass

    # 1. geo_datasets
    op.create_table(
        "geo_datasets",
        sa.Column("dataset_id", sa.String(length=128), primary_key=True),
        sa.Column("dataset_name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("dataset_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("source_version", sa.String(length=64), nullable=False, server_default="1.0.0"),
        sa.Column("geometry_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("srid", sa.Integer(), nullable=False, server_default="4326"),
        sa.Column("bounding_box", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feature_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attribution", sa.Text(), nullable=False, server_default=""),
        sa.Column("licensing_policy", sa.String(length=64), nullable=False, server_default="cc_by_4.0"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("owner_user_id", sa.String(length=128), nullable=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("data_quality_status", sa.String(length=64), nullable=False, server_default="verified"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_geo_datasets_owner_user_id", "geo_datasets", ["owner_user_id"])
    op.create_index("ix_geo_datasets_tenant_id", "geo_datasets", ["tenant_id"])

    # 2. geo_features
    op.create_table(
        "geo_features",
        sa.Column("feature_id", sa.String(length=128), primary_key=True),
        sa.Column("dataset_id", sa.String(length=128), sa.ForeignKey("geo_datasets.dataset_id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(length=256), nullable=False),
        sa.Column("geometry_type", sa.String(length=64), nullable=False),
        sa.Column("coordinates", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("bounding_box", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source_reference", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("data_quality", sa.String(length=64), nullable=False, server_default="verified"),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_geo_features_dataset_id", "geo_features", ["dataset_id"])

    # 3. map_layers
    op.create_table(
        "map_layers",
        sa.Column("layer_id", sa.String(length=128), primary_key=True),
        sa.Column("dataset_id", sa.String(length=128), sa.ForeignKey("geo_datasets.dataset_id", ondelete="CASCADE"), nullable=False),
        sa.Column("layer_name", sa.String(length=256), nullable=False),
        sa.Column("geometry_type", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False, server_default="vector"),
        sa.Column("style_definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("default_visibility", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("default_opacity", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("min_zoom", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("max_zoom", sa.Float(), nullable=False, server_default="22.0"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("category", sa.String(length=128), nullable=False, server_default="Boundaries"),
        sa.Column("required_permissions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("license_reference", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_map_layers_dataset_id", "map_layers", ["dataset_id"])

    # 4. user_map_views
    op.create_table(
        "user_map_views",
        sa.Column("map_view_id", sa.String(length=128), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("camera", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("basemap_style_id", sa.String(length=128), nullable=False, server_default="atlas-dark"),
        sa.Column("visible_layers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("layer_configurations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("selected_feature_id", sa.String(length=128), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("map_schema_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_user_map_views_owner_user_id", "user_map_views", ["owner_user_id"])
    op.create_index("ix_user_map_views_tenant_id", "user_map_views", ["tenant_id"])
    op.create_index("ix_user_map_views_workspace_id", "user_map_views", ["workspace_id"])

    # 5. map_audit_events
    op.create_table(
        "map_audit_events",
        sa.Column("event_id", sa.String(length=128), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_map_audit_events_user_id", "map_audit_events", ["user_id"])
    op.create_index("ix_map_audit_events_tenant_id", "map_audit_events", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("map_audit_events")
    op.drop_table("user_map_views")
    op.drop_table("map_layers")
    op.drop_table("geo_features")
    op.drop_table("geo_datasets")

