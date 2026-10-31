"use client";

import React, { useState } from "react";
import { Building2, X, ChevronRight, ChevronLeft, MapPin } from "lucide-react";
import { CompanyGeoSelector } from "./CompanyGeoSelector";
import { CompanyGeoFilters } from "./CompanyGeoFilters";
import { CompanyGeoSummary } from "./CompanyGeoSummary";
import { CompanyGeoComparison } from "./CompanyGeoComparison";
import { FacilityPrecisionLegend } from "./FacilityPrecisionLegend";
import { FacilityInspector } from "./FacilityInspector";
import { useCompanyFootprint } from "@/hooks/maps/corporate/useCompanyFootprint";
import { CorporateFacility, MappedCompanySearchResult } from "@/lib/maps/corporate/types";

interface CorporateMapModeProps {
  initialCompanyId?: string | null;
  selectedFacility: CorporateFacility | null;
  onSelectFacility: (fac: CorporateFacility | null) => void;
  onFacilitiesLoaded?: (facilities: CorporateFacility[]) => void;
  className?: string;
}

export function CorporateMapMode({
  initialCompanyId,
  selectedFacility,
  onSelectFacility,
  onFacilitiesLoaded,
  className = "",
}: CorporateMapModeProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  const {
    companyId,
    setCompanyId,
    includeSubsidiaries,
    setIncludeSubsidiaries,
    selectedCountry,
    setSelectedCountry,
    selectedTypes,
    setSelectedTypes,
    selectedStatuses,
    setSelectedStatuses,
    asOfDate,
    setAsOfDate,
    footprint,
    facilities,
    rawFacilities,
    summary,
    loading,
    error,
    refresh,
  } = useCompanyFootprint({
    initialCompanyId: initialCompanyId || "cmp_apple",
    initialIncludeSubsidiaries: true,
  });

  // Notify parent of loaded facilities for Map rendering
  React.useEffect(() => {
    if (onFacilitiesLoaded) {
      onFacilitiesLoaded(facilities);
    }
  }, [facilities, onFacilitiesLoaded]);

  const availableCountries = React.useMemo(() => {
    if (!rawFacilities) return [];
    const set = new Set<string>();
    rawFacilities.forEach((f) => {
      if (f.country_code) set.add(f.country_code.toUpperCase());
    });
    return Array.from(set).sort();
  }, [rawFacilities]);

  const handleToggleType = (type: any) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleToggleStatus = (status: any) => {
    setSelectedStatuses((prev) =>
      prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]
    );
  };

  const handleResetFilters = () => {
    setSelectedTypes([]);
    setSelectedStatuses([]);
    setSelectedCountry(null);
    setAsOfDate(null);
    setIncludeSubsidiaries(true);
  };

  return (
    <div className={`relative flex h-full ${className}`}>
      {/* Left Corporate Intelligence Drawer */}
      {isSidebarOpen ? (
        <div className="w-80 h-full bg-zinc-950 border-r border-zinc-800 flex flex-col z-20 shadow-xl overflow-hidden">
          {/* Drawer Header */}
          <div className="p-3 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/40 shrink-0">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-sky-400" />
              <span className="font-bold text-zinc-100 text-xs uppercase tracking-wider">
                Corporate Geography
              </span>
            </div>
            <button
              type="button"
              onClick={() => setIsSidebarOpen(false)}
              className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200 transition-colors"
              title="Collapse Drawer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {/* 1. Company Search / Selector */}
            <CompanyGeoSelector
              selectedCompanyId={companyId}
              onSelectCompany={(comp: MappedCompanySearchResult) => {
                setCompanyId(comp.entity_id || comp.company_id);
                onSelectFacility(null);
              }}
            />

            {/* 2. Footprint Summary */}
            <CompanyGeoSummary
              summary={summary}
              onOpenCompare={() => setIsCompareOpen(true)}
            />

            {/* 3. Filters */}
            <CompanyGeoFilters
              includeSubsidiaries={includeSubsidiaries}
              onToggleSubsidiaries={setIncludeSubsidiaries}
              selectedTypes={selectedTypes}
              onToggleType={handleToggleType}
              selectedStatuses={selectedStatuses}
              onToggleStatus={handleToggleStatus}
              selectedCountry={selectedCountry}
              onSelectCountry={setSelectedCountry}
              availableCountries={availableCountries}
              asOfDate={asOfDate}
              onSetAsOfDate={setAsOfDate}
              onResetFilters={handleResetFilters}
            />

            {/* 4. Facilities Listing (Accessible textual alternative to map) */}
            <div className="space-y-1.5 pt-2 border-t border-zinc-800">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold flex items-center justify-between">
                <span>Facilities List ({facilities.length})</span>
              </div>
              <div className="space-y-1 max-h-52 overflow-y-auto pr-1">
                {facilities.map((fac) => {
                  const isSelected = selectedFacility?.facility_id === fac.facility_id;
                  return (
                    <button
                      key={fac.facility_id}
                      type="button"
                      onClick={() => onSelectFacility(fac)}
                      className={`w-full text-left p-2 rounded border transition-colors flex items-start justify-between text-xs ${
                        isSelected
                          ? "bg-sky-950/40 border-sky-800/60 text-sky-200"
                          : "bg-zinc-900/40 border-zinc-800/60 text-zinc-300 hover:bg-zinc-800/40"
                      }`}
                    >
                      <div>
                        <div className="font-semibold leading-tight">{fac.canonical_name}</div>
                        <div className="text-[10px] text-zinc-500 mt-0.5">
                          {fac.locality ? `${fac.locality}, ` : ""}
                          {fac.country_code}
                        </div>
                      </div>
                      <span className="text-[9px] font-mono px-1 py-0.5 bg-zinc-800 rounded text-zinc-400">
                        {fac.facility_type.replace("_FACILITY", "").replace("CORPORATE_", "")}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Collapsed Drawer Toggle Button */
        <button
          type="button"
          onClick={() => setIsSidebarOpen(true)}
          className="absolute top-4 left-4 z-20 p-2 bg-zinc-900/90 border border-zinc-800 hover:bg-zinc-800 text-zinc-200 rounded shadow-lg flex items-center gap-1.5 text-xs font-semibold"
          title="Open Corporate Geography Drawer"
        >
          <Building2 className="w-4 h-4 text-sky-400" />
          <span>Corporate Geo</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      )}

      {/* Floating Precision Legend */}
      <div className="absolute bottom-4 left-4 z-10 max-w-xs">
        <FacilityPrecisionLegend />
      </div>

      {/* Right Facility Inspector if a facility is selected */}
      {selectedFacility && (
        <div className="absolute top-0 right-0 bottom-0 w-84 z-20 shadow-2xl">
          <FacilityInspector
            facility={selectedFacility}
            onClose={() => onSelectFacility(null)}
          />
        </div>
      )}

      {/* Cross-Company Comparison Modal */}
      {isCompareOpen && companyId && (
        <CompanyGeoComparison
          initialCompanyAId={companyId}
          onClose={() => setIsCompareOpen(false)}
        />
      )}
    </div>
  );
}

