/**
 * Geographic Region Comparison Drawer / Modal (Stage 131).
 *
 * Compares identical spatial metrics between Region A and Region B,
 * calculating deltas, relative changes, and area-normalized densities.
 */

import React, { useState } from 'react';
import { ArrowRight, Scale, X } from 'lucide-react';

import { compareRegions } from '@/lib/maps/analytics/api';
import { RegionComparisonResult } from '@/lib/maps/analytics/types';

interface SpatialRegionComparisonProps {
  datasetId: string;
  metricId: string;
  aggregation: string;
  h3Resolution: number;
  onClose: () => void;
  className?: string;
}

export function SpatialRegionComparison({
  datasetId,
  metricId,
  aggregation,
  h3Resolution,
  onClose,
  className = '',
}: SpatialRegionComparisonProps) {
  const [regionAName, setRegionAName] = useState('Western Europe');
  const [regionBName, setRegionBName] = useState('North America East');
  const [result, setResult] = useState<RegionComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Default region presets
  const regionABounds: [number, number, number, number] = [-10.0, 35.0, 20.0, 60.0]; // Western Europe
  const regionBBounds: [number, number, number, number] = [-85.0, 25.0, -65.0, 48.0]; // US East

  const handleCompare = async () => {
    setLoading(true);
    setError(null);
    try {
      const cmp = await compareRegions({
        dataset_id: datasetId,
        metric_id: metricId,
        aggregation,
        region_a_name: regionAName,
        region_a_bounds: regionABounds,
        region_b_name: regionBName,
        region_b_bounds: regionBBounds,
        h3_resolution: h3Resolution,
      });
      setResult(cmp);
    } catch (err: any) {
      setError(err.message || 'Comparison failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`bg-zinc-950/95 border border-zinc-800 backdrop-blur-md rounded-lg p-4 text-xs text-zinc-300 shadow-2xl pointer-events-auto flex flex-col gap-3 w-96 ${className}`}
      role="dialog"
      aria-label="Geographic Region Comparison"
    >
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-1.5 font-semibold text-zinc-100 uppercase tracking-wider text-[11px]">
          <Scale className="w-4 h-4 text-emerald-400" />
          <span>Region Comparison</span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-400 hover:text-zinc-100 transition-colors p-0.5"
          aria-label="Close Comparison"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex flex-col gap-2">
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div>
            <label className="text-zinc-500 block uppercase mb-1">Region A</label>
            <input
              type="text"
              value={regionAName}
              onChange={(e) => setRegionAName(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-zinc-200"
            />
          </div>
          <div>
            <label className="text-zinc-500 block uppercase mb-1">Region B</label>
            <input
              type="text"
              value={regionBName}
              onChange={(e) => setRegionBName(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-zinc-200"
            />
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium py-1.5 rounded transition-colors text-[11px] flex items-center justify-center gap-1.5"
        >
          {loading ? 'Comparing...' : 'Run Statistical Comparison'}
        </button>

        {error && <div className="text-red-400 text-[10px] bg-red-950/40 p-2 rounded">{error}</div>}

        {result && (
          <div className="flex flex-col gap-2 mt-2 pt-2 border-t border-zinc-800/80 font-mono text-[11px]">
            <div className="grid grid-cols-2 gap-2 bg-zinc-900/60 p-2 rounded border border-zinc-800/50">
              <div>
                <span className="text-zinc-400 block text-[10px] truncate">{result.region_a_name}</span>
                <span className="text-zinc-100 font-semibold text-sm">
                  {result.region_a_summary.mean_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </span>
                <span className="text-[9px] text-zinc-500 block">{result.unit}</span>
                <span className="text-[9px] text-zinc-400 mt-1 block">
                  Density: {result.area_normalized_a.toLocaleString()}/km²
                </span>
              </div>
              <div>
                <span className="text-zinc-400 block text-[10px] truncate">{result.region_b_name}</span>
                <span className="text-zinc-100 font-semibold text-sm">
                  {result.region_b_summary.mean_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </span>
                <span className="text-[9px] text-zinc-500 block">{result.unit}</span>
                <span className="text-[9px] text-zinc-400 mt-1 block">
                  Density: {result.area_normalized_b.toLocaleString()}/km²
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between p-2 bg-zinc-900/40 rounded border border-zinc-800/40 text-[10px]">
              <span className="text-zinc-400">Absolute Delta:</span>
              <span className="text-zinc-100 font-semibold">
                {result.absolute_difference.toLocaleString(undefined, { maximumFractionDigits: 2 })} {result.unit}
              </span>
            </div>

            {typeof result.relative_difference_pct === 'number' && (
              <div className="flex items-center justify-between p-2 bg-zinc-900/40 rounded border border-zinc-800/40 text-[10px]">
                <span className="text-zinc-400">Relative Delta:</span>
                <span className={result.relative_difference_pct >= 0 ? 'text-emerald-400' : 'text-amber-400'}>
                  {result.relative_difference_pct > 0 ? '+' : ''}
                  {result.relative_difference_pct}%
                </span>
              </div>
            )}

            {result.higher_region && (
              <div className="text-[10px] text-emerald-400/90 flex items-center gap-1">
                <ArrowRight className="w-3 h-3" />
                <span>Higher concentration in {result.higher_region}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
