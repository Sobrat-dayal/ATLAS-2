'use client';

import React from 'react';
import { RegionalSummary } from '@/lib/maps/infrastructure/types';
import { SECTOR_VISUALS } from '@/lib/maps/infrastructure/sectorStyles';
import { X, Globe2, Layers, Zap } from 'lucide-react';

interface InfrastructureRegionalSummaryProps {
  summary: RegionalSummary | null;
  onClose: () => void;
}

export const InfrastructureRegionalSummary: React.FC<InfrastructureRegionalSummaryProps> = ({
  summary,
  onClose,
}) => {
  if (!summary) return null;

  return (
    <div className="absolute left-4 top-16 bottom-4 w-96 max-w-[calc(100vw-32px)] bg-zinc-950/95 border border-zinc-800 rounded-xl shadow-2xl backdrop-blur-xl flex flex-col z-30 overflow-hidden text-xs">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/80 bg-zinc-900/50 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5 text-cyan-400 font-semibold tracking-wider uppercase text-[10px] mb-1">
            <Globe2 className="w-3.5 h-3.5" />
            Regional Profile
          </div>
          <h3 className="font-semibold text-sm text-zinc-100 truncate">{summary.region_name}</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-zinc-400 hover:text-zinc-100 bg-zinc-800/40 hover:bg-zinc-800 rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Summary Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Core Distinct Counting Cards */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded">
            <span className="text-[10px] text-zinc-400 uppercase font-mono">Distinct Facilities</span>
            <div className="text-xl font-bold text-zinc-100 font-mono mt-0.5">
              {summary.facility_count}
            </div>
            <span className="text-[10px] text-zinc-500">Parent assets / sites</span>
          </div>
          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded">
            <span className="text-[10px] text-zinc-400 uppercase font-mono">Generating / Child Units</span>
            <div className="text-xl font-bold text-zinc-100 font-mono mt-0.5">
              {summary.unit_count}
            </div>
            <span className="text-[10px] text-zinc-500">Turbines, berths, segments</span>
          </div>
        </div>

        {/* Sector Distribution */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-500" />
            Sector Distribution
          </span>
          <div className="space-y-1.5">
            {Object.entries(summary.sector_breakdown).map(([secKey, count]) => {
              if (count === 0) return null;
              const meta = SECTOR_VISUALS[secKey as keyof typeof SECTOR_VISUALS] || {
                label: secKey,
                color: '#38bdf8',
              };
              const pct = ((count / summary.total_assets) * 100).toFixed(0);

              return (
                <div key={secKey} className="p-2 bg-zinc-900/40 border border-zinc-800/60 rounded">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-zinc-200">{meta.label}</span>
                    <span className="font-mono text-zinc-400">
                      {count} <span className="text-zinc-600">({pct}%)</span>
                    </span>
                  </div>
                  <div className="w-full bg-zinc-800/80 rounded-full h-1 overflow-hidden">
                    <div
                      style={{ width: `${pct}%`, backgroundColor: meta.color }}
                      className="h-full rounded-full"
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Status Distribution */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
            Operational Lifecycle
          </span>
          <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px]">
            {Object.entries(summary.status_breakdown).map(([stat, count]) => {
              if (count === 0) return null;
              return (
                <div key={stat} className="p-2 bg-zinc-900/40 border border-zinc-800/60 rounded flex justify-between">
                  <span className="text-zinc-400 capitalize">{stat.replace('_', ' ')}</span>
                  <span className="text-zinc-200 font-semibold">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
