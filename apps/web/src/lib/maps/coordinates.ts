/**
 * Coordinates and Distance Formatting Utilities for ATLAS Maps V1.
 * Enforces Critical Unit Rule: Geographic degrees are NOT meters.
 */

export function formatCoordinates(lon: number, lat: number, precision: number = 4): string {
  const latDir = lat >= 0 ? "N" : "S";
  const lonDir = lon >= 0 ? "E" : "W";
  return `${Math.abs(lat).toFixed(precision)}° ${latDir}, ${Math.abs(lon).toFixed(precision)}° ${lonDir}`;
}

export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  const km = meters / 1000;
  if (km < 10) {
    return `${km.toFixed(2)} km`;
  }
  return `${km.toFixed(1)} km`;
}

export function isValidCoordinate(lon: number, lat: number): boolean {
  if (typeof lon !== "number" || typeof lat !== "number") return false;
  if (isNaN(lon) || isNaN(lat)) return false;
  return lon >= -180 && lon <= 180 && lat >= -90 && lat <= 90;
}

