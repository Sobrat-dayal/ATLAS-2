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
import { SavedScreensLibraryModal } from "./saved/SavedScreensLibraryModal";
import { SaveScreenDialog } from "./saved/SaveScreenDialog";
import { AdvancedSortModal } from "./sorting/AdvancedSortModal";
import { RankingConfigModal } from "./ranking/RankingConfigModal";
import { ExportDialog } from "./exports/ExportDialog";

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
    rankingSpec,
    currentSavedScreen,
    isDirtyFromSaved,
    isSavedScreensOpen,
    isSaveDialogOpen,
    isSaveAs,
    isRankingModalOpen,
    isExportDialogOpen,
    isAdvancedSortOpen,
    setUniverse,
    toggleExchange,
    toggleCountry,
    toggleSector,
    addFilter,
    setFilters,
    removeFilter,
    clearFilters,
    setSorting,
    setMultiSort,
    applyRanking,
    loadSavedScreen,
    clearSavedScreen,
    onSavedScreenSaved,
    toggleColumn,
    resetColumns,
    goToPage,
    changePageSize,
    selectRow,
    setIsCoverageOpen,
    setIsColumnManagerOpen,
    setIsSavedScreensOpen,
    setIsSaveDialogOpen,
    setIsSaveAs,
    setIsRankingModalOpen,
    setIsExportDialogOpen,
    setIsAdvancedSortOpen,
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
        currentSavedScreen={currentSavedScreen}
        isDirtyFromSaved={isDirtyFromSaved}
        onOpenSavedScreens={() => setIsSavedScreensOpen(true)}
        onOpenSaveDialog={() => {
          setIsSaveAs(false);
          setIsSaveDialogOpen(true);
        }}
        onOpenAdvancedSort={() => setIsAdvancedSortOpen(true)}
        sortCount={sortCriteria.length}
        onOpenRanking={() => setIsRankingModalOpen(true)}
        isRankingActive={rankingSpec !== null}
        onOpenExport={() => setIsExportDialogOpen(true)}
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

      {/* 10. Stage 97: Saved Screens Library Modal */}
      <SavedScreensLibraryModal
        isOpen={isSavedScreensOpen}
        onClose={() => setIsSavedScreensOpen(false)}
        onLoadScreen={loadSavedScreen}
        onOpenSaveDialog={() => {
          setIsSavedScreensOpen(false);
          setIsSaveAs(false);
          setIsSaveDialogOpen(true);
        }}
        currentScreenId={currentSavedScreen?.saved_screen_id}
      />

      {/* 11. Stage 97: Save Screen Dialog */}
      <SaveScreenDialog
        isOpen={isSaveDialogOpen}
        onClose={() => setIsSaveDialogOpen(false)}
        isSaveAs={isSaveAs}
        currentSavedScreen={currentSavedScreen}
        selectedUniverseId={selectedUniverseId}
        selectedExchanges={selectedExchanges}
        selectedCountries={selectedCountries}
        selectedSectors={selectedSectors}
        activeFilters={activeFilters}
        sortCriteria={sortCriteria}
        rankingSpec={rankingSpec}
        visibleColumnIds={visibleColumnIds}
        onSaved={onSavedScreenSaved}
      />

      {/* 12. Stage 97: Advanced Multi-Column Sort Modal */}
      <AdvancedSortModal
        isOpen={isAdvancedSortOpen}
        onClose={() => setIsAdvancedSortOpen(false)}
        sortCriteria={sortCriteria}
        columnsRegistry={columnsRegistry}
        onApplySort={setMultiSort}
      />

      {/* 13. Stage 97: Quantitative Ranking Configuration Modal */}
      <RankingConfigModal
        isOpen={isRankingModalOpen}
        onClose={() => setIsRankingModalOpen(false)}
        rankingSpec={rankingSpec}
        columnsRegistry={columnsRegistry}
        onApplyRanking={applyRanking}
      />

      {/* 14. Stage 97: Export Dialog */}
      <ExportDialog
        isOpen={isExportDialogOpen}
        onClose={() => setIsExportDialogOpen(false)}
        selectedUniverseId={selectedUniverseId}
        selectedExchanges={selectedExchanges}
        selectedCountries={selectedCountries}
        selectedSectors={selectedSectors}
        activeFilters={activeFilters}
        sortCriteria={sortCriteria}
        rankingSpec={rankingSpec}
        columnsRegistry={columnsRegistry}
        visibleColumnIds={visibleColumnIds}
        totalMatchingCount={totalMatching}
        currentPage={page}
        pageSize={pageSize}
        currentSavedScreenId={currentSavedScreen?.saved_screen_id}
      />
    </div>
  );
}
