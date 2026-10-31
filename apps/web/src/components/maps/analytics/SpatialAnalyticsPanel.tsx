/**
 * ATLAS Spatial Analytics Control Panel (Stage 131).
 *
 * Professional financial analytics controls:
 * - Dataset and Metric discovery
 * - Visualization mode selection (H3, Points, Heatmap, HexGrid)
 * - Aggregation method selection (Sum, Mean, Count, Density, Weighted Mean, Distinct)
 * - H3 Resolution slider
 * - Palette and Extrusion controls
 * - Regional Comparison trigger
 */

import React from 'react';
import {
  BarChart3,
  Box,
  Flame,
  Grid,
  Hexagon,
  Layers,
  MapPin,
  Scale,
  Sliders,
  X,
} from 'lucide-react';

import {
  ColorPalette,
  SpatialAggregationMethod,
  SpatialMetricDefinition,
  SpatialVisualizationType,
} from '@/lib/maps/analytics/types';

interface SpatialAnalyticsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  datasetId: string;
  onDatasetChange: (id: string) => void;
  metricId: string;
  onMetricChange: (id: string) => void;
  metrics: SpatialMetricDefinition[];
  visualizationType: SpatialVisualizationType;
  onVisualizationChange: (type: SpatialVisualizationType) => void;
  aggregation: SpatialAggregationMethod;
  onAggregationChange: (method: SpatialAggregationMethod) => void;
  h3Resolution: number;
  onH3ResolutionChange: (res: number) => void;
  palette: ColorPalette;
  onPaletteChange: (palette: ColorPalette) => void;
  isExtruded: boolean;
  onExtrudedChange: (extruded: boolean) => void;
  opacity: number;
  onOpacityChange: (opacity: number) => void;
  onOpenComparison: () => void;
  isLoading: boolean;
  error: string | null;
  className?: string;
}

export function SpatialAnalyticsPanel({
  isOpen,
  onClose,
  datasetId,
  onDatasetChange,
  metricId,
  onMetricChange,
  metrics,
  visualizationType,
  onVisualizationChange,
  aggregation,
  onAggregationChange,
  h3Resolution,
  onH3ResolutionChange,
  palette,
  onPaletteChange,
  isExtruded,
  onExtrudedChange,
  opacity,
  onOpacityChange,
  onOpenComparison,
  isLoading,
  error,
  className = '',
}: SpatialAnalyticsPanelProps) {
  if (!isOpen) return null;

  const currentMetric = metrics.find((m) => m.metric_id === metricId);

  return (
    <div
      className={`bg-zinc-950/95 border border-zinc-800 backdrop-blur-md rounded-lg p-4 text-xs text-zinc-300 shadow-2xl pointer-events-auto flex flex-col gap-4 w-84 max-h-[85vh] overflow-y-auto ${className}`}
      role="region"
      aria-label="Spatial Analytics Controls"
    >
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-1.5 font-semibold text-zinc-100 uppercase tracking-wider text-[11px]">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <span>Spatial Analytics</span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-400 hover:text-zinc-100 transition-colors p-0.5"
          aria-label="Close Analytics Panel"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/60 rounded p-2 text-red-300 text-[10px]">
          {error}
        </div>
      )}

      {/* Dataset Selector */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[10px] text-zinc-500 uppercase font-mono tracking-wider">
          Spatial Dataset
        </label>
        <select
          value={datasetId}
          onChange={(e) => onDatasetChange(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-100 text-xs focus:outline-none focus:border-emerald-500"
        >
          <option value="financial_centers_global">Global Financial Monetary Hubs</option>
        </select>
      </div>

      {/* Visualization Type */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[10px] text-zinc-500 uppercase font-mono tracking-wider">
          Visualization Mode
        </label>
        <div className="grid grid-cols-2 gap-1.5">
          <button
            onClick={() => onVisualizationChange('h3_hexagon')}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] border transition-colors ${
              visualizationType === 'h3_hexagon'
                ? 'bg-zinc-800 border-emerald-500 text-zinc-100 font-medium'
                : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Hexagon className="w-3.5 h-3.5 text-emerald-400" />
            <span>H3 Hexagons</span>
          </button>

          <button
            onClick={() => onVisualizationChange('scatterplot')}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] border transition-colors ${
              visualizationType === 'scatterplot'
                ? 'bg-zinc-800 border-emerald-500 text-zinc-100 font-medium'
                : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-blue-400" />
            <span>Points</span>
          </button>

          <button
            onClick={() => onVisualizationChange('heatmap')}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] border transition-colors ${
              visualizationType === 'heatmap'
                ? 'bg-zinc-800 border-emerald-500 text-zinc-100 font-medium'
                : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            <span>Heatmap</span>
          </button>

          <button
            onClick={() => onVisualizationChange('hexagon_grid')}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] border transition-colors ${
              visualizationType === 'hexagon_grid'
                ? 'bg-zinc-800 border-emerald-500 text-zinc-100 font-medium'
                : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Grid className="w-3.5 h-3.5 text-purple-400" />
            <span>Hex Grid</span>
          </button>
        </div>
      </div>

      {/* Metric Selector */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[10px] text-zinc-500 uppercase font-mono tracking-wider">
          Metric
        </label>
        <select
          value={metricId}
          onChange={(e) => onMetricChange(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-100 text-xs focus:outline-none focus:border-emerald-500"
        >
          {metrics.map((m) => (
            <option key={m.metric_id} value={m.metric_id}>
              {m.display_name} ({m.unit})
            </option>
          ))}
        </select>
        {currentMetric && (
          <span className="text-[10px] text-zinc-500 leading-tight">
            {currentMetric.description}
          </span>
        )}
      </div>

      {/* Aggregation Function */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[10px] text-zinc-500 uppercase font-mono tracking-wider">
          Aggregation Method
        </label>
        <select
          value={aggregation}
          onChange={(e) => onAggregationChange(e.target.value as SpatialAggregationMethod)}
          className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-100 text-xs focus:outline-none focus:border-emerald-500 capitalize"
        >
          {currentMetric?.allowed_aggregations.map((agg) => (
            <option key={agg} value={agg}>
              {agg.replace('_', ' ')}
            </option>
          )) || <option value="count">Count</option>}
        </select>
      </div>

      {/* H3 Resolution Slider */}
      {visualizationType === 'h3_hexagon' && (
        <div className="flex flex-col gap-1.5 pt-1 border-t border-zinc-800/80">
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-zinc-500 uppercase font-mono">H3 Resolution</span>
            <span className="font-mono text-emerald-400 font-semibold">{h3Resolution}</span>
          </div>
          <input
            type="range"
            min={1}
            max={10}
            step={1}
            value={h3Resolution}
            onChange={(e) => onH3ResolutionChange(parseInt(e.target.value, 10))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
          <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
            <span>Coarse (1)</span>
            <span>Balanced (5)</span>
            <span>Fine (10)</span>
          </div>
        </div>
      )}

      {/* Appearance Controls */}
      <div className="flex flex-col gap-2 pt-1 border-t border-zinc-800/80">
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-zinc-500 uppercase font-mono">Color Palette</span>
          <select
            value={palette}
            onChange={(e) => onPaletteChange(e.target.value as ColorPalette)}
            className="bg-zinc-900 border border-zinc-800 rounded px-2 py-0.5 text-zinc-200 text-[10px]"
          >
            <option value="viridis">Viridis (Color-blind safe)</option>
            <option value="cividis">Cividis (Color-blind safe)</option>
            <option value="magma">Magma</option>
            <option value="blues">Blues</option>
            <option value="turbo">Turbo</option>
            <option value="spectral">Spectral</option>
          </select>
        </div>

        <div className="flex items-center justify-between text-[10px]">
          <span className="text-zinc-500 uppercase font-mono">3D Extrusion</span>
          <button
            onClick={() => onExtrudedChange(!isExtruded)}
            className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
              isExtruded
                ? 'bg-emerald-950 border-emerald-500 text-emerald-300'
                : 'bg-zinc-900 border-zinc-800 text-zinc-400'
            }`}
          >
            {isExtruded ? 'Enabled' : 'Disabled'}
          </button>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[10px]">
            <span className="text-zinc-500 uppercase font-mono">Layer Opacity</span>
            <span className="font-mono text-zinc-400">{Math.round(opacity * 100)}%</span>
          </div>
          <input
            type="range"
            min={0.2}
            max={1.0}
            step={0.05}
            value={opacity}
            onChange={(e) => onOpacityChange(parseFloat(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
        </div>
      </div>

      {/* Regional Comparison Button */}
      <div className="pt-2 border-t border-zinc-800/80">
        <button
          onClick={onOpenComparison}
          className="w-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-200 text-[11px] py-1.5 rounded flex items-center justify-center gap-1.5 transition-colors font-medium"
        >
          <Scale className="w-3.5 h-3.5 text-emerald-400" />
          <span>Compare Geographic Regions</span>
        </button>
      </div>

      {isLoading && (
        <div className="text-[10px] text-emerald-400 font-mono text-center animate-pulse">
          Querying GPU & H3 indexes...
        </div>
      )}
    </div>
  );
}

