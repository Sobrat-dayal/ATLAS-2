/**
 * Client-Side H3 Operations and Geometry Builder (Stage 131).
 *
 * Wraps h3-js v4.5.0 with coordinate validation, GeoJSON ring generation,
 * pentagon detection, area normalization, and antimeridian handling.
 */

import * as h3 from 'h3-js';

/**
 * Assigns a geographic coordinate pair to an H3 hexagon cell index.
 */
export function latLngToCell(lat: number, lng: number, resolution: number): string {
  if (resolution < 0 || resolution > 15) {
    throw new Error(`Invalid H3 resolution ${resolution}. Must be between 0 and 15.`);
  }
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    throw new Error(`Coordinates [${lat}, ${lng}] are out of WGS84 bounds.`);
  }
  return h3.latLngToCell(lat, lng, resolution);
}

/**
 * Computes centroid [latitude, longitude] for an H3 cell.
 */
export function cellToLatLng(cellId: string): [number, number] {
  validateCell(cellId);
  return h3.cellToLatLng(cellId);
}

/**
 * Generates closed GeoJSON coordinate ring [[lon, lat], ...] for an H3 cell.
 */
export function cellToGeoJsonBoundary(cellId: string): [number, number][] {
  validateCell(cellId);
  // h3.cellToBoundary returns [[lat0, lng0], [lat1, lng1], ...]
  const rawVertices = h3.cellToBoundary(cellId);

  const coords: [number, number][] = [];
  let hasPositive = false;
  let hasNegative = false;

  for (const [lat, lng] of rawVertices) {
    if (lng > 90) hasPositive = true;
    if (lng < -90) hasNegative = true;
    coords.push([lng, lat]);
  }

  // Antimeridian wrap normalization
  if (hasPositive && hasNegative) {
    for (const pt of coords) {
      if (pt[0] < 0) pt[0] += 360;
    }
  }

  // Ensure closed ring
  if (coords.length > 0) {
    const first = coords[0];
    const last = coords[coords.length - 1];
    if (first[0] !== last[0] || first[1] !== last[1]) {
      coords.push([first[0], first[1]]);
    }
  }

  return coords;
}

/**
 * Traverses hierarchy to return parent cell at coarser resolution.
 */
export function cellToParent(cellId: string, parentResolution: number): string {
  validateCell(cellId);
  const currentRes = h3.getResolution(cellId);
  if (parentResolution > currentRes) {
    throw new Error(`Parent resolution ${parentResolution} cannot be finer than cell resolution ${currentRes}`);
  }
  return h3.cellToParent(cellId, parentResolution);
}

/**
 * Traverses hierarchy to return all child cells at finer resolution.
 */
export function cellToChildren(cellId: string, childResolution: number): string[] {
  validateCell(cellId);
  const currentRes = h3.getResolution(cellId);
  if (childResolution < currentRes) {
    throw new Error(`Child resolution ${childResolution} cannot be coarser than cell resolution ${currentRes}`);
  }
  return h3.cellToChildren(cellId, childResolution);
}

/**
 * Returns resolution level [0-15].
 */
export function getResolution(cellId: string): number {
  validateCell(cellId);
  return h3.getResolution(cellId);
}

/**
 * Validates that string is a valid H3 index.
 */
export function isValidCell(cellId: string): boolean {
  return h3.isValidCell(cellId);
}

/**
 * Returns true if cell is a pentagon (5 vertices).
 */
export function isPentagon(cellId: string): boolean {
  validateCell(cellId);
  return h3.isPentagon(cellId);
}

/**
 * Computes exact surface area of an H3 cell in square kilometers (km²).
 */
export function cellAreaKm2(cellId: string): number {
  validateCell(cellId);
  return h3.cellArea(cellId, 'km2');
}

/**
 * Converts a polygon coordinate ring into covering H3 cells.
 */
export function polygonToCells(coordinates: [number, number][], resolution: number): string[] {
  if (resolution < 0 || resolution > 15) {
    throw new Error(`Invalid H3 resolution ${resolution}`);
  }
  // Convert [lon, lat] GeoJSON to [lat, lon] for h3-js
  const latLngCoords: [number, number][] = coordinates.map(([lon, lat]) => [lat, lon]);
  return h3.polygonToCells(latLngCoords, resolution);
}

function validateCell(cellId: string): void {
  if (!cellId || typeof cellId !== 'string' || !h3.isValidCell(cellId)) {
    throw new Error(`Invalid H3 cell index: "${cellId}"`);
  }
}

