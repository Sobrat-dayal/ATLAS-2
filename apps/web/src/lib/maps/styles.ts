/**
 * Basemap Styles & Tile Licensing Configuration for ATLAS Maps V1.
 */

import { MapBasemapStyle } from "./types";

export const BASEMAP_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO, © OpenFreeMap";

export const PRESET_BASEMAP_STYLES: MapBasemapStyle[] = [
  {
    style_id: "atlas-dark",
    display_name: "ATLAS Institutional Dark",
    provider_id: "carto_dark_matter",
    style_url: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    attribution: BASEMAP_ATTRIBUTION,
    license_reference: "OpenStreetMap / CARTO Basemap License (CC BY 4.0)",
    is_dark: true,
    is_available: true,
    max_zoom: 20,
  },
  {
    style_id: "atlas-light",
    display_name: "ATLAS High-Contrast Light",
    provider_id: "carto_positron",
    style_url: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    attribution: BASEMAP_ATTRIBUTION,
    license_reference: "OpenStreetMap / CARTO Basemap License (CC BY 4.0)",
    is_dark: false,
    is_available: true,
    max_zoom: 20,
  },
  {
    style_id: "atlas-minimal",
    display_name: "ATLAS Minimalist Geopolitical",
    provider_id: "openfreemap_bright",
    style_url: "https://tiles.openfreemap.org/styles/bright",
    attribution: BASEMAP_ATTRIBUTION,
    license_reference: "OpenFreeMap / OpenStreetMap License (ODbL)",
    is_dark: false,
    is_available: true,
    max_zoom: 19,
  },
  {
    style_id: "atlas-satellite",
    display_name: "ATLAS Reference Imagery",
    provider_id: "esri_world_imagery",
    style_url: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
    attribution: "Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
    license_reference: "Esri Master License Agreement for Web Mapping",
    is_dark: true,
    is_available: true,
    max_zoom: 18,
  },
];

export const DEFAULT_CAMERA = {
  longitude: 10.0,
  latitude: 25.0,
  zoom: 1.8,
  bearing: 0,
  pitch: 0,
  projection: "mercator",
  revision: 1,
};

