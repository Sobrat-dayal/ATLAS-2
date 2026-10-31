"use client";

import React from "react";
import { Filter, Calendar, Globe, Layers, CheckSquare, Square, RotateCcw } from "lucide-react";
import { CorporateFacilityStatus, CorporateFacilityType } from "@/lib/maps/corporate/types";
import { FACILITY_STATUS_STYLES, FACILITY_TYPE_STYLES } from "@/lib/maps/corporate/facilityStyles";

interface CompanyGeoFiltersProps {
  includeSubsidiaries: boolean;
  onToggleSubsidiaries: (val: boolean) => void;
  selectedTypes: CorporateFacilityType[];
  onToggleType: (type: CorporateFacilityType) => void;
  selectedStatuses: CorporateFacilityStatus[];
  onToggleStatus: (status: CorporateFacilityStatus) => void;
  selectedCountry: string | null;
  onSelectCountry: (code: string | null) => void;
  availableCountries?: string[];
  asOfDate: string | null;
  onSetAsOfDate: (date: string | null) => void;
  onResetFilters: () => void;
  className?: string;
}

export function CompanyGeoFilters({
  includeSubsidiaries,
  onToggleSubsidiaries,
  selectedTypes,
  onToggleType,
  selectedStatuses,
  onToggleStatus,
  selectedCountry,
  onSelectCountry,
  availableCountries = [],
  asOfDate,
  onSetAsOfDate,
  onResetFilters,
  className = "",
}: CompanyGeoFiltersProps) {
  const commonTypes: CorporateFacilityType[] = [
    "CORPORATE_HEADQUARTERS",
    "MANUFACTURING_FACILITY",
    "ASSEMBLY_FACILITY",
    "RESEARCH_AND_DEVELOPMENT",
    "CORPORATE_OFFICE",
    "REGIONAL_HEADQUARTERS",
    "DISTRIBUTION_CENTER",
    "WAREHOUSE",
    "REGISTERED_OFFICE",
  ];

  return (
    <div className={`space-y-3 p-3 bg-zinc-950 border border-zinc-800 rounded text-xs ${className}`}>
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-1.5 font-bold text-zinc-300 uppercase tracking-wider text-[11px]">
          <Filter className="w-3.5 h-3.5 text-sky-400" />
          <span>Footprint Filters</span>
        </div>
        <button
          type="button"
          onClick={onResetFilters}
          className="flex items-center gap-1 text-[10px] text-zinc-400 hover:text-zinc-200 transition-colors"
          title="Reset all filters"
        >
          <RotateCcw className="w-2.5 h-2.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* 1. Subsidiary Scope Toggle */}
      <div className="p-2 bg-zinc-900/60 rounded border border-zinc-800/60 flex items-center justify-between">
        <div>
          <div className="font-semibold text-zinc-200 text-xs">Include Subsidiaries</div>
          <div className="text-[10px] text-zinc-400">Include verified group subsidiaries</div>
        </div>
        <button
          type="button"
          onClick={() => onToggleSubsidiaries(!includeSubsidiaries)}
          className={`relative inline-flex h-4 w-8 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
            includeSubsidiaries ? "bg-sky-500" : "bg-zinc-700"
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-3 w-3 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              includeSubsidiaries ? "translate-x-4" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* 2. Country Filter */}
      {availableCountries.length > 0 && (
        <div>
          <div className="flex items-center gap-1 text-[11px] font-semibold text-zinc-400 mb-1">
            <Globe className="w-3 h-3" />
            <span>Country</span>
          </div>
          <select
            value={selectedCountry || ""}
            onChange={(e) => onSelectCountry(e.target.value || null)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-xs text-zinc-200 focus:outline-none focus:border-sky-500/50"
          >
            <option value="">All Represented Countries ({availableCountries.length})</option>
            {availableCountries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* 3. Historical As-Of Date */}
      <div>
        <div className="flex items-center gap-1 text-[11px] font-semibold text-zinc-400 mb-1">
          <Calendar className="w-3 h-3 text-sky-400" />
          <span>Historical As-Of Date</span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={asOfDate ? asOfDate.split("T")[0] : ""}
            onChange={(e) => onSetAsOfDate(e.target.value ? `${e.target.value}T00:00:00Z` : null)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-xs text-zinc-200 focus:outline-none focus:border-sky-500/50"
          />
          {asOfDate && (
            <button
              type="button"
              onClick={() => onSetAsOfDate(null)}
              className="text-[10px] text-zinc-400 hover:text-zinc-200 px-1 py-0.5 bg-zinc-800 rounded"
            >
              Latest
            </button>
          )}
        </div>
      </div>

      {/* 4. Facility Types */}
      <div>
        <div className="flex items-center gap-1 text-[11px] font-semibold text-zinc-400 mb-1.5">
          <Layers className="w-3 h-3" />
          <span>Facility Types</span>
        </div>
        <div className="space-y-1 max-h-40 overflow-y-auto pr-1">
          {commonTypes.map((type) => {
            const style = FACILITY_TYPE_STYLES[type];
            const isChecked = selectedTypes.includes(type);
            return (
              <button
                key={type}
                type="button"
                onClick={() => onToggleType(type)}
                className="w-full flex items-center justify-between px-1.5 py-1 rounded hover:bg-zinc-900 text-left transition-colors"
              >
                <div className="flex items-center gap-1.5">
                  {isChecked ? (
                    <CheckSquare className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                  ) : (
                    <Square className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                  )}
                  <span className={`text-[11px] ${isChecked ? "text-zinc-100 font-medium" : "text-zinc-400"}`}>
                    {style?.label || type}
                  </span>
                </div>
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: style?.color || "#71717a" }}
                />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

