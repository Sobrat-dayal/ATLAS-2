'use client';

import React from 'react';
import { InfrastructureSector } from '@/lib/maps/infrastructure/types';
import { SECTOR_VISUALS } from '@/lib/maps/infrastructure/sectorStyles';
import {
  Anchor,
  Plane,
  Zap,
  Activity,
  Flame,
  Layers,
  Server,
  Navigation,
  Box,
  Check,
} from 'lucide-react';

interface InfrastructureSectorPanelProps {
  selectedSectors: Set<InfrastructureSector>;
  onToggleSector: (sector: InfrastructureSector) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
  sectorCounts?: Record<string, number>;
}

const ICONS: Record<string, React.ElementType> = {
  Anchor,
  Plane,
  Zap,
  Activity,
  Flame,
  Layers,
  Server,
  Navigation,
  Box,
};

export const InfrastructureSectorPanel: React.FC<InfrastructureSectorPanelProps> = ({
  selectedSectors,
  onToggleSector,
  onSelectAll,
  onClearAll,
  sectorCounts = {},
}) => {
  const allSectors = Object.keys(SECTOR_VISUALS) as InfrastructureSector[];

  return (
    <div className="flex flex-col gap-2 p-3 bg-zinc-900/90 border border-zinc-800 rounded-lg text-xs shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-1 border-b border-zinc-800/80">
        <span className="font-semibold text-zinc-200 tracking-wide uppercase text-[10px]">
          Physical Sectors
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={onSelectAll}
            className="text-[10px] text-zinc-400 hover:text-zinc-100 transition-colors"
          >
            All
          </button>
          <span className="text-zinc-600">|</span>
          <button
            onClick={onClearAll}
            className="text-[10px] text-zinc-400 hover:text-zinc-100 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-1.5 max-h-[220px] overflow-y-auto pr-1">
        {allSectors.map((sec) => {
          const meta = SECTOR_VISUALS[sec];
          const isSelected = selectedSectors.size === 0 || selectedSectors.has(sec);
          const IconComponent = ICONS[meta.iconName] || Layers;
          const count = sectorCounts[sec] ?? 0;

          return (
            <button
              key={sec}
              onClick={() => onToggleSector(sec)}
              style={{
                borderColor: isSelected ? meta.borderColor : 'rgba(39, 39, 42, 0.6)',
                backgroundColor: isSelected ? meta.bgColor : 'rgba(24, 24, 27, 0.4)',
              }}
              className="flex items-center justify-between px-2.5 py-1.5 rounded border text-left transition-all hover:brightness-110 group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <span style={{ color: meta.color }} className="shrink-0">
                  <IconComponent className="w-3.5 h-3.5" />
                </span>
                <span
                  className={`truncate font-medium text-[11px] ${
                    isSelected ? 'text-zinc-200' : 'text-zinc-500'
                  }`}
                >
                  {meta.label}
                </span>
              </div>
              <div className="flex items-center gap-1.5 shrink-0 ml-1">
                {count > 0 && (
                  <span className="text-[10px] text-zinc-400 font-mono">
                    {count}
                  </span>
                )}
                {isSelected && (
                  <Check style={{ color: meta.color }} className="w-3 h-3" />
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

