/**
 * 2D/3D Camera Interoperability Engine for ATLAS Maps (Stage 130).
 *
 * Implements bidirectional state conversion between 2D MapLibre cameras
 * and 3D Cesium globe cameras with Mercator bounds clamping and nadir pitch normalization.
 */

import { AtlasGlobeCamera } from "./types";
import { normalizeLongitude, degreesToRadians, radiansToDegrees } from "./coordinates";

export const EQUATORIAL_CIRCUMFERENCE_METERS = 40075016.686;
export const WEB_MERCATOR_MAX_LATITUDE = 85.0511287798066;
export const WEB_MERCATOR_MIN_LATITUDE = -85.0511287798066;

export function maplibreToCesiumCamera(
  centerLon: number,
  centerLat: number,
  zoom: number,
  bearingDeg: number = 0.0,
  pitchDeg: number = 0.0
): AtlasGlobeCamera {
  const lon = normalizeLongitude(centerLon);
  const lat = Math.max(-90.0, Math.min(90.0, centerLat));

  const cosLat = Math.max(Math.cos(degreesToRadians(lat)), 0.05);
  // Altitude in meters from zoom level
  const heightMeters = (EQUATORIAL_CIRCUMFERENCE_METERS * cosLat) / Math.pow(2.0, zoom);
  const clampedHeight = Math.max(100.0, Math.min(25000000.0, heightMeters));

  const headingRad = degreesToRadians(bearingDeg % 360.0);
  const clampedPitchDeg = Math.max(0.0, Math.min(85.0, pitchDeg));
  const cesiumPitchRad = -Math.PI / 2 + degreesToRadians(clampedPitchDeg);

  return {
    longitude: lon,
    latitude: lat,
    height_meters: clampedHeight,
    heading_radians: headingRad,
    pitch_radians: cesiumPitchRad,
    roll_radians: 0.0,
    scene_mode: "SCENE3D",
    camera_schema_version: "1.0",
  };
}

export function cesiumToMaplibreCamera(camera: AtlasGlobeCamera): {
  center: [number, number];
  zoom: number;
  pitch: number;
  bearing: number;
} {
  const lon = normalizeLongitude(camera.longitude);
  const lat = Math.max(
    WEB_MERCATOR_MIN_LATITUDE,
    Math.min(WEB_MERCATOR_MAX_LATITUDE, camera.latitude)
  );

  const cosLat = Math.max(Math.cos(degreesToRadians(lat)), 0.05);
  const effectiveHeight = Math.max(100.0, camera.height_meters);

  const rawZoom = Math.log2((EQUATORIAL_CIRCUMFERENCE_METERS * cosLat) / effectiveHeight);
  const clampedZoom = Math.max(0.0, Math.min(22.0, Number(rawZoom.toFixed(2))));

  const bearingDeg = Number((radiansToDegrees(camera.heading_radians) % 360.0).toFixed(2));

  // Cesium pitch (-pi/2 is nadir) to MapLibre pitch (0 is nadir)
  const effectivePitchRad = Math.min(0.0, camera.pitch_radians);
  const convertedPitchDeg = radiansToDegrees(effectivePitchRad + Math.PI / 2);
  const clampedPitchDeg = Math.max(0.0, Math.min(60.0, Number(convertedPitchDeg.toFixed(2))));

  return {
    center: [Number(lon.toFixed(6)), Number(lat.toFixed(6))],
    zoom: clampedZoom,
    pitch: clampedPitchDeg,
    bearing: bearingDeg,
  };
}
