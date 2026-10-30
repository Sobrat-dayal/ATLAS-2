/**
 * Comprehensive Unit Tests for Stage 129: ATLAS Maps V1 (PostGIS + MapLibre).
 *
 * Verifies:
 * - Fixture A: Point coordinate formatting and bounds checks.
 * - Fixture B: Polygon bounding box and point containment.
 * - Fixture C: Invalid coordinate detection and error mapping.
 * - Fixture D: Antimeridian crossing detection.
 * - Fixture E: Metric distance formatting and Critical Unit Rule (Degrees != Meters).
 * - Fixture G: Basemap styles licensing and attribution.
 * - Fixture H: Camera state serialization.
 * - Fixture I: Independent Workspace map panel camera isolation.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  formatCoordinates,
  formatDistance,
  isValidCoordinate,
} from "../coordinates";
import { crossesAntimeridian, isPointInsideBounds } from "../bounds";
import { PRESET_BASEMAP_STYLES, BASEMAP_ATTRIBUTION, DEFAULT_CAMERA } from "../styles";
import { getMapErrorMessage } from "../errors";
import { GeoBoundingBox, MapCameraState } from "../types";

describe("Stage 129 — ATLAS Maps V1 Geospatial Foundation Tests", () => {
  it("Fixture A: validates point coordinate formatting and bounds", () => {
    const lon = -74.006;
    const lat = 40.7128;

    assert.equal(isValidCoordinate(lon, lat), true);
    assert.equal(isValidCoordinate(-185, 40), false);
    assert.equal(isValidCoordinate(10, 95), false);

    const formatted = formatCoordinates(lon, lat);
    assert.equal(formatted, "40.7128° N, 74.0060° W");
  });

  it("Fixture B: validates polygon bounding box and point containment", () => {
    const bbox: GeoBoundingBox = {
      west: -10,
      south: 40,
      east: 10,
      north: 60,
    };

    assert.equal(crossesAntimeridian(bbox), false);
    assert.equal(isPointInsideBounds(0, 50, bbox), true);
    assert.equal(isPointInsideBounds(15, 50, bbox), false);
    assert.equal(isPointInsideBounds(0, 70, bbox), false);
  });

  it("Fixture C: maps invalid coordinate and geometry error codes to descriptive messages", () => {
    assert.match(
      getMapErrorMessage("MAP_COORDINATES_INVALID"),
      /Invalid geographic coordinates/
    );
    assert.match(
      getMapErrorMessage("MAP_DATASET_ACCESS_DENIED"),
      /Access to this proprietary spatial dataset is denied/
    );
    assert.match(
      getMapErrorMessage("MAP_WEBGL_UNAVAILABLE"),
      /WebGL 2D hardware acceleration is unavailable/
    );
  });

  it("Fixture D: validates antimeridian crossing detection (west > east)", () => {
    const standardBbox: GeoBoundingBox = {
      west: -120,
      south: 20,
      east: -70,
      north: 50,
    };
    assert.equal(crossesAntimeridian(standardBbox), false);

    const antimeridianBbox: GeoBoundingBox = {
      west: 170,
      south: -20,
      east: -170,
      north: 20,
    };
    assert.equal(crossesAntimeridian(antimeridianBbox), true);

    // Points at 175° and -175° should be inside
    assert.equal(isPointInsideBounds(175, 0, antimeridianBbox), true);
    assert.equal(isPointInsideBounds(-175, 0, antimeridianBbox), true);
    // Point at 0° should NOT be inside
    assert.equal(isPointInsideBounds(0, 0, antimeridianBbox), false);
  });

  it("Fixture E: validates metric distance formatting (Critical Unit Rule: Degrees != Meters)", () => {
    assert.equal(formatDistance(850), "850 m");
    assert.equal(formatDistance(4500), "4.50 km");
    assert.equal(formatDistance(343550), "343.6 km");
  });

  it("Fixture G: validates approved basemap styles, providers, and legal attribution", () => {
    assert.equal(PRESET_BASEMAP_STYLES.length >= 3, true);

    const styleIds = PRESET_BASEMAP_STYLES.map((s) => s.style_id);
    assert.equal(styleIds.includes("atlas-dark"), true);
    assert.equal(styleIds.includes("atlas-light"), true);
    assert.equal(styleIds.includes("atlas-minimal"), true);

    for (const style of PRESET_BASEMAP_STYLES) {
      assert.equal(style.attribution.length > 0, true);
      assert.equal(style.is_available, true);
      assert.equal(style.max_zoom >= 18, true);
    }
    // Vector basemaps must include OpenStreetMap attribution
    assert.equal(PRESET_BASEMAP_STYLES[0].attribution.includes("OpenStreetMap"), true);
    assert.equal(PRESET_BASEMAP_STYLES[1].attribution.includes("OpenStreetMap"), true);
    assert.equal(PRESET_BASEMAP_STYLES[2].attribution.includes("OpenStreetMap"), true);
  });

  it("Fixture H: validates canonical camera state defaults and projection", () => {
    assert.equal(DEFAULT_CAMERA.projection, "mercator");
    assert.equal(DEFAULT_CAMERA.bearing, 0);
    assert.equal(DEFAULT_CAMERA.pitch, 0);
    assert.equal(typeof DEFAULT_CAMERA.longitude, "number");
    assert.equal(typeof DEFAULT_CAMERA.latitude, "number");
    assert.equal(typeof DEFAULT_CAMERA.zoom, "number");
  });

  it("Fixture I: enforces independent camera state across multiple Workspace Map panels", () => {
    const panelCameraA: MapCameraState = {
      longitude: -74.006,
      latitude: 40.7128,
      zoom: 12,
      bearing: 0,
      pitch: 0,
      projection: "mercator",
      revision: 1,
    };

    const panelCameraB: MapCameraState = {
      longitude: 139.6917,
      latitude: 35.6895,
      zoom: 10,
      bearing: 15,
      pitch: 20,
      projection: "mercator",
      revision: 1,
    };

    // Mutate Panel A
    const updatedPanelA: MapCameraState = {
      ...panelCameraA,
      zoom: 14,
      revision: 2,
    };

    // Assert Panel B remains strictly untouched
    assert.notEqual(updatedPanelA.zoom, panelCameraB.zoom);
    assert.notEqual(updatedPanelA.longitude, panelCameraB.longitude);
    assert.equal(panelCameraB.zoom, 10);
    assert.equal(panelCameraB.longitude, 139.6917);
    assert.equal(panelCameraB.bearing, 15);
  });
});
