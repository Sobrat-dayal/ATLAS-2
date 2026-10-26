"use client";

import React, { useMemo } from "react";
import {
  Search,
  Filter,
  BarChart3,
  Calendar,
  Layers,
  ShieldCheck,
  ChevronRight,
  Database,
  Info,
} from "lucide-react";
import {
  EconomicGeographyDTO,
  EconomicIndicatorDTO,
  EconomicSeriesDTO,
  IndicatorCategory,
} from "@/lib/economics";

interface EconomicIndicatorExplorerProps {
  indicators: EconomicIndicatorDTO[];
  seriesList: EconomicSeriesDTO[];
  geographies: EconomicGeographyDTO[];
  selectedCategory: IndicatorCategory | null;
  onSelectCategory: (cat: IndicatorCategory | null) => void;
  selectedGeographyId: string | null;
  onSelectGeographyId: (geoId: string | null) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSelectSeries: (seriesId: string) => void;
}

const CATEGORIES: { label: string; value: IndicatorCategory | null }[] = [
  { label: "All Categories", value: null },
  { label: "National Accounts", value: "NATIONAL_ACCOUNTS" },
  { label: "Inflation", value: "INFLATION" },
  { label: "Labor Market", value: "LABOR_MARKET" },
  { label: "Interest Rates", value: "INTEREST_RATES" },
  { label: "Monetary", value: "MONETARY" },
  { label: "Fiscal", value: "FISCAL" },
  { label: "External Sector", value: "EXTERNAL_SECTOR" },
  { label: "Industrial", value: "INDUSTRIAL_ACTIVITY" },
];

export function EconomicIndicatorExplorer({
  indicators,
  seriesList,
  geographies,
  selectedCategory,
  onSelectCategory,
  selectedGeographyId,
  onSelectGeographyId,
  searchQuery,
  onSearchChange,
  onSelectSeries,
}: EconomicIndicatorExplorerProps) {
  // Filter indicators and series
  const filteredSeries = useMemo(() => {
    return seriesList.filter((s) => {
      // Geography filter
      if (selectedGeographyId && s.geography_id !== selectedGeographyId) {
        return false;
      }
      // Indicator lookup
      const ind = indicators.find((i) => i.indicator_id === s.canonical_indicator_id);
      // Category filter
      if (selectedCategory && ind?.category !== selectedCategory) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = s.series_name.toLowerCase().includes(q);
        const matchesCode = s.source_series_code.toLowerCase().includes(q);
        const matchesProvider = s.source_provider_id.toLowerCase().includes(q);
        const matchesInd = ind?.display_name.toLowerCase().includes(q) || false;
        if (!matchesName && !matchesCode && !matchesProvider && !matchesInd) {
          return false;
        }
      }
      return true;
    });
  }, [seriesList, indicators, selectedGeographyId, selectedCategory, searchQuery]);

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4 mb-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary flex items-center gap-2">
            <Database className="w-4 h-4 text-atlas-accent" />
            Canonical Economic Indicator & Series Explorer
          </h3>
          <p className="text-xs text-atlas-text-muted mt-0.5">
            Discover authorized statistical time-series across G6 sovereign agencies and international bodies.
          </p>
        </div>

        {/* Search & Geography controls */}
        <div className="flex items-center gap-2">
          {/* Geography dropdown */}
          <select
            value={selectedGeographyId || ""}
            onChange={(e) => onSelectGeographyId(e.target.value ? e.target.value : null)}
            className="text-xs bg-atlas-background border border-atlas-border-subtle rounded px-2.5 py-1.5 text-atlas-text-primary focus:outline-none focus:border-atlas-accent"
          >
            <option value="">All Geographies (G6)</option>
            {geographies.map((g) => (
              <option key={g.geography_id} value={g.geography_id}>
                {g.iso_code} - {g.name}
              </option>
            ))}
          </select>

          {/* Search box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-atlas-text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by indicator, series code, agency..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="text-xs bg-atlas-background border border-atlas-border-subtle rounded pl-8 pr-3 py-1.5 text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:outline-none focus:border-atlas-accent w-48 sm:w-64"
            />
          </div>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-4 text-xs border-b border-atlas-border-subtle/50">
        <Filter className="w-3.5 h-3.5 text-atlas-text-muted shrink-0 mr-1" />
        {CATEGORIES.map((cat) => (
          <button
            key={cat.label}
            onClick={() => onSelectCategory(cat.value)}
            className={`px-2.5 py-1 rounded text-xs whitespace-nowrap transition-colors ${
              selectedCategory === cat.value
                ? "bg-atlas-accent text-white font-medium"
                : "bg-atlas-background/70 hover:bg-atlas-surface-hover text-atlas-text-secondary"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Series Grid / Table */}
      {filteredSeries.length === 0 ? (
        <div className="py-8 text-center text-xs text-atlas-text-muted flex flex-col items-center justify-center">
          <Info className="w-6 h-6 text-atlas-text-muted/40 mb-2" />
          <span>No economic series found matching the selected filters.</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredSeries.map((s) => {
            const geo = geographies.find((g) => g.geography_id === s.geography_id);
            const ind = indicators.find((i) => i.indicator_id === s.canonical_indicator_id);

            return (
              <div
                key={s.series_id}
                onClick={() => onSelectSeries(s.series_id)}
                className="p-3 bg-atlas-background/60 hover:bg-atlas-surface-hover border border-atlas-border-subtle hover:border-atlas-accent/50 rounded cursor-pointer transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between text-[10px] text-atlas-text-muted mb-1">
                    <span className="font-mono bg-atlas-border-subtle/60 text-atlas-text-primary px-1.5 py-0.5 rounded font-semibold">
                      {geo?.iso_code || "US"}
                    </span>
                    <span className="font-mono text-atlas-accent uppercase font-medium">
                      {s.frequency}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-atlas-text-primary group-hover:text-atlas-accent transition-colors line-clamp-1">
                    {s.series_name}
                  </h4>
                  <p className="text-[11px] text-atlas-text-muted line-clamp-2 mt-1">
                    {s.source_definition}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-atlas-border-subtle/40 flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                  <div className="flex items-center gap-1.5">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span>{s.source_provider_id}</span>
                  </div>
                  <div className="flex items-center gap-1 text-atlas-text-secondary group-hover:text-atlas-accent">
                    <span>{s.observation_count} Obs</span>
                    <ChevronRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
