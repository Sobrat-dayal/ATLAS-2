/**
 * ATLAS 3D Globe API Client (Stage 130).
 *
 * Communicates with /api/v1/maps/globe for configuration, imagery/terrain catalogs,
 * 3D tilesets, camera conversions, and saved globe views.
 */

import {
  Atlas3DTilesetSource,
  AtlasGlobeCamera,
  GlobeImageryProvider,
  GlobeRuntimeConfig,
  GlobeTerrainProvider,
  UserGlobeView,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export async function fetchGlobeConfig(): Promise<GlobeRuntimeConfig> {
  try {
    const res = await fetch(`${API_BASE}/maps/globe/config`, {
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    // Fallback baseline config
    return {
      default_imagery_provider_id: "natural-earth",
      default_terrain_provider_id: "ellipsoid",
      ion_configured: false,
      supported_modes: ["2D", "3D"],
      max_active_viewers: 2,
      default_camera: {
        longitude: 0.0,
        latitude: 20.0,
        height_meters: 20000000.0,
        heading_radians: 0.0,
        pitch_radians: -Math.PI / 2,
        roll_radians: 0.0,
      },
    };
  }
}

export async function fetchImageryProviders(
  includeRestricted: boolean = false
): Promise<GlobeImageryProvider[]> {
  try {
    const res = await fetch(
      `${API_BASE}/maps/globe/imagery?include_restricted=${includeRestricted}`,
      { headers: { "Content-Type": "application/json" } }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return [
      {
        provider_id: "natural-earth",
        name: "Natural Earth II Global Reference",
        imagery_type: "NATURAL_EARTH",
        source_url: "https://naturalearth.cesium.com/tiles/{z}/{x}/{y}.png",
        attribution: "© Natural Earth (Public Domain)",
        licensing_policy: "cc_by_4.0",
        is_available: true,
        is_default: true,
        max_zoom: 9,
        description: "Global shaded relief and bathymetry from Natural Earth dataset.",
      },
      {
        provider_id: "carto-dark",
        name: "CARTO Dark Matter 3D",
        imagery_type: "CARTOGRAPHIC_DARK",
        source_url: "https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attribution: "© OpenStreetMap contributors, © CARTO",
        licensing_policy: "cc_by_4.0",
        is_available: true,
        is_default: false,
        max_zoom: 19,
        description: "High-contrast dark cartographic basemap designed for financial analytics.",
      },
      {
        provider_id: "carto-light",
        name: "CARTO Positron 3D",
        imagery_type: "CARTOGRAPHIC_LIGHT",
        source_url: "https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png",
        attribution: "© OpenStreetMap contributors, © CARTO",
        licensing_policy: "cc_by_4.0",
        is_available: true,
        is_default: false,
        max_zoom: 19,
        description: "Clean, low-saturation light basemap.",
      },
      {
        provider_id: "osm-standard",
        name: "OpenStreetMap 3D",
        imagery_type: "OPEN_STREET_MAP",
        source_url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: "© OpenStreetMap contributors",
        licensing_policy: "odbl_1.0",
        is_available: true,
        is_default: false,
        max_zoom: 19,
        description: "Standard global crowdsourced geographic layer.",
      },
      {
        provider_id: "satellite-reference",
        name: "Sentinel-2 Cloudless Satellite Imagery",
        imagery_type: "SATELLITE",
        source_url: "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg",
        attribution: "© Copernicus Sentinel data, © EOX IT Services GmbH",
        licensing_policy: "cc_by_4.0",
        is_available: true,
        is_default: false,
        max_zoom: 16,
        description: "Real global satellite mosaic from European Space Agency Sentinel-2.",
      },
    ];
  }
}

export async function fetchTerrainProviders(
  includeRestricted: boolean = false
): Promise<GlobeTerrainProvider[]> {
  try {
    const res = await fetch(
      `${API_BASE}/maps/globe/terrain?include_restricted=${includeRestricted}`,
      { headers: { "Content-Type": "application/json" } }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return [
      {
        provider_id: "ellipsoid",
        name: "WGS84 Ellipsoid (No Elevation)",
        terrain_type: "ELLIPSOID",
        attribution: "WGS84 Mathematical Ellipsoid Model",
        source_url_optional: null,
        is_available: true,
        is_default: true,
        has_measured_elevation: false,
        description: "Mathematical reference ellipsoid with zero elevation distortion and guaranteed instant loading.",
      },
      {
        provider_id: "cesium-world-terrain",
        name: "Cesium World Terrain (High-Resolution Global Mesh)",
        terrain_type: "CESIUM_WORLD_TERRAIN",
        attribution: "© Cesium ion, © Copernicus, © USGS, © NASA SRTM",
        source_url_optional: "https://assets.ion.cesium.com/1",
        is_available: false,
        is_default: false,
        has_measured_elevation: true,
        description: "Quantized-mesh global terrain elevation with high-resolution topographic relief.",
      },
    ];
  }
}

export async function fetchTilesets(): Promise<Atlas3DTilesetSource[]> {
  try {
    const res = await fetch(`${API_BASE}/maps/globe/tilesets`, {
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return [
      {
        tileset_id: "atlas.reference.financial_district_3dtiles",
        dataset_id: "atlas.reference.financial_centers",
        source_type: "OGC_3D_TILES",
        source_reference: "https://assets.atlas.internal/3dtiles/london_financial/tileset.json",
        bounding_volume: {
          type: "region",
          west: -0.095,
          south: 51.51,
          east: -0.08,
          north: 51.52,
          min_height: 0.0,
          max_height: 310.0,
        },
        attribution: "© Open City 3D Model, UK Geospatial Commission",
        licensing_policy: "cc_by_4.0",
        tenant_id: null,
        is_available: true,
        data_quality: "verified",
        description: "OGC 3D Tiles 1.1 b3dm mesh of institutional financial towers and exchanges in London.",
      },
    ];
  }
}

export async function fetchGlobeViews(): Promise<UserGlobeView[]> {
  try {
    const res = await fetch(`${API_BASE}/maps/globe/views`, {
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return [];
  }
}

export async function saveGlobeView(payload: {
  name: string;
  cesium_camera: AtlasGlobeCamera;
  description?: string;
  renderer_mode?: string;
  maplibre_camera?: any;
  imagery_provider_id?: string;
  terrain_provider_id?: string;
  visible_layer_references?: string[];
  selected_feature_id?: string | null;
  quality_profile?: string;
}): Promise<UserGlobeView> {
  const res = await fetch(`${API_BASE}/maps/globe/views`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to save globe view (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function deleteGlobeView(viewId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/maps/globe/views/${viewId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to delete view ${viewId}`);
  return true;
}

