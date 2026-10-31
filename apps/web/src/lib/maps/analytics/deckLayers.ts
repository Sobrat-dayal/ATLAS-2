/**
 * deck.gl Layer Builders for ATLAS Spatial Analytics (Stage 131).
 *
 * Implements GPU-accelerated layers:
 * - H3HexagonLayer: Hexagonal binning via h3 cell indexes.
 * - ScatterplotLayer: High-volume point distribution.
 * - HeatmapLayer: Density / weight intensity surfaces.
 * - HexagonLayer: GPU-aggregated dynamic grid.
 */

import { HeatmapLayer, HexagonLayer } from '@deck.gl/aggregation-layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { ScatterplotLayer } from '@deck.gl/layers';

import { getColorForValue } from './colorScales';
import { AtlasH3Aggregate, ColorPalette } from './types';

export interface LayerBuilderOptions {
  palette?: ColorPalette;
  minVal?: number;
  maxVal?: number;
  extruded?: boolean;
  elevationScale?: number;
  opacity?: number;
  onHover?: (info: any) => void;
  onClick?: (info: any) => void;
}

export function buildH3HexagonLayer(
  aggregates: AtlasH3Aggregate[],
  options: LayerBuilderOptions = {}
): H3HexagonLayer<AtlasH3Aggregate> {
  const palette = options.palette || 'viridis';
  const minVal = options.minVal ?? 0;
  const maxVal = options.maxVal ?? 100;
  const extruded = options.extruded ?? false;
  const elevationScale = options.elevationScale ?? 50;

  return new H3HexagonLayer<AtlasH3Aggregate>({
    id: 'atlas-h3-hexagons',
    data: aggregates,
    pickable: true,
    wireframe: true,
    filled: true,
    extruded,
    getHexagon: (d: AtlasH3Aggregate) => d.h3_cell_id,
    getFillColor: (d: AtlasH3Aggregate) =>
      getColorForValue(d.value, minVal, maxVal, palette, d.is_suppressed, Math.round((options.opacity ?? 0.8) * 255)),
    getLineColor: [255, 255, 255, 50],
    lineWidthMinPixels: 1,
    getElevation: (d: AtlasH3Aggregate) => {
      if (d.is_suppressed || d.value === null || isNaN(d.value)) return 0;
      const range = maxVal - minVal;
      const norm = range > 0 ? (d.value - minVal) / range : 0.5;
      return Math.max(0, norm) * 1000;
    },
    elevationScale,
    updateTriggers: {
      getFillColor: [minVal, maxVal, palette, options.opacity],
      getElevation: [minVal, maxVal],
    },
    onHover: options.onHover as any,
    onClick: options.onClick as any,
  });
}

export function buildScatterplotLayer(
  points: { id: string; longitude: number; latitude: number; value?: number; label?: string }[],
  options: LayerBuilderOptions = {}
): ScatterplotLayer<any> {
  const palette = options.palette || 'viridis';
  const minVal = options.minVal ?? 0;
  const maxVal = options.maxVal ?? 100;

  return new ScatterplotLayer({
    id: 'atlas-scatterplot',
    data: points,
    pickable: true,
    opacity: options.opacity ?? 0.85,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 4,
    radiusMaxPixels: 24,
    lineWidthMinPixels: 1,
    getPosition: (d: any) => [d.longitude, d.latitude],
    getRadius: (d: any) => {
      if (!d.value) return 5000;
      const range = maxVal - minVal;
      const norm = range > 0 ? (d.value - minVal) / range : 0.5;
      return 5000 + norm * 20000;
    },
    getFillColor: (d: any) => getColorForValue(d.value ?? null, minVal, maxVal, palette, false, 220),
    getLineColor: [255, 255, 255, 120],
    updateTriggers: {
      getFillColor: [minVal, maxVal, palette],
      getRadius: [minVal, maxVal],
    },
    onHover: options.onHover as any,
    onClick: options.onClick as any,
  });
}

export function buildHeatmapLayer(
  points: { longitude: number; latitude: number; value?: number }[],
  options: { radiusPixels?: number; intensity?: number } = {}
): HeatmapLayer<any> {
  return new HeatmapLayer({
    id: 'atlas-heatmap',
    data: points,
    getPosition: (d: any) => [d.longitude, d.latitude],
    getWeight: (d: any) => (typeof d.value === 'number' ? Math.max(0, d.value) : 1),
    radiusPixels: options.radiusPixels ?? 45,
    intensity: options.intensity ?? 1.2,
    threshold: 0.05,
    aggregation: 'SUM',
  });
}

export function buildHexagonGridLayer(
  points: { longitude: number; latitude: number; value?: number }[],
  options: LayerBuilderOptions & { radius?: number } = {}
): HexagonLayer<any> {
  return new HexagonLayer({
    id: 'atlas-hexgrid',
    data: points,
    getPosition: (d: any) => [d.longitude, d.latitude],
    radius: options.radius ?? 50000,
    elevationScale: options.elevationScale ?? 50,
    extruded: options.extruded ?? true,
    pickable: true,
    onHover: options.onHover as any,
    onClick: options.onClick as any,
  });
}

