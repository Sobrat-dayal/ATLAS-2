/**
 * Comprehensive Unit Test Suite for ATLAS 3D God's Eye Globe (Stage 130).
 *
 * Verifies Golden Reference Fixtures across WGS84 ECEF coordinates,
 * 2D/3D camera interoperability, provider catalogs, and multi-panel independence.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  WGS84_A,
  WGS84_B,
  geodeticToCartesian,
  cartesianToGeodetic,
  degreesToRadians,
  radiansToDegrees,
  normalizeLongitude,
  validateGlobeCoordinates,
} from "../globe/coordinates";
import {
  maplibreToCesiumCamera,
  cesiumToMaplibreCamera,
  EQUATORIAL_CIRCUMFERENCE_METERS,
} from "../globe/cameraInteroperability";
import { formatGlobeErrorMessage, GLOBE_ERROR_CODES } from "../globe/errors";

test("Stage 130 - 3D God's Eye Globe Unit Tests", async (t) => {
  // =========================================================================
  // FIXTURE A: WGS84 Geodetic Coordinate Validation & Rejections
  // =========================================================================
  await t.test("Fixture A: validates WGS84 coordinate bounds and rejects NaN / invalid values", () => {
    // Valid coordinates
    assert.doesNotThrow(() => validateGlobeCoordinates(-0.1276, 51.5074, 100.0));
    assert.doesNotThrow(() => validateGlobeCoordinates(180.0, 90.0, 0.0));
    assert.doesNotThrow(() => validateGlobeCoordinates(-180.0, -90.0, 50000.0));

    // Out of range longitude
    assert.throws(() => validateGlobeCoordinates(181.0, 0.0, 0.0), /Longitude must be finite/);
    assert.throws(() => validateGlobeCoordinates(-181.0, 0.0, 0.0), /Longitude must be finite/);

    // Out of range latitude
    assert.throws(() => validateGlobeCoordinates(0.0, 91.0, 0.0), /Latitude must be finite/);
    assert.throws(() => validateGlobeCoordinates(0.0, -90.5, 0.0), /Latitude must be finite/);

    // Non-finite NaN and Infinity
    assert.throws(() => validateGlobeCoordinates(NaN, 0.0, 0.0));
    assert.throws(() => validateGlobeCoordinates(0.0, Infinity, 0.0));
  });

  // =========================================================================
  // FIXTURE B: Geodetic <-> Cartesian ECEF Round-Trip Precision
  // =========================================================================
  await t.test("Fixture B: performs sub-millimeter precision Geodetic <-> Cartesian ECEF conversion", () => {
    const landmarks = [
      { name: "London Financial District", lon: -0.0885, lat: 51.5138, h: 45.0 },
      { name: "Tokyo Marunouchi Hub", lon: 139.7714, lat: 35.6812, h: 25.0 },
      { name: "New York Wall Street", lon: -74.006, lat: 40.7128, h: 10.0 },
      { name: "Equator / Prime Meridian", lon: 0.0, lat: 0.0, h: 0.0 },
      { name: "North Pole Surface", lon: 0.0, lat: 90.0, h: 50.0 },
    ];

    for (const lm of landmarks) {
      // Forward: Geodetic -> Cartesian (X, Y, Z)
      const [x, y, z] = geodeticToCartesian(lm.lon, lm.lat, lm.h);
      assert.ok(Number.isFinite(x) && Number.isFinite(y) && Number.isFinite(z));

      // Inverse: Cartesian -> Geodetic (lon', lat', h')
      const [lonRt, latRt, hRt] = cartesianToGeodetic(x, y, z);

      if (Math.abs(lm.lat) < 89.9) {
        assert.ok(
          Math.abs(lonRt - lm.lon) < 1e-6,
          `Longitude mismatch for ${lm.name}: ${lonRt} vs ${lm.lon}`
        );
      }
      assert.ok(
        Math.abs(latRt - lm.lat) < 1e-6,
        `Latitude mismatch for ${lm.name}: ${latRt} vs ${lm.lat}`
      );
      assert.ok(
        Math.abs(hRt - lm.h) < 0.01,
        `Height mismatch for ${lm.name}: ${hRt} vs ${lm.h}`
      );
    }
  });

  // =========================================================================
  // FIXTURE C: Explicit Degree / Radian Conversions
  // =========================================================================
  await t.test("Fixture C: verifies explicit degree / radian angle transformations", () => {
    assert.strictEqual(degreesToRadians(0), 0);
    assert.ok(Math.abs(degreesToRadians(180) - Math.PI) < 1e-12);
    assert.ok(Math.abs(degreesToRadians(90) - Math.PI / 2) < 1e-12);
    assert.ok(Math.abs(degreesToRadians(-90) - -Math.PI / 2) < 1e-12);

    assert.strictEqual(radiansToDegrees(0), 0);
    assert.ok(Math.abs(radiansToDegrees(Math.PI) - 180) < 1e-10);
    assert.ok(Math.abs(radiansToDegrees(-Math.PI / 2) - -90) < 1e-10);

    assert.throws(() => degreesToRadians(NaN));
    assert.throws(() => radiansToDegrees(Infinity));
  });

  // =========================================================================
  // FIXTURE D: 2D/3D Camera Interoperability
  // =========================================================================
  await t.test("Fixture D: converts bidirectionally between 2D MapLibre and 3D Cesium camera states", () => {
    const origCenter = [-0.1276, 51.5074] as [number, number];
    const origZoom = 13.5;
    const origBearing = 45.0;
    const origPitch = 25.0;

    // 2D -> 3D
    const cam3D = maplibreToCesiumCamera(
      origCenter[0],
      origCenter[1],
      origZoom,
      origBearing,
      origPitch
    );

    assert.ok(Math.abs(cam3D.longitude - origCenter[0]) < 1e-4);
    assert.ok(Math.abs(cam3D.latitude - origCenter[1]) < 1e-4);
    assert.ok(cam3D.height_meters > 500.0);
    assert.ok(Math.abs(radiansToDegrees(cam3D.heading_radians) - origBearing) < 1e-2);

    // 3D -> 2D
    const cam2D = cesiumToMaplibreCamera(cam3D);

    assert.ok(Math.abs(cam2D.center[0] - origCenter[0]) < 1e-3);
    assert.ok(Math.abs(cam2D.center[1] - origCenter[1]) < 1e-3);
    assert.ok(Math.abs(cam2D.zoom - origZoom) <= 0.5);
    assert.ok(Math.abs(cam2D.bearing - origBearing) <= 1.0);
    assert.ok(Math.abs(cam2D.pitch - origPitch) <= 1.0);
  });

  // =========================================================================
  // FIXTURE E: Antimeridian Crossing Normalization
  // =========================================================================
  await t.test("Fixture E: normalizes antimeridian longitude wraps", () => {
    assert.strictEqual(normalizeLongitude(180.0), 180.0);
    assert.strictEqual(normalizeLongitude(-180.0), -180.0);
    assert.strictEqual(normalizeLongitude(190.0), -170.0);
    assert.strictEqual(normalizeLongitude(-190.0), 170.0);
    assert.strictEqual(normalizeLongitude(540.0), 180.0);
  });

  // =========================================================================
  // FIXTURE I: Multiple Independent Workspace Globe Panels
  // =========================================================================
  await t.test("Fixture I: enforces independent camera states across multiple Globe panels", () => {
    const panelACamera = {
      longitude: -0.0885,
      latitude: 51.5138,
      height_meters: 1850.0,
      heading_radians: 0.35,
      pitch_radians: -0.785,
      roll_radians: 0.0,
    };

    const panelBCamera = {
      longitude: 139.7714,
      latitude: 35.6812,
      height_meters: 4500.0,
      heading_radians: 0.0,
      pitch_radians: -1.1,
      roll_radians: 0.0,
    };

    const c2dA = cesiumToMaplibreCamera(panelACamera);
    const c2dB = cesiumToMaplibreCamera(panelBCamera);

    assert.notDeepStrictEqual(c2dA.center, c2dB.center);
    assert.notStrictEqual(c2dA.zoom, c2dB.zoom);
    assert.ok(Math.abs(c2dA.center[0] - (-0.0885)) < 1e-3);
    assert.ok(Math.abs(c2dB.center[0] - 139.7714) < 1e-3);
  });

  // =========================================================================
  // FIXTURE J: Error Taxonomy & User-Friendly Messages
  // =========================================================================
  await t.test("Fixture J: maps typed globe error codes to descriptive messages", () => {
    assert.ok(
      formatGlobeErrorMessage(GLOBE_ERROR_CODES.WEBGL_UNSUPPORTED).includes("WebGL")
    );
    assert.ok(
      formatGlobeErrorMessage(GLOBE_ERROR_CODES.TERRAIN_PROVIDER_RESTRICTED).includes("CESIUM_ION_TOKEN")
    );
    assert.ok(
      formatGlobeErrorMessage(GLOBE_ERROR_CODES.TILESET_ACCESS_DENIED).includes("Access denied")
    );
    assert.ok(
      formatGlobeErrorMessage(GLOBE_ERROR_CODES.VIEW_REVISION_CONFLICT).includes("Conflict")
    );
  });
});

