'use client';

import React from 'react';
import { InfrastructureFiltersState } from '@/hooks/maps/infrastructure/useInfrastructureFilters';
import { Search, RotateCcw, Calendar } from 'lucide-react';
import { InfrastructureStatus } from '@/lib/maps/infrastructure/types';

interface InfrastructureFiltersProps {
  filters: InfrastructureFiltersState;
  onSearchChange: (q: string) => void;
  onCountryChange: (c: string) => void;
  onStatusChange: (s: InfrastructureStatus | 'all') => void;
  onHistoricalDateChange: (d: string) => void;
  onReset: () => void;
}

export const InfrastructureFilters: React.FC<InfrastructureFiltersProps> = ({
  filters,
  onSearchChange,
  onCountryChange,
  onStatusChange,
  onHistoricalDateChange,
  onReset,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-2 p-2.5 bg-zinc-900/90 border border-zinc-800 rounded-lg text-xs shadow-xl backdrop-blur-md">
      {/* Search Input */}
      <div className="relative flex-1 min-w-[160px]">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
        <input
          type="text"
          value={filters.searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search infrastructure assets or terminals..."
          className="w-full pl-8 pr-3 py-1.5 bg-zinc-950/70 border border-zinc-800 rounded text-zinc-200 placeholder-zinc-500 text-xs focus:outline-none focus:border-cyan-500/50"
        />
      </div>

      {/* Country Filter */}
      <input
        type="text"
        value={filters.countryFilter}
        onChange={(e) => onCountryChange(e.target.value.toUpperCase())}
        placeholder="ISO (e.g. US, NL)"
        maxLength={3}
        className="w-24 px-2 py-1.5 bg-zinc-950/70 border border-zinc-800 rounded text-zinc-200 placeholder-zinc-500 text-xs text-center uppercase focus:outline-none focus:border-cyan-500/50 font-mono"
      />

      {/* Operational Status Dropdown */}
      <select
        value={filters.selectedStatus}
        onChange={(e) => onStatusChange(e.target.value as any)}
        className="px-2.5 py-1.5 bg-zinc-950/70 border border-zinc-800 rounded text-zinc-300 text-xs focus:outline-none focus:border-cyan-500/50"
      >
        <option value="all">All Statuses</option>
        <option value="operational">Operational</option>
        <option value="under_construction">Under Construction</option>
        <option value="proposed">Proposed</option>
        <option value="decommissioned">Decommissioned</option>
        <option value="suspended">Suspended</option>
        <option value="retired">Retired</option>
      </select>

      {/* Historical Date Input */}
      <div className="flex items-center gap-1.5 px-2 py-1 bg-zinc-950/70 border border-zinc-800 rounded">
        <Calendar className="w-3.5 h-3.5 text-zinc-500" />
        <input
          type="date"
          value={filters.historicalAsOf}
          onChange={(e) => onHistoricalDateChange(e.target.value)}
          className="bg-transparent text-zinc-300 text-xs focus:outline-none font-mono"
          title="Point-in-Time Historical State (YYYY-MM-DD)"
        />
      </div>

      {/* Reset */}
      <button
        onClick={onReset}
        title="Reset All Filters"
        className="p-1.5 text-zinc-400 hover:text-zinc-200 bg-zinc-800/50 hover:bg-zinc-800 rounded transition-colors"
      >
        <RotateCcw className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

