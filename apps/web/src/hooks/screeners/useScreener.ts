"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  CountryOption,
  ExchangeOption,
  FilterCriterion,
  SavedScreener,
  ScreenerColumnDefinition,
  ScreenerCoverageResponse,
  ScreenerFilterDefinition,
  ScreenerRankingSpec,
  ScreenerResultRow,
  ScreenerRunRequest,
  ScreenerRunResponse,
  ScreenerUniverseDefinition,
  SectorOption,
  SortCriterion,
} from "@/lib/screeners/types";
import {
  fetchScreenerColumns,
  fetchScreenerCoverage,
  fetchScreenerExchanges,
  fetchScreenerFilters,
  fetchScreenerGeographies,
  fetchScreenerIndustries,
  fetchScreenerUniverses,
  runScreenerQuery,
} from "@/lib/screeners/api";

const DEFAULT_SORT: SortCriterion[] = [
  { field_id: "market_cap", direction: "desc" },
];

export function useScreener() {
  // Metadata catalogs
  const [universes, setUniverses] = useState<ScreenerUniverseDefinition[]>([]);
  const [filtersRegistry, setFiltersRegistry] = useState<ScreenerFilterDefinition[]>([]);
  const [columnsRegistry, setColumnsRegistry] = useState<ScreenerColumnDefinition[]>([]);
  const [exchanges, setExchanges] = useState<ExchangeOption[]>([]);
  const [geographies, setGeographies] = useState<CountryOption[]>([]);
  const [industries, setIndustries] = useState<SectorOption[]>([]);
  const [coverage, setCoverage] = useState<ScreenerCoverageResponse | null>(null);

  // Query state
  const [selectedUniverseId, setSelectedUniverseId] = useState<string>("common_equity");
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [activeFilters, setActiveFilters] = useState<FilterCriterion[]>([]);
  const [sortCriteria, setSortCriteria] = useState<SortCriterion[]>(DEFAULT_SORT);
  const [visibleColumnIds, setVisibleColumnIds] = useState<string[]>([]);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(50);

  // Stage 97: Advanced Sort, Ranking & Saved Screens state
  const [rankingSpec, setRankingSpec] = useState<ScreenerRankingSpec | null>(null);
  const [currentSavedScreen, setCurrentSavedScreen] = useState<SavedScreener | null>(null);
  const [isDirtyFromSaved, setIsDirtyFromSaved] = useState<boolean>(false);

  // Modals state
  const [isSavedScreensOpen, setIsSavedScreensOpen] = useState<boolean>(false);
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState<boolean>(false);
  const [isSaveAs, setIsSaveAs] = useState<boolean>(false);
  const [isRankingModalOpen, setIsRankingModalOpen] = useState<boolean>(false);
  const [isExportDialogOpen, setIsExportDialogOpen] = useState<boolean>(false);
  const [isAdvancedSortOpen, setIsAdvancedSortOpen] = useState<boolean>(false);

  // Output & UI state
  const [results, setResults] = useState<ScreenerRunResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRow, setSelectedRow] = useState<ScreenerResultRow | null>(null);
  const [isCoverageOpen, setIsCoverageOpen] = useState<boolean>(false);
  const [isColumnManagerOpen, setIsColumnManagerOpen] = useState<boolean>(false);

  const abortControllerRef = useRef<AbortController | null>(null);

  // 1. Initial metadata loading
  useEffect(() => {
    let isMounted = true;
    async function loadMetadata() {
      try {
        const [u, f, c, e, g, ind, cov] = await Promise.all([
          fetchScreenerUniverses(),
          fetchScreenerFilters(),
          fetchScreenerColumns(),
          fetchScreenerExchanges(),
          fetchScreenerGeographies(),
          fetchScreenerIndustries(),
          fetchScreenerCoverage(),
        ]);
        if (!isMounted) return;
        setUniverses(u);
        setFiltersRegistry(f);
        setColumnsRegistry(c);
        setExchanges(e);
        setGeographies(g);
        setIndustries(ind);
        setCoverage(cov);

        // Set default visible columns
        const defaultCols = c.filter((col) => col.default_visible).map((col) => col.column_id);
        setVisibleColumnIds(defaultCols);
      } catch (err: unknown) {
        if (!isMounted) return;
        console.warn("Error loading screener metadata:", err);
      }
    }
    loadMetadata();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Query execution
  const executeQuery = useCallback(
    async (
      overridePage?: number,
      overrideUniverseId?: string,
      overrideFilters?: FilterCriterion[],
      overrideSort?: SortCriterion[],
      overrideRanking?: ScreenerRankingSpec | null
    ) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setLoading(true);
      setError(null);

      const targetUniverse = overrideUniverseId ?? selectedUniverseId;
      const targetFilters = overrideFilters ?? activeFilters;
      const targetSort = overrideSort ?? sortCriteria;
      const targetRanking = overrideRanking !== undefined ? overrideRanking : rankingSpec;
      const targetPage = overridePage ?? page;

      const requestPayload: ScreenerRunRequest = {
        universe: {
          universe_id: targetUniverse,
          exchange_mics: selectedExchanges.length > 0 ? selectedExchanges : null,
          listing_country_codes: selectedCountries.length > 0 ? selectedCountries : null,
          sectors: selectedSectors.length > 0 ? selectedSectors : null,
        },
        filters: targetFilters,
        sort: targetSort,
        multi_sort: targetSort.length > 1 ? targetSort : undefined,
        ranking: targetRanking ?? undefined,
        columns: visibleColumnIds.length > 0 ? visibleColumnIds : null,
        page: targetPage,
        page_size: pageSize,
      };

      try {
        const data = await runScreenerQuery(requestPayload, abortController.signal);
        setResults(data);
        setPage(data.page);
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        const msg = err instanceof Error ? err.message : "Failed to run screener query.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [
      selectedUniverseId,
      activeFilters,
      sortCriteria,
      rankingSpec,
      page,
      pageSize,
      selectedExchanges,
      selectedCountries,
      selectedSectors,
      visibleColumnIds,
    ]
  );

  // Trigger query on initial load or universe change
  useEffect(() => {
    executeQuery();
  }, [selectedUniverseId, selectedExchanges, selectedCountries, selectedSectors]);

  // Actions
  const handleUniverseChange = (id: string) => {
    setSelectedUniverseId(id);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleToggleExchange = (mic: string) => {
    setSelectedExchanges((prev) =>
      prev.includes(mic) ? prev.filter((m) => m !== mic) : [...prev, mic]
    );
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleToggleCountry = (code: string) => {
    setSelectedCountries((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleToggleSector = (name: string) => {
    setSelectedSectors((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleAddFilter = (criterion: FilterCriterion) => {
    setActiveFilters((prev) => {
      const idx = prev.findIndex((f) => f.filter_id === criterion.filter_id);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = criterion;
        return copy;
      }
      return [...prev, criterion];
    });
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleRemoveFilter = (filterId: string) => {
    setActiveFilters((prev) => prev.filter((f) => f.filter_id !== filterId));
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleSetFilters = (filters: FilterCriterion[]) => {
    setActiveFilters(filters);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
    executeQuery(1, undefined, filters);
  };

  const handleClearFilters = () => {
    setActiveFilters([]);
    setSelectedExchanges([]);
    setSelectedCountries([]);
    setSelectedSectors([]);
    setRankingSpec(null);
    setSortCriteria(DEFAULT_SORT);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
    executeQuery(1, undefined, [], DEFAULT_SORT, null);
  };

  const handleSortToggle = (fieldId: string) => {
    const newSort: SortCriterion[] = (() => {
      const current = sortCriteria.find((s) => s.field_id === fieldId);
      if (!current) {
        return [{ field_id: fieldId, direction: "desc" }];
      }
      if (current.direction === "desc") {
        return [{ field_id: fieldId, direction: "asc" }];
      }
      return DEFAULT_SORT;
    })();

    setSortCriteria(newSort);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
    executeQuery(1, undefined, undefined, newSort);
  };

  const handleSetMultiSort = (newSort: SortCriterion[]) => {
    const validSort = newSort.length > 0 ? newSort : DEFAULT_SORT;
    setSortCriteria(validSort);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
    executeQuery(1, undefined, undefined, validSort);
  };

  const handleApplyRanking = (spec: ScreenerRankingSpec | null) => {
    setRankingSpec(spec);
    setPage(1);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
    executeQuery(1, undefined, undefined, undefined, spec);
  };

  const handleLoadSavedScreen = (screen: SavedScreener) => {
    setSelectedUniverseId(screen.universe.universe_id);
    setSelectedExchanges(screen.universe.exchange_mics ?? []);
    setSelectedCountries(screen.universe.listing_country_codes ?? []);
    setSelectedSectors(screen.universe.sectors ?? []);
    setActiveFilters(screen.filters);
    const screenSort = screen.sort && screen.sort.length > 0 ? screen.sort : DEFAULT_SORT;
    setSortCriteria(screenSort);
    setRankingSpec(screen.ranking ?? null);
    if (screen.columns && screen.columns.length > 0) {
      setVisibleColumnIds(screen.columns);
    }
    setCurrentSavedScreen(screen);
    setIsDirtyFromSaved(false);
    setPage(1);

    executeQuery(
      1,
      screen.universe.universe_id,
      screen.filters,
      screenSort,
      screen.ranking ?? null
    );
  };

  const handleClearSavedScreen = () => {
    setCurrentSavedScreen(null);
    setIsDirtyFromSaved(false);
  };

  const handleSavedScreenSaved = (saved: SavedScreener) => {
    setCurrentSavedScreen(saved);
    setIsDirtyFromSaved(false);
  };

  const handleToggleColumn = (columnId: string) => {
    setVisibleColumnIds((prev) =>
      prev.includes(columnId) ? prev.filter((c) => c !== columnId) : [...prev, columnId]
    );
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handleResetColumns = () => {
    const defaultCols = columnsRegistry.filter((col) => col.default_visible).map((c) => c.column_id);
    setVisibleColumnIds(defaultCols);
    if (currentSavedScreen) setIsDirtyFromSaved(true);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    executeQuery(newPage);
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setPage(1);
    executeQuery(1);
  };

  return {
    // Catalogs
    universes,
    filtersRegistry,
    columnsRegistry,
    exchanges,
    geographies,
    industries,
    coverage,

    // Selections
    selectedUniverseId,
    selectedExchanges,
    selectedCountries,
    selectedSectors,
    activeFilters,
    sortCriteria,
    visibleColumnIds,
    page,
    pageSize,

    // Stage 97: Ranking & Saved Screen state
    rankingSpec,
    currentSavedScreen,
    isDirtyFromSaved,

    // Modals state
    isSavedScreensOpen,
    isSaveDialogOpen,
    isSaveAs,
    isRankingModalOpen,
    isExportDialogOpen,
    isAdvancedSortOpen,

    // Outputs
    results,
    loading,
    error,
    selectedRow,
    isCoverageOpen,
    isColumnManagerOpen,

    // Handlers
    setUniverse: handleUniverseChange,
    toggleExchange: handleToggleExchange,
    toggleCountry: handleToggleCountry,
    toggleSector: handleToggleSector,
    addFilter: handleAddFilter,
    setFilters: handleSetFilters,
    removeFilter: handleRemoveFilter,
    clearFilters: handleClearFilters,
    setSorting: handleSortToggle,
    setMultiSort: handleSetMultiSort,
    applyRanking: handleApplyRanking,
    loadSavedScreen: handleLoadSavedScreen,
    clearSavedScreen: handleClearSavedScreen,
    onSavedScreenSaved: handleSavedScreenSaved,
    toggleColumn: handleToggleColumn,
    resetColumns: handleResetColumns,
    goToPage: handlePageChange,
    changePageSize: handlePageSizeChange,
    selectRow: setSelectedRow,
    setIsCoverageOpen,
    setIsColumnManagerOpen,
    setIsSavedScreensOpen,
    setIsSaveDialogOpen,
    setIsSaveAs,
    setIsRankingModalOpen,
    setIsExportDialogOpen,
    setIsAdvancedSortOpen,
    runScreener: executeQuery,
  };
}
