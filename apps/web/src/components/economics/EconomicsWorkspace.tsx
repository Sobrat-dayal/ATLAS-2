"use client";

import React from "react";
import {
  Globe,
  Database,
  TrendingUp,
  RefreshCw,
  Layers,
  ShieldCheck,
  AlertTriangle,
  Landmark,
} from "lucide-react";
import { EconomicsSubTab, useEconomics } from "@/hooks/economics/useEconomics";
import { GlobalMacroSnapshotCards } from "./GlobalMacroSnapshotCards";
import { MajorEconomiesTable } from "./MajorEconomiesTable";
import { EconomicIndicatorExplorer } from "./EconomicIndicatorExplorer";
import { EconomicSeriesChart } from "./EconomicSeriesChart";
import { EconomicObservationsTable } from "./EconomicObservationsTable";
import { EconomicSourceInspector } from "./EconomicSourceInspector";
import { EconomicCoveragePanel } from "./EconomicCoveragePanel";
import { CountryEconomicsWorkspace } from "./countries/CountryEconomicsWorkspace";

export function EconomicsWorkspace() {
  const {
    activeTab,
    setActiveTab,
    selectedCountryEconomicsId,
    navigateToCountry,
    overview,
    geographies,
    categories,
    coverage,
    indicators,
    seriesList,
    selectedGeographyId,
    setSelectedGeographyId,
    selectedCategoryId,
    setSelectedCategoryId,
    searchQuery,
    setSearchQuery,
    selectedSeriesId,
    selectedSeriesData,
    selectedVintages,
    activeTransformation,
    setActiveTransformation,
    activeDateRange,
    setActiveDateRange,
    isLoading,
    isSeriesLoading,
    error,
    selectSeries,
    refresh,
  } = useEconomics();

  const handleSelectSeriesFromAnywhere = (seriesId: string) => {
    selectSeries(seriesId);
  };

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background text-atlas-text-primary overflow-y-auto">
      {/* Top Navigation & Workspace Header */}
      <div className="border-b border-atlas-border-subtle bg-atlas-surface/80 backdrop-blur-xs px-4 py-3 sticky top-0 z-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-atlas-accent/15 text-atlas-accent">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-atlas-text-primary tracking-tight">
                  ATLAS Macroeconomic Intelligence
                </h1>
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  STAGE 90 COUNTRY ECONOMICS
                </span>
              </div>
              <p className="text-xs text-atlas-text-muted">
                Canonical National Accounts, Sovereign Country Intelligence & Historical Statistical Vintages
              </p>
            </div>
          </div>

          {/* Sub-tab switcher and refresh */}
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <nav className="flex items-center bg-atlas-background border border-atlas-border-subtle rounded p-0.5 text-xs">
              <button
                onClick={() => setActiveTab("overview")}
                className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
                  activeTab === "overview"
                    ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                <Globe className="w-3.5 h-3.5 text-atlas-accent" />
                <span>Overview</span>
              </button>
              <button
                onClick={() => setActiveTab("country")}
                className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
                  activeTab === "country"
                    ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                <Landmark className="w-3.5 h-3.5 text-indigo-400" />
                <span>Country Economics</span>
              </button>
              <button
                onClick={() => setActiveTab("explorer")}
                className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
                  activeTab === "explorer"
                    ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                <Database className="w-3.5 h-3.5 text-blue-400" />
                <span>Indicators</span>
              </button>
              <button
                onClick={() => setActiveTab("series")}
                className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
                  activeTab === "series"
                    ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                <span>Historical Series</span>
              </button>
            </nav>

            <button
              onClick={refresh}
              className="p-1.5 bg-atlas-background hover:bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
              title="Refresh Macroeconomic Data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Workspace Body */}
      <div className="p-4 sm:p-6 max-w-7xl mx-auto w-full">
        {/* Error Alert (if any) */}
        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded flex items-center gap-2 text-xs text-rose-400 mb-4">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Tab 1: Global Overview */}
        {activeTab === "overview" && (
          <div>
            <GlobalMacroSnapshotCards
              overview={overview}
              onSelectSeries={handleSelectSeriesFromAnywhere}
            />

            <MajorEconomiesTable
              economies={overview?.major_economies || []}
              onSelectSeries={handleSelectSeriesFromAnywhere}
              onNavigateCountry={navigateToCountry}
            />

            <EconomicCoveragePanel coverage={coverage} />
          </div>
        )}

        {/* Tab 2: Country Economics Intelligence (Stage 90) */}
        {activeTab === "country" && (
          <div>
            <CountryEconomicsWorkspace initialCountryId={selectedCountryEconomicsId} />
          </div>
        )}

        {/* Tab 3: Economic Indicator & Series Explorer */}
        {activeTab === "explorer" && (
          <div>
            <EconomicIndicatorExplorer
              indicators={indicators}
              seriesList={seriesList}
              geographies={geographies}
              selectedCategory={selectedCategoryId}
              onSelectCategory={setSelectedCategoryId}
              selectedGeographyId={selectedGeographyId}
              onSelectGeographyId={setSelectedGeographyId}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSelectSeries={handleSelectSeriesFromAnywhere}
            />

            <EconomicCoveragePanel coverage={coverage} />
          </div>
        )}

        {/* Tab 3: Historical Economic Series */}
        {activeTab === "series" && (
          <div>
            <EconomicSeriesChart
              seriesData={selectedSeriesData}
              isLoading={isSeriesLoading}
              activeDateRange={activeDateRange}
              onSelectDateRange={setActiveDateRange}
              activeTransformation={activeTransformation}
              onSelectTransformation={setActiveTransformation}
            />

            <EconomicObservationsTable seriesData={selectedSeriesData} />

            <EconomicSourceInspector
              seriesData={selectedSeriesData}
              vintages={selectedVintages}
            />
          </div>
        )}
      </div>
    </div>
  );
}
