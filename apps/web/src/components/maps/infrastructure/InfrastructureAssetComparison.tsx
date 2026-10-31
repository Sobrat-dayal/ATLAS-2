'use client';

import React from 'react';
import { X, AlertTriangle, ArrowLeftRight, Check, Building } from 'lucide-react';
import { SECTOR_VISUALS } from '@/lib/maps/infrastructure/sectorStyles';

interface InfrastructureAssetComparisonProps {
  comparisonData: any;
  onClose: () => void;
}

export const InfrastructureAssetComparison: React.FC<InfrastructureAssetComparisonProps> = ({
  comparisonData,
  onClose,
}) => {
  if (!comparisonData || !comparisonData.assets) return null;

  const assets = comparisonData.assets;
  const discrepancies = comparisonData.basis_discrepancies || [];

  return (
    <div className="absolute inset-x-8 top-16 bottom-8 bg-zinc-950/98 border border-zinc-800 rounded-2xl shadow-2xl backdrop-blur-2xl flex flex-col z-40 overflow-hidden text-xs">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ArrowLeftRight className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold text-zinc-100">
            Side-by-Side Infrastructure Asset Comparison
          </h2>
          <span className="text-[10px] text-zinc-400 font-mono px-2 py-0.5 bg-zinc-800/80 rounded">
            {assets.length} Assets
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-zinc-400 hover:text-zinc-100 bg-zinc-800/40 hover:bg-zinc-800 rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Discrepancy Alert Banner (Fixture F) */}
      {discrepancies.length > 0 && (
        <div className="p-3 bg-amber-950/30 border-b border-amber-800/40 flex items-start gap-3 text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-[11px]">Capacity Reporting Basis Discrepancy</div>
            <div className="text-[10px] text-amber-200/80">
              {discrepancies[0].warning} Differing bases detected:{' '}
              <span className="font-mono">{discrepancies[0].differing_bases.join(', ')}</span>.
            </div>
          </div>
        </div>
      )}

      {/* Side-by-side columns */}
      <div className="flex-1 overflow-x-auto p-4 flex gap-4">
        {assets.map((a: any) => {
          const meta = SECTOR_VISUALS[a.sector as keyof typeof SECTOR_VISUALS] || {
            label: a.sector,
            color: '#38bdf8',
          };

          return (
            <div
              key={a.asset_id}
              className="w-80 shrink-0 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col space-y-3.5"
            >
              <div>
                <span
                  style={{ color: meta.color }}
                  className="text-[10px] uppercase tracking-wider font-semibold"
                >
                  {meta.label}
                </span>
                <h3 className="font-semibold text-sm text-zinc-100 truncate mt-0.5" title={a.name}>
                  {a.name}
                </h3>
                <div className="text-[10px] text-zinc-500 font-mono mt-0.5">
                  {a.asset_id} • {a.country}
                </div>
              </div>

              {/* Status and Precision */}
              <div className="space-y-1 text-[11px] pt-1 border-t border-zinc-800/80">
                <div className="flex justify-between">
                  <span className="text-zinc-500">Status:</span>
                  <span className="text-zinc-300 capitalize">{a.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Precision:</span>
                  <span className="text-zinc-300 capitalize">{a.precision}</span>
                </div>
              </div>

              {/* Capacities */}
              <div className="space-y-1.5 pt-2 border-t border-zinc-800/80">
                <span className="text-[10px] uppercase font-mono text-zinc-400 font-semibold">
                  Reported Output & Capacity
                </span>
                <div className="space-y-1.5">
                  {a.capacities.map((c: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 bg-zinc-950/60 border border-zinc-800/80 rounded flex justify-between items-center"
                    >
                      <span className="font-mono text-zinc-200">
                        {c.value !== null && c.value !== undefined
                          ? `${Number(c.value).toLocaleString()} ${c.unit || ''}`
                          : 'Not available'}
                      </span>
                      {c.basis && (
                        <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 bg-zinc-800 rounded text-zinc-400">
                          {c.basis}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Entity Links (Fixture G) */}
              {a.entity_links && a.entity_links.length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-zinc-800/80">
                  <span className="text-[10px] uppercase font-mono text-zinc-400 font-semibold flex items-center gap-1">
                    <Building className="w-3 h-3" />
                    Entity Roles
                  </span>
                  <div className="space-y-1">
                    {a.entity_links.map((link: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-1.5 bg-zinc-950/40 border border-zinc-800/60 rounded flex justify-between text-[10px]"
                      >
                        <span className="text-zinc-300 truncate max-w-[140px]">{link.entity_name}</span>
                        <span className="text-cyan-400 font-semibold uppercase">{link.role}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
