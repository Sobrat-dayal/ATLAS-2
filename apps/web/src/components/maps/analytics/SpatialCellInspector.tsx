/**
 * Spatial Cell Inspector Component (Stage 131).
 *
 * Displays detailed, source-backed cell attributes, geodetic area, observation counts,
 * density normalization, and k-anonymity privacy disclosure.
 */

import React from 'react';
import { ShieldAlert, X } from 'lucide-react';

import { isPentagon } from '@/lib/maps/analytics/h3';
import { AtlasH3Aggregate } from '@/lib/maps/analytics/types';

interface SpatialCellInspectorProps {
  cell: AtlasH3Aggregate | null;
  onClose: () => void;
  className?: string;
}

export function SpatialCellInspector({ cell, onClose, className = '' }: SpatialCellInspectorProps) {
  if (!cell) return null;

  const pentagon = isPentagon(cell.h3_cell_id);

  return (
    <div
      className={`bg-zinc-950/95 border border-zinc-800 backdrop-blur-md rounded-lg p-4 text-xs text-zinc-300 shadow-2xl pointer-events-auto flex flex-col gap-3 w-80 ${className}`}
      role="dialog"
      aria-label="H3 Cell Inspector"
    >
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-1.5">
          <span className="font-semibold text-zinc-100 uppercase tracking-wider text-[11px]">
            H3 Cell Details
          </span>
          {pentagon ? (
            <span className="bg-amber-950/80 text-amber-300 text-[9px] px-1.5 py-0.5 rounded font-mono border border-amber-800/60">
              Pentagon
            </span>
          ) : (
            <span className="bg-zinc-800 text-zinc-300 text-[9px] px-1.5 py-0.5 rounded font-mono">
              Hexagon
            </span>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-zinc-400 hover:text-zinc-100 transition-colors p-0.5"
          aria-label="Close Cell Inspector"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex flex-col gap-2 font-mono text-[11px]">
        <div>
          <span className="text-zinc-500 block text-[10px] uppercase">Cell ID</span>
          <span className="text-zinc-200 select-all font-semibold">{cell.h3_cell_id}</span>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-zinc-800/60">
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Resolution</span>
            <span className="text-zinc-200">{cell.h3_resolution}</span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Cell Area</span>
            <span className="text-zinc-200">{cell.cell_area_km2} km²</span>
          </div>
        </div>

        <div className="pt-1 border-t border-zinc-800/60">
          <span className="text-zinc-500 block text-[10px] uppercase">Aggregated Metric</span>
          {cell.is_suppressed ? (
            <div className="flex items-center gap-1.5 text-amber-400 mt-1 bg-amber-950/30 p-1.5 rounded border border-amber-800/40">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span className="text-[10px] leading-tight">
                Suppressed for Privacy (k-anonymity threshold not met)
              </span>
            </div>
          ) : (
            <div className="text-emerald-400 font-semibold text-sm">
              {cell.value !== null ? cell.value.toLocaleString(undefined, { maximumFractionDigits: 4 }) : 'N/A'}{' '}
              <span className="text-[10px] text-zinc-400 font-normal">{cell.unit}</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-zinc-800/60">
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Observations</span>
            <span className="text-zinc-200">{cell.record_count.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Density</span>
            <span className="text-zinc-200">
              {cell.density !== null && cell.density !== undefined
                ? `${cell.density.toLocaleString(undefined, { maximumFractionDigits: 2 })}/km²`
                : 'N/A'}
            </span>
          </div>
        </div>

        {cell.distinct_count !== undefined && cell.distinct_count !== null && (
          <div className="pt-1 border-t border-zinc-800/60">
            <span className="text-zinc-500 block text-[10px] uppercase">Distinct Entities</span>
            <span className="text-zinc-200">{cell.distinct_count}</span>
          </div>
        )}

        {cell.time_bucket && (
          <div className="pt-1 border-t border-zinc-800/60">
            <span className="text-zinc-500 block text-[10px] uppercase">Time Period</span>
            <span className="text-zinc-200">{cell.time_bucket}</span>
          </div>
        )}
      </div>

      <div className="text-[9px] text-zinc-500 pt-1 border-t border-zinc-800/60 leading-tight">
        Provenance: Verified spatial features indexed with H3 geodetic coordinate algorithms.
      </div>
    </div>
  );
}

