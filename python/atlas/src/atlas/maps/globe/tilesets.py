"""OGC 3D Tileset Source Registry and Authorization (Stage 130).

Manages 3D Tileset sources with strict multi-tenant isolation, bounding volume
metadata, and licensing verification.
"""

from __future__ import annotations

from atlas.maps.domain import DataQualityStatus, LicensingPolicy
from atlas.maps.globe.domain import Atlas3DTilesetSource, TilesetSourceType
from atlas.maps.globe.errors import (
    GlobeTilesetAccessDeniedError,
    GlobeTilesetNotFoundError,
)

DEFAULT_3D_TILESETS: dict[str, Atlas3DTilesetSource] = {
    "atlas.reference.financial_district_3dtiles": Atlas3DTilesetSource(
        tileset_id="atlas.reference.financial_district_3dtiles",
        dataset_id="atlas.reference.financial_centers",
        source_type=TilesetSourceType.OGC_3D_TILES,
        source_reference="https://assets.atlas.internal/3dtiles/london_financial/tileset.json",
        bounding_volume={
            "type": "region",
            "west": -0.095,
            "south": 51.510,
            "east": -0.080,
            "north": 51.520,
            "min_height": 0.0,
            "max_height": 310.0,
        },
        attribution="© Open City 3D Model, UK Geospatial Commission",
        licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
        tenant_id=None,  # Public reference asset
        is_available=True,
        data_quality=DataQualityStatus.VERIFIED,
        description="OGC 3D Tiles 1.1 b3dm mesh of institutional financial towers and exchanges in London.",
    ),
    "atlas.tenant_alpha.confidential_vault_3dtiles": Atlas3DTilesetSource(
        tileset_id="atlas.tenant_alpha.confidential_vault_3dtiles",
        dataset_id="atlas.tenant_alpha.private_geography",
        source_type=TilesetSourceType.OGC_3D_TILES,
        source_reference="https://storage.internal.atlas/tenant-alpha/vault_3dtiles/tileset.json",
        bounding_volume={
            "type": "sphere",
            "center": [8.5417, 47.3769, 450.0],
            "radius": 250.0,
        },
        attribution="© Tenant Alpha Proprietary Asset Registry",
        licensing_policy=LicensingPolicy.PROPRIETARY_LICENSED,
        tenant_id="tenant-alpha",  # Strict private tenant ownership
        is_available=True,
        data_quality=DataQualityStatus.PROVISIONAL,
        description="Confidential private vault building structural 3D tileset.",
    ),
}


class AtlasGlobeTilesetRegistry:
    """Manages 3D Tiles sources with tenant isolation and authorization checks."""

    def __init__(self) -> None:
        self._tilesets: dict[str, Atlas3DTilesetSource] = dict(DEFAULT_3D_TILESETS)

    def list_tilesets(self, tenant_id: str, is_admin: bool = False) -> list[Atlas3DTilesetSource]:
        """List all 3D Tilesets accessible to the requesting tenant.

        Public tilesets (tenant_id is None) and tenant-owned tilesets are returned.
        Other tenants' private tilesets are strictly excluded.
        """
        results: list[Atlas3DTilesetSource] = []
        for tileset in self._tilesets.values():
            if tileset.tenant_id is None or tileset.tenant_id == tenant_id or is_admin:
                results.append(tileset)
        return results

    def get_tileset(
        self,
        tileset_id: str,
        tenant_id: str,
        is_admin: bool = False,
    ) -> Atlas3DTilesetSource:
        """Retrieve a specific 3D Tileset, verifying tenant authorization.

        Raises:
            GlobeTilesetNotFoundError: If the tileset does not exist.
            GlobeTilesetAccessDeniedError: If the tileset belongs to another tenant.
        """
        tileset = self._tilesets.get(tileset_id)
        if not tileset:
            raise GlobeTilesetNotFoundError(tileset_id)

        # Enforce multi-tenant boundary (Fixture G)
        if tileset.tenant_id is not None and tileset.tenant_id != tenant_id and not is_admin:
            raise GlobeTilesetAccessDeniedError(tileset_id=tileset_id, tenant_id=tenant_id)

        return tileset

    def register_tileset(self, tileset: Atlas3DTilesetSource) -> None:
        """Register a new 3D Tileset into the runtime registry."""
        self._tilesets[tileset.tileset_id] = tileset
