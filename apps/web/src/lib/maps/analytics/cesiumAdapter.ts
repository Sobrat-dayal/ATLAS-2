/**
 * CesiumJS 3D Globe Compatibility Adapter for H3 Spatial Analytics (Stage 131).
 *
 * Translates 2D H3 aggregation results into Cesium-compatible 3D geographic polygons
 * and extruded data columns, preserving analytical state and provenance across 2D/3D switches.
 */

import { getColorForValue } from './colorScales';
import { cellToGeoJsonBoundary } from './h3';
import { AtlasH3Aggregate, ColorPalette } from './types';

export interface CesiumH3PolygonEntity {
  id: string;
  positionsDegrees: number[]; // Flattened [lon0, lat0, lon1, lat1, ...]
  rgbaColor: [number, number, number, number]; // [r, g, b, a] 0-255
  extrudedHeightMeters: number;
  aggregate: AtlasH3Aggregate;
}

/**
 * Converts Atlas H3 aggregates into Cesium-renderable 3D polygon definitions.
 */
export function convertH3AggregatesToCesiumEntities(
  aggregates: AtlasH3Aggregate[],
  options: {
    palette?: ColorPalette;
    minVal?: number;
    maxVal?: number;
    extruded?: boolean;
    elevationScale?: number;
    opacity?: number;
  } = {}
): CesiumH3PolygonEntity[] {
  const palette = options.palette || 'viridis';
  const minVal = options.minVal ?? 0;
  const maxVal = options.maxVal ?? 100;
  const extruded = options.extruded ?? false;
  const elevationScale = options.elevationScale ?? 50;
  const opacity = options.opacity ?? 0.8;

  const entities: CesiumH3PolygonEntity[] = [];

  for (const agg of aggregates) {
    try {
      const ring = cellToGeoJsonBoundary(agg.h3_cell_id);
      if (ring.length < 3) continue;

      // Flatten coordinates into [lon0, lat0, lon1, lat1, ...]
      const flattened: number[] = [];
      for (const [lon, lat] of ring) {
        flattened.push(lon, lat);
      }

      // Compute color
      const rgba = getColorForValue(
        agg.value,
        minVal,
        maxVal,
        palette,
        agg.is_suppressed,
        Math.round(opacity * 255)
      );

      // Compute extrusion height (meters)
      let height = 0;
      if (extruded && !agg.is_suppressed && agg.value !== null && !isNaN(agg.value)) {
        const range = maxVal - minVal;
        const norm = range > 0 ? (agg.value - minVal) / range : 0.5;
        height = Math.max(100, norm * elevationScale * 1000);
      }

      entities.push({
        id: `cesium-h3-${agg.h3_cell_id}`,
        positionsDegrees: flattened,
        rgbaColor: rgba,
        extrudedHeightMeters: height,
        aggregate: agg,
      });
    } catch {
      // Ignore individual cell calculation errors safely
    }
  }

  return entities;
}

