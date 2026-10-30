"""Imagery and Terrain Provider Registries for ATLAS 3D Globe (Stage 130).

Maintains authoritative catalog of authorized imagery sources and terrain providers
with legal attribution, licensing compliance, and honest availability reporting.
"""

from __future__ import annotations

import os

from atlas.maps.domain import LicensingPolicy
from atlas.maps.globe.domain import (
    GlobeImageryProvider,
    GlobeImageryType,
    GlobeTerrainProvider,
    GlobeTerrainType,
)
from atlas.maps.globe.errors import (
    GlobeImageryProviderNotFoundError,
    GlobeImageryProviderRestrictedError,
    GlobeTerrainProviderNotFoundError,
    GlobeTerrainProviderRestrictedError,
)

# Canonical Approved Globe Imagery Catalog
DEFAULT_IMAGERY_PROVIDERS: dict[str, GlobeImageryProvider] = {
    "natural-earth": GlobeImageryProvider(
        provider_id="natural-earth",
        name="Natural Earth II Global Reference",
        imagery_type=GlobeImageryType.NATURAL_EARTH,
        source_url="https://naturalearth.cesium.com/tiles/{z}/{x}/{y}.png",
        attribution="© Natural Earth (Public Domain)",
        licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
        is_available=True,
        is_default=True,
        max_zoom=9,
        description="Global shaded relief and bathymetry from Natural Earth dataset.",
    ),
    "carto-dark": GlobeImageryProvider(
        provider_id="carto-dark",
        name="CARTO Dark Matter 3D",
        imagery_type=GlobeImageryType.CARTOGRAPHIC_DARK,
        source_url="https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attribution="© OpenStreetMap contributors, © CARTO",
        licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
        is_available=True,
        is_default=False,
        max_zoom=19,
        description="High-contrast dark cartographic basemap designed for financial analytics.",
    ),
    "carto-light": GlobeImageryProvider(
        provider_id="carto-light",
        name="CARTO Positron 3D",
        imagery_type=GlobeImageryType.CARTOGRAPHIC_LIGHT,
        source_url="https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png",
        attribution="© OpenStreetMap contributors, © CARTO",
        licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
        is_available=True,
        is_default=False,
        max_zoom=19,
        description="Clean, low-saturation light basemap.",
    ),
    "osm-standard": GlobeImageryProvider(
        provider_id="osm-standard",
        name="OpenStreetMap 3D",
        imagery_type=GlobeImageryType.OPEN_STREET_MAP,
        source_url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution="© OpenStreetMap contributors",
        licensing_policy=LicensingPolicy.ODBL,
        is_available=True,
        is_default=False,
        max_zoom=19,
        description="Standard global crowdsourced geographic layer.",
    ),
    "satellite-reference": GlobeImageryProvider(
        provider_id="satellite-reference",
        name="Sentinel-2 Cloudless Satellite Imagery",
        imagery_type=GlobeImageryType.SATELLITE,
        source_url="https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg",
        attribution="© Copernicus Sentinel data, © EOX IT Services GmbH",
        licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
        is_available=True,
        is_default=False,
        max_zoom=16,
        description="Real global satellite mosaic from European Space Agency Sentinel-2.",
    ),
    "restricted-premium-satellite": GlobeImageryProvider(
        provider_id="restricted-premium-satellite",
        name="Enterprise High-Resolution Orthoimagery (Licensed)",
        imagery_type=GlobeImageryType.SATELLITE,
        source_url="https://enterprise-satellite.internal.atlas/v1/tiles/{z}/{x}/{y}.png",
        attribution="© Proprietary Commercial Aerial Imagery Provider",
        licensing_policy=LicensingPolicy.PROPRIETARY_LICENSED,
        is_available=False,
        is_default=False,
        max_zoom=21,
        description="Restricted enterprise commercial aerial dataset requiring special entitlement.",
    ),
}

# Canonical Approved Globe Terrain Catalog
DEFAULT_TERRAIN_PROVIDERS: dict[str, GlobeTerrainProvider] = {
    "ellipsoid": GlobeTerrainProvider(
        provider_id="ellipsoid",
        name="WGS84 Ellipsoid (No Elevation)",
        terrain_type=GlobeTerrainType.ELLIPSOID,
        attribution="WGS84 Mathematical Ellipsoid Model",
        source_url_optional=None,
        is_available=True,
        is_default=True,
        has_measured_elevation=False,
        description="Mathematical reference ellipsoid with zero elevation distortion and guaranteed instant loading.",
    ),
    "cesium-world-terrain": GlobeTerrainProvider(
        provider_id="cesium-world-terrain",
        name="Cesium World Terrain (High-Resolution Global Mesh)",
        terrain_type=GlobeTerrainType.CESIUM_WORLD_TERRAIN,
        attribution="© Cesium ion, © Copernicus, © USGS, © NASA SRTM",
        source_url_optional="https://assets.ion.cesium.com/1",
        is_available=bool(os.environ.get("CESIUM_ION_TOKEN")),
        is_default=False,
        has_measured_elevation=True,
        description="Quantized-mesh global terrain elevation with high-resolution topographic relief.",
    ),
    "restricted-military-dtm": GlobeTerrainProvider(
        provider_id="restricted-military-dtm",
        name="High-Resolution LiDAR Digital Terrain Model",
        terrain_type=GlobeTerrainType.LICENSED_TERRAIN,
        attribution="© Sovereign Hydrographic & Topographic Office",
        source_url_optional="https://restricted-terrain.internal.atlas/dtm",
        is_available=False,
        is_default=False,
        has_measured_elevation=True,
        description="Sub-meter resolution terrain model restricted to sovereign or authorized enterprise clients.",
    ),
}


class AtlasGlobeProviderRegistry:
    """Registry managing available imagery and terrain providers with entitlement enforcement."""

    def __init__(self) -> None:
        self._imagery: dict[str, GlobeImageryProvider] = dict(DEFAULT_IMAGERY_PROVIDERS)
        self._terrain: dict[str, GlobeTerrainProvider] = dict(DEFAULT_TERRAIN_PROVIDERS)

    def list_imagery(self, include_restricted: bool = False) -> list[GlobeImageryProvider]:
        if include_restricted:
            return list(self._imagery.values())
        return [p for p in self._imagery.values() if p.is_available]

    def get_imagery(self, provider_id: str, tenant_entitled: bool = True) -> GlobeImageryProvider:
        provider = self._imagery.get(provider_id)
        if not provider:
            raise GlobeImageryProviderNotFoundError(provider_id)
        if not provider.is_available or not tenant_entitled:
            if provider.licensing_policy in (
                LicensingPolicy.PROPRIETARY_LICENSED,
                LicensingPolicy.RESTRICTED_ACCESS,
            ):
                raise GlobeImageryProviderRestrictedError(
                    provider_id, "Tenant does not hold an active commercial imagery license"
                )
            raise GlobeImageryProviderRestrictedError(provider_id, "Provider currently unavailable")
        return provider

    def list_terrain(self, include_restricted: bool = False) -> list[GlobeTerrainProvider]:
        if include_restricted:
            return list(self._terrain.values())
        return [p for p in self._terrain.values() if p.is_available]

    def get_terrain(self, provider_id: str, tenant_entitled: bool = True) -> GlobeTerrainProvider:
        provider = self._terrain.get(provider_id)
        if not provider:
            raise GlobeTerrainProviderNotFoundError(provider_id)
        if not provider.is_available or not tenant_entitled:
            if provider.terrain_type == GlobeTerrainType.LICENSED_TERRAIN:
                raise GlobeTerrainProviderRestrictedError(
                    provider_id, "Tenant not entitled to restricted terrain dataset"
                )
            if provider.terrain_type == GlobeTerrainType.CESIUM_WORLD_TERRAIN:
                raise GlobeTerrainProviderRestrictedError(
                    provider_id, "CESIUM_ION_TOKEN is not configured in environment"
                )
            raise GlobeTerrainProviderRestrictedError(provider_id, "Provider currently unavailable")
        return provider
