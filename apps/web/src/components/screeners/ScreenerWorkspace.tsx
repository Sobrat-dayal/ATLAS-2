"use client";

import React from "react";
import { useScreener } from "@/hooks/screeners/useScreener";
import { ScreenerHeader } from "./ScreenerHeader";
import { ScreenerToolbar } from "./ScreenerToolbar";
import { VisualScreenerBuilder } from "./visual-builder/VisualScreenerBuilder";
import { ScreenerActiveFilters } from "./ScreenerActiveFilters";
import { ScreenerResultsTable } from "./ScreenerResultsTable";
import { ScreenerPagination } from "./ScreenerPagination";
import { ScreenerColumnManager } from "./ScreenerColumnManager";
import { ScreenerSourceInspector } from "./ScreenerSourceInspector";
import { ScreenerCoveragePanel } from "./ScreenerCoveragePanel";
import { ScreenerEmptyState } from "./ScreenerEmptyState";
import { ScreenerErrorState } from "./ScreenerErrorState";

export function ScreenerWorkspace() {
  const {
    universes,
    filtersRegistry,
    columnsRegistry,
    exchanges,
    geographies,
    industries,
    coverage,
    selectedUniverseId,
    selectedExchanges,
    selectedCountries,
    selectedSectors,
    activeFilters,
    sortCriteria,
    visibleColumnIds,
    page,
    pageSize,
    results,
    loading,
    error,
    selectedRow,
    isCoverageOpen,
    isColumnManagerOpen,
    setUniverse,
    toggleExchange,
    toggleCountry,
    toggleSector,
    addFilter,
    setFilters,
    removeFilter,
    clearFilters,
    setSorting,
    toggleColumn,
    resetColumns,
    goToPage,
    changePageSize,
    selectRow,
    setIsCoverageOpen,
    setIsColumnManagerOpen,
    runScreener,
  } = useScreener();

  const totalMatching = results?.total_matching_count ?? 0;
  const totalEvaluated = results?.source_coverage?.total_evaluated ?? (coverage?.total_instruments ?? 0);
  const rows = results?.rows ?? [];
  const totalPages = results?.total_pages ?? 1;

  // Filter columns to display based on visibleColumnIds
  const activeColumns = columnsRegistry.filter((c) =>
    visibleColumnIds.includes(c.column_id)
  );

  return (
    <div className="flex h-full min-h-screen w-full flex-col bg-background text-foreground">
      {/* 1. Header with Title, Universe selector, and Primary Actions */}
      <ScreenerHeader
        universes={universes}
        selectedUniverseId={selectedUniverseId}
        onSelectUniverse={setUniverse}
        matchingCount={totalMatching}
        totalEvaluated={totalEvaluated}
        loading={loading}
        onRunScreener={() => runScreener()}
        onReset={clearFilters}
        onToggleColumns={() => setIsColumnManagerOpen(true)}
        onToggleCoverage={() => setIsCoverageOpen(!isCoverageOpen)}
        isCoverageOpen={isCoverageOpen}
      />

      {/* 2. Collapsible Data Coverage & Provenance Audit Panel */}
      <ScreenerCoveragePanel
        isOpen={isCoverageOpen}
        onClose={() => setIsCoverageOpen(false)}
        coverage={coverage}
      />

      {/* 3. Universe Scope Toolbar (Exchanges, Countries, Sectors) */}
      <ScreenerToolbar
        exchanges={exchanges}
        geographies={geographies}
        industries={industries}
        selectedExchanges={selectedExchanges}
        selectedCountries={selectedCountries}
        selectedSectors={selectedSectors}
        onToggleExchange={toggleExchange}
        onToggleCountry={toggleCountry}
        onToggleSector={toggleSector}
      />

      {/* 4. Institutional Visual Screener Filter Builder (Stage 95) */}
      <VisualScreenerBuilder
        filtersRegistry={filtersRegistry}
        universes={universes}
        selectedUniverseId={selectedUniverseId}
        exchanges={exchanges}
        geographies={geographies}
        industries={industries}
        appliedFilters={activeFilters}
        onApplyFilters={setFilters}
        isLoading={loading}
      />


      {/* 5. Active Filter Badges with Quick Removal */}
      <ScreenerActiveFilters
        activeFilters={activeFilters}
        filtersRegistry={filtersRegistry}
        selectedExchanges={selectedExchanges}
        selectedCountries={selectedCountries}
        selectedSectors={selectedSectors}
        onRemoveFilter={removeFilter}
        onClearFilters={clearFilters}
      />

      {/* 6. Main Data Grid / Empty / Error States */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {error ? (
          <ScreenerErrorState error={error} onRetry={() => runScreener()} />
        ) : !loading && rows.length === 0 ? (
          <ScreenerEmptyState onReset={clearFilters} />
        ) : (
          <ScreenerResultsTable
            rows={rows}
            columns={activeColumns.length > 0 ? activeColumns : columnsRegistry.filter((c) => c.default_visible)}
            sortCriteria={sortCriteria}
            onToggleSort={setSorting}
            selectedRow={selectedRow}
            onSelectRow={selectRow}
            loading={loading}
          />
        )}
      </div>

      {/* 7. Pagination Controls */}
      <ScreenerPagination
        page={page}
        pageSize={pageSize}
        totalPages={totalPages}
        totalMatchingCount={totalMatching}
        onPageChange={goToPage}
        onPageSizeChange={changePageSize}
      />

      {/* 8. Column Manager Modal */}
      <ScreenerColumnManager
        isOpen={isColumnManagerOpen}
        onClose={() => setIsColumnManagerOpen(false)}
        columnsRegistry={columnsRegistry}
        visibleColumnIds={visibleColumnIds}
        onToggleColumn={toggleColumn}
        onResetColumns={resetColumns}
      />

      {/* 9. Source Provenance Inspector Drawer */}
      <ScreenerSourceInspector
        row={selectedRow}
        onClose={() => selectRow(null)}
      />
    </div>
  );
}
