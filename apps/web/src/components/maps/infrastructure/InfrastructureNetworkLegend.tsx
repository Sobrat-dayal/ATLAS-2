'use client';

import React from 'react';
import { SECTOR_VISUALS } from '@/lib/maps/infrastructure/sectorStyles';
import { InfrastructureSector } from '@/lib/maps/infrastructure/types';

export const InfrastructureNetworkLegend: React.FC = () => {
  const sectors = Object.keys(SECTOR_VISUALS) as InfrastructureSector[];

  return (
    <div className="p-2.5 bg-zinc-950/90 border border-zinc-800 rounded-lg text-[10px] shadow-xl backdrop-blur-md space-y-2 w-48">
      <div className="font-semibold text-zinc-300 uppercase tracking-wider font-mono border-b border-zinc-800/80 pb-1">
        Infrastructure Legend
      </div>

      <div className="space-y-1">
        {sectors.map((sec) => {
          const meta = SECTOR_VISUALS[sec];
          return (
            <div key={sec} className="flex items-center gap-2">
              <span
                style={{ backgroundColor: meta.color }}
                className="w-2.5 h-2.5 rounded-full shrink-0 shadow-sm"
              />
              <span className="text-zinc-400 truncate">{meta.label}</span>
            </div>
          );
        })}
      </div>

      <div className="pt-1.5 border-t border-zinc-800/80 space-y-1 text-zinc-400">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-purple-400 shrink-0" />
          <span>High-Voltage Line</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-orange-400 shrink-0" />
          <span>Pipeline Corridor</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 border-b border-dashed border-zinc-400 shrink-0" />
          <span>Approximate Route</span>
        </div>
      </div>
    </div>
  );
};
