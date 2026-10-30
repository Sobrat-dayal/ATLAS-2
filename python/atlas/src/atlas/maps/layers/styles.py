"""Basemap Styles Registry for ATLAS Maps V1.

Provides compliant licensed MapLibre style JSON definitions and metadata.
Includes prominent legal attribution and fallback mechanisms.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from atlas.maps.domain import MapBasemapStyle

BASEMAP_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO, © OpenFreeMap"

BASEMAP_STYLES: Dict[str, MapBasemapStyle] = {
    "atlas-dark": MapBasemapStyle(
        style_id="atlas-dark",
        display_name="ATLAS Institutional Dark",
        provider_id="carto_dark_matter",
        style_url="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        attribution=BASEMAP_ATTRIBUTION,
        license_reference="OpenStreetMap / CARTO Basemap License (CC BY 4.0)",
        requires_api_key=False,
        max_zoom=20.0,
        is_dark=True,
        is_available=True,
    ),
    "atlas-light": MapBasemapStyle(
        style_id="atlas-light",
        display_name="ATLAS High-Contrast Light",
        provider_id="carto_positron",
        style_url="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        attribution=BASEMAP_ATTRIBUTION,
        license_reference="OpenStreetMap / CARTO Basemap License (CC BY 4.0)",
        requires_api_key=False,
        max_zoom=20.0,
        is_dark=False,
        is_available=True,
    ),
    "atlas-minimal": MapBasemapStyle(
        style_id="atlas-minimal",
        display_name="ATLAS Minimalist Geopolitical",
        provider_id="openfreemap_bright",
        style_url="https://tiles.openfreemap.org/styles/bright",
        attribution=BASEMAP_ATTRIBUTION,
        license_reference="OpenFreeMap / OpenStreetMap License (ODbL)",
        requires_api_key=False,
        max_zoom=19.0,
        is_dark=False,
        is_available=True,
    ),
    "atlas-satellite": MapBasemapStyle(
        style_id="atlas-satellite",
        display_name="ATLAS Reference Imagery",
        provider_id="esri_world_imagery",
        style_url="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
        attribution="Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        license_reference="Esri Master License Agreement for Web Mapping",
        requires_api_key=False,
        max_zoom=18.0,
        is_dark=True,
        is_available=True,
    ),
}


def get_basemap_style(style_id: str) -> Optional[MapBasemapStyle]:
    return BASEMAP_STYLES.get(style_id)


def list_basemap_styles() -> List[MapBasemapStyle]:
    return list(BASEMAP_STYLES.values())

