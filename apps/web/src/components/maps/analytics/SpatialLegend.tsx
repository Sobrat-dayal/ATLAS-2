/**
 * Data-Driven Spatial Analytics Legend (Stage 131).
 *
 * Renders source-backed color gradient, min/max values, aggregation units,
 * resolution indicator, and source attribution pill.
 */

import React from 'react';

import { getCssGradient, PALETTES } from '@/lib/maps/analytics/colorScales';
import { ColorPalette, SpatialAnalyticsResult } from '@/lib/maps/analytics/types';

interface SpatialLegendProps {
  result: SpatialAnalyticsResult | null;
  palette: ColorPalette;
  metricDisplayName?: string;
  className?: string;
}

export function SpatialLegend({
  result,
  palette,
  metricDisplayName,
  className = '',
}: SpatialLegendProps) {
  if (!result || result.aggregates.length === 0) return null;

  const summary = result.summary;
  const gradient = getCssGradient(palette);
  const minDisplay = summary.min_value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  const maxDisplay = summary.max_value.toLocaleString(undefined, { maximumFractionDigits: 2 });

  return (
    <div
      className={`bg-zinc-950/90 border border-zinc-800 backdrop-blur-md rounded-md p-3 text-xs text-zinc-300 shadow-xl pointer-events-auto flex flex-col gap-2 min-w-[260px] ${className}`}
      role="region"
      aria-label="Spatial Analytics Legend"
    >
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-1.5">
        <span className="font-medium text-zinc-100 uppercase tracking-wider text-[10px]">
          {metricDisplayName || result.metric_id}
        </span>
        <span className="text-[10px] text-zinc-400 font-mono">
          H3 Res: {result.h3_resolution}
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <div
          className="h-2.5 w-full rounded-sm border border-zinc-700/50"
          style={{ background: gradient }}
        />
        <div className="flex justify-between text-[10px] font-mono text-zinc-400">
          <span>{minDisplay}</span>
          <span>{result.unit || summary.unit}</span>
          <span>{maxDisplay}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[9px] text-zinc-500 pt-1 border-t border-zinc-800/60 font-mono">
        <span>{result.aggregates.length.toLocaleString()} cells</span>
        {summary.suppressed_cells > 0 && (
          <span className="text-amber-400/80">{summary.suppressed_cells} suppressed</span>
        )}
        <span className="truncate max-w-[120px]">{result.source_attribution || 'ATLAS Source'}</span>
      </div>
    </div>
  );
}

