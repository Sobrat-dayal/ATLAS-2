/**
 * Bounding Box & Antimeridian Normalization for ATLAS Maps V1.
 */

import { GeoBoundingBox } from "./types";

export function crossesAntimeridian(bbox: GeoBoundingBox): boolean {
  return bbox.west > bbox.east;
}

export function normalizeBoundingBox(bbox: GeoBoundingBox): [number, number, number, number] {
  return [bbox.west, bbox.south, bbox.east, bbox.north];
}

export function isPointInsideBounds(lon: number, lat: number, bbox: GeoBoundingBox): boolean {
  if (lat < bbox.south || lat > bbox.north) return false;
  if (crossesAntimeridian(bbox)) {
    return lon >= bbox.west || lon <= bbox.east;
  }
  return lon >= bbox.west && lon <= bbox.east;
}

