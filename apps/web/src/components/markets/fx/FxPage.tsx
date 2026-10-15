"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import { useFxDirectory } from "@/hooks/markets/useFxDirectory";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { FxCoverageSummary } from "./FxCoverageSummary";
import { FxCurrencyConverter } from "./FxCurrencyConverter";
import { FxEmptyState } from "./FxEmptyState";
import { FxHeader } from "./FxHeader";
import { FxPairDirectoryTable } from "./FxPairDirectoryTable";
import { FxPairFilters } from "./FxPairFilters";
import { FxPairInspector } from "./FxPairInspector";

export function FxPage() {
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);

  const {
    data,
    currencies,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,
    query,
    setQuery,
    baseCurrency,
    setBaseCurrency,
    quoteCurrency,
    setQuoteCurrency,
    resetFilters,
    cursor,
    setCursor,
  } = useFxDirectory({ limit: 25 });

  const items = data?.items || [];
  const coverage = data?.coverage;

  const handleRowSelect = (instrumentEntityId: string) => {
    selectEntity(instrumentEntityId);
    setInspectorOpen(true);
  };

  const handleCloseInspector = () => {
    setInspectorOpen(false);
  };

  const isFiltered =
    query.trim() !== "" || baseCurrency !== "all" || quoteCurrency !== "all";

  const activeInspectorId =
    inspectorOpen && selectedEntityId ? selectedEntityId : null;

  const selectedItem = items.find(
    (item) => item.instrument_entity_id === selectedEntityId
  );

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Sub-Navigation */}
      <MarketsNavigationTabs />

      {/* 2. FX Header */}
      <FxHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 3. Error State with Retry */}
      {!isLoading && isError && (
        <div className="flex flex-col items-center justify-center py-10 px-4 bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded-md text-center mb-6">
          <h3 className="text-sm font-semibold text-rose-400">
            Failed to load FX directory
          </h3>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-4">
            {error?.message || "An error occurred while fetching currency pair observations."}
          </p>
          <button
            type="button"
            onClick={refetch}
            className="px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* 4. Coverage Summary */}
      {!isError && <FxCoverageSummary coverage={coverage} />}

      {/* 5. Directory Filters */}
      {!isError && (
        <FxPairFilters
          query={query}
          onQueryChange={setQuery}
          baseCurrency={baseCurrency}
          onBaseCurrencyChange={setBaseCurrency}
          quoteCurrency={quoteCurrency}
          onQuoteCurrencyChange={setQuoteCurrency}
          onReset={resetFilters}
          currencies={currencies}
          totalMatched={data?.total_count}
        />
      )}

      {/* 6. Empty State */}
      {!isLoading && !isError && items.length === 0 && (
        <FxEmptyState
          isSearchOrFiltered={isFiltered}
          onResetFilters={resetFilters}
        />
      )}

      {/* 7. Loading Skeleton */}
      {isLoading && items.length === 0 && (
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-8 text-center animate-pulse text-xs text-[var(--atlas-text-tertiary)]">
          Loading ATLAS Foreign Exchange Directory...
        </div>
      )}

      {/* 8. Main Workspace Grid */}
      {!isError && items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Table Area */}
          <div className="lg:col-span-8 space-y-5">
            <FxPairDirectoryTable
              items={items}
              isLoading={isLoading}
              selectedEntityId={selectedEntityId}
              onSelectEntity={handleRowSelect}
              hasMore={data?.has_more || false}
              nextCursor={data?.next_cursor}
              cursor={cursor}
              onPageChange={setCursor}
              totalMatched={data?.total_count}
            />
          </div>

          {/* Right Area: Inspector + Converter */}
          <div className="lg:col-span-4 space-y-5 sticky top-4">
            {activeInspectorId && (
              <FxPairInspector
                instrumentEntityId={activeInspectorId}
                onClose={handleCloseInspector}
              />
            )}

            <FxCurrencyConverter
              currencies={currencies}
              defaultFrom={selectedItem?.base_currency || "EUR"}
              defaultTo={selectedItem?.quote_currency || "USD"}
            />
          </div>
        </div>
      )}
    </div>
  );
}
