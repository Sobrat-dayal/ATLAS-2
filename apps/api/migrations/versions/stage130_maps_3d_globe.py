"""stage130_maps_3d_globe

Revision ID: stage130_maps_3d_globe
Revises: stage129_maps_v1_postgis
Create Date: 2026-10-30 00:00:00.000000

Stage 130 — 3D God's Eye Globe using CesiumJS:
- Extends user_map_views with 3D camera state, renderer mode, terrain, and imagery configurations.
- Creates globe_tileset_sources table with OGC 3D Tiles metadata and multi-tenant RLS.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage130_maps_3d_globe"
down_revision: Union[str, Sequence[str], None] = "stage129_maps_v1_postgis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend user_map_views with 3D globe columns
    op.add_column(
        "user_map_views",
        sa.Column("renderer_mode", sa.String(32), nullable=False, server_default="2D"),
    )
    op.add_column(
        "user_map_views",
        sa.Column("cesium_camera", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "user_map_views",
        sa.Column("imagery_provider_id", sa.String(128), nullable=True),
    )
    op.add_column(
        "user_map_views",
        sa.Column("terrain_provider_id", sa.String(128), nullable=True),
    )
    op.add_column(
        "user_map_views",
        sa.Column("quality_profile", sa.String(64), nullable=True, server_default="balanced"),
    )

    # 2. Create globe_tileset_sources table
    op.create_table(
        "globe_tileset_sources",
        sa.Column("tileset_id", sa.String(128), primary_key=True),
        sa.Column("dataset_id", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False, server_default="OGC_3D_TILES"),
        sa.Column("source_reference", sa.String(512), nullable=False),
        sa.Column("bounding_volume", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("attribution", sa.Text(), nullable=False, server_default=""),
        sa.Column("licensing_policy", sa.String(64), nullable=False, server_default="open_source_compliant"),
        sa.Column("tenant_id", sa.String(128), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("data_quality", sa.String(64), nullable=False, server_default="verified"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_globe_tileset_sources_tenant", "globe_tileset_sources", ["tenant_id"])
    op.create_index("ix_globe_tileset_sources_dataset", "globe_tileset_sources", ["dataset_id"])

    # 3. Enable RLS on globe_tileset_sources
    try:
        op.execute("ALTER TABLE globe_tileset_sources ENABLE ROW LEVEL SECURITY;")
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_policies WHERE tablename = 'globe_tileset_sources' AND policyname = 'globe_tileset_sources_tenant_isolation'
                ) THEN
                    CREATE POLICY globe_tileset_sources_tenant_isolation ON globe_tileset_sources
                        FOR ALL
                        USING (
                            tenant_id IS NULL OR
                            tenant_id = current_setting('app.current_tenant_id', true)
                        );
                END IF;
            END $$;
            """
        )
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.execute("DROP POLICY IF EXISTS globe_tileset_sources_tenant_isolation ON globe_tileset_sources;")
    except Exception:
        pass
    op.drop_index("ix_globe_tileset_sources_dataset", table_name="globe_tileset_sources")
    op.drop_index("ix_globe_tileset_sources_tenant", table_name="globe_tileset_sources")
    op.drop_table("globe_tileset_sources")

    op.drop_column("user_map_views", "quality_profile")
    op.drop_column("user_map_views", "terrain_provider_id")
    op.drop_column("user_map_views", "imagery_provider_id")
    op.drop_column("user_map_views", "cesium_camera")
    op.drop_column("user_map_views", "renderer_mode")

