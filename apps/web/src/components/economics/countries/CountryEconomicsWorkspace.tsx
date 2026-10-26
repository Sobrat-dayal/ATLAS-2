"use client";

import React from "react";
import {
  Globe,
  TrendingUp,
  Percent,
  Users,
  Factory,
  Landmark,
  Scale,
  ArrowLeftRight,
  Building2,
  Database,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import { useCountryEconomics } from "@/hooks/economics/useCountryEconomics";
import { CountryCategoryTab } from "@/lib/economics/countries";
import { CountrySelector } from "./CountrySelector";
import { CountryEconomicsOverview } from "./CountryEconomicsOverview";
import { CountryGDPPanel } from "./CountryGDPPanel";
import { CountryInflationPanel } from "./CountryInflationPanel";
import { CountryLaborPanel } from "./CountryLaborPanel";
import { CountryIndustryPanel } from "./CountryIndustryPanel";
import { CountryMonetaryPanel } from "./CountryMonetaryPanel";
import { CountryFiscalPanel } from "./CountryFiscalPanel";
import { CountryExternalPanel } from "./CountryExternalPanel";
import { CountryDemographicsPanel } from "./CountryDemographicsPanel";
import { CountryDataCoverage } from "./CountryDataCoverage";

interface CountryEconomicsWorkspaceProps {
  initialCountryId?: string;
}

export function CountryEconomicsWorkspace({
  initialCountryId = "US",
}: CountryEconomicsWorkspaceProps) {
  const {
    countries,
    selectedCountryId,
    setSelectedCountryId,
    activeCategory,
    setActiveCategory,
    overview,
    profile,
    gdp,
    production,
    inflation,
    labor,
    industry,
    monetary,
    fiscal,
    external,
    demographics,
    coverage,
    isLoading,
    error,
    refresh,
  } = useCountryEconomics(initialCountryId);

  const categories: { id: CountryCategoryTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <Globe className="w-3.5 h-3.5 text-atlas-accent" /> },
    { id: "gdp", label: "GDP & Growth", icon: <TrendingUp className="w-3.5 h-3.5 text-blue-400" /> },
    { id: "inflation", label: "Inflation & Prices", icon: <Percent className="w-3.5 h-3.5 text-rose-400" /> },
    { id: "labor", label: "Employment & Labor", icon: <Users className="w-3.5 h-3.5 text-amber-400" /> },
    { id: "industry", label: "Industry & Retail", icon: <Factory className="w-3.5 h-3.5 text-purple-400" /> },
    { id: "monetary", label: "Monetary & Credit", icon: <Landmark className="w-3.5 h-3.5 text-emerald-400" /> },
    { id: "fiscal", label: "Government & Fiscal", icon: <Scale className="w-3.5 h-3.5 text-indigo-400" /> },
    { id: "external", label: "Trade & External", icon: <ArrowLeftRight className="w-3.5 h-3.5 text-cyan-400" /> },
    { id: "demographics", label: "Demographics", icon: <Building2 className="w-3.5 h-3.5 text-teal-400" /> },
    { id: "historical", label: "Coverage Matrix", icon: <Database className="w-3.5 h-3.5 text-atlas-text-muted" /> },
  ];

  return (
    <div className="space-y-4">
      {/* Workspace Sub-Header: Country Selection & Category Navigation */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          {/* Country Selector + Quick G6 Pills */}
          <div className="flex flex-wrap items-center gap-2">
            <CountrySelector
              countries={countries}
              selectedCountryId={selectedCountryId}
              onSelectCountry={setSelectedCountryId}
            />

            <div className="h-5 w-px bg-atlas-border-subtle hidden sm:block mx-1" />

            {/* Quick Switcher for Core G6 */}
            <div className="flex items-center gap-1">
              {["US", "EA", "CN", "IN", "JP", "GB"].map((iso) => {
                const isActive =
                  selectedCountryId.toLowerCase() === iso.toLowerCase() ||
                  profile?.iso_code.toLowerCase() === iso.toLowerCase();
                return (
                  <button
                    key={iso}
                    onClick={() => setSelectedCountryId(iso)}
                    className={`font-mono text-xs px-2.5 py-1 rounded transition-colors ${
                      isActive
                        ? "bg-atlas-accent text-white font-bold shadow-xs"
                        : "bg-atlas-background hover:bg-atlas-surface-elevated text-atlas-text-secondary border border-atlas-border-subtle"
                    }`}
                  >
                    {iso}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Refresh Action */}
          <div className="flex items-center gap-2 self-end lg:self-auto">
            <button
              onClick={() => refresh()}
              disabled={isLoading}
              className="p-1.5 bg-atlas-background hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary transition-colors flex items-center gap-1.5 text-xs font-mono"
              title="Refresh Sovereign Economic Data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>

        {/* Category Navigation Tabs */}
        <div className="mt-3 pt-3 border-t border-atlas-border-subtle overflow-x-auto">
          <nav className="flex items-center gap-1 min-w-max text-xs">
            {categories.map((cat) => {
              const isActive = activeCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
                    isActive
                      ? "bg-atlas-background text-atlas-text-primary border border-atlas-border-strong shadow-xs"
                      : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-background/50"
                  }`}
                >
                  {cat.icon}
                  <span>{cat.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center gap-2 text-xs text-rose-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Category Workspace Content */}
      {activeCategory === "overview" && (
        <CountryEconomicsOverview
          overview={overview}
          profile={profile}
          onNavigateCategory={(cat) => setActiveCategory(cat as CountryCategoryTab)}
        />
      )}

      {activeCategory === "gdp" && (
        <CountryGDPPanel gdp={gdp} production={production} />
      )}

      {activeCategory === "inflation" && (
        <CountryInflationPanel inflation={inflation} />
      )}

      {activeCategory === "labor" && (
        <CountryLaborPanel labor={labor} />
      )}

      {activeCategory === "industry" && (
        <CountryIndustryPanel industry={industry} />
      )}

      {activeCategory === "monetary" && (
        <CountryMonetaryPanel monetary={monetary} />
      )}

      {activeCategory === "fiscal" && (
        <CountryFiscalPanel fiscal={fiscal} />
      )}

      {activeCategory === "external" && (
        <CountryExternalPanel external={external} />
      )}

      {activeCategory === "demographics" && (
        <CountryDemographicsPanel demographics={demographics} />
      )}

      {activeCategory === "historical" && (
        <CountryDataCoverage coverage={coverage} />
      )}
    </div>
  );
}
