"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  CountryOption,
  ExchangeOption,
  FilterCriterion,
  ScreenerColumnDefinition,
  ScreenerCoverageResponse,
  ScreenerFilterDefinition,
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
      overrideSort?: SortCriterion[]
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
  };

  const handleToggleExchange = (mic: string) => {
    setSelectedExchanges((prev) =>
      prev.includes(mic) ? prev.filter((m) => m !== mic) : [...prev, mic]
    );
    setPage(1);
  };

  const handleToggleCountry = (code: string) => {
    setSelectedCountries((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
    setPage(1);
  };

  const handleToggleSector = (name: string) => {
    setSelectedSectors((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
    setPage(1);
  };

  const handleAddFilter = (criterion: FilterCriterion) => {
    setActiveFilters((prev) => {
      // If same filter_id exists, update it, else add
      const idx = prev.findIndex((f) => f.filter_id === criterion.filter_id);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = criterion;
        return copy;
      }
      return [...prev, criterion];
    });
    setPage(1);
  };

  const handleRemoveFilter = (filterId: string) => {
    setActiveFilters((prev) => prev.filter((f) => f.filter_id !== filterId));
    setPage(1);
  };

  const handleSetFilters = (filters: FilterCriterion[]) => {
    setActiveFilters(filters);
    setPage(1);
    executeQuery(1, undefined, filters);
  };

  const handleClearFilters = () => {
    setActiveFilters([]);
    setSelectedExchanges([]);
    setSelectedCountries([]);
    setSelectedSectors([]);
    setPage(1);
    executeQuery(1, undefined, []);
  };


  const handleSortToggle = (fieldId: string) => {
    setSortCriteria((prev) => {
      const current = prev.find((s) => s.field_id === fieldId);
      if (!current) {
        return [{ field_id: fieldId, direction: "desc" }];
      }
      if (current.direction === "desc") {
        return [{ field_id: fieldId, direction: "asc" }];
      }
      return DEFAULT_SORT;
    });
    setPage(1);
    executeQuery(1, undefined, undefined, [
      sortCriteria[0]?.field_id === fieldId && sortCriteria[0]?.direction === "desc"
        ? { field_id: fieldId, direction: "asc" }
        : { field_id: fieldId, direction: "desc" },
    ]);
  };

  const handleToggleColumn = (columnId: string) => {
    setVisibleColumnIds((prev) =>
      prev.includes(columnId) ? prev.filter((c) => c !== columnId) : [...prev, columnId]
    );
  };

  const handleResetColumns = () => {
    const defaultCols = columnsRegistry.filter((col) => col.default_visible).map((c) => c.column_id);
    setVisibleColumnIds(defaultCols);
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
    toggleColumn: handleToggleColumn,
    resetColumns: handleResetColumns,
    goToPage: handlePageChange,
    changePageSize: handlePageSizeChange,
    selectRow: setSelectedRow,
    setIsCoverageOpen,
    setIsColumnManagerOpen,
    runScreener: executeQuery,
  };
}
