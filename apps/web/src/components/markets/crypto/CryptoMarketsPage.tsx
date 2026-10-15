"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import { useCryptoMarkets } from "@/hooks/markets/useCryptoMarkets";
import { CryptoSpotMarketDirectoryItem } from "@/lib/markets/crypto";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { CryptoCoverageSummary } from "./CryptoCoverageSummary";
import { CryptoEmptyState } from "./CryptoEmptyState";
import { CryptoHeader } from "./CryptoHeader";
import { CryptoMarketFilters } from "./CryptoMarketFilters";
import { CryptoMarketInspector } from "./CryptoMarketInspector";
import { CryptoSpotMarketTable } from "./CryptoSpotMarketTable";

export function CryptoMarketsPage() {
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);
  const [cursorHistory, setCursorHistory] = useState<(string | null)[]>([null]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);

  const {
    data,
    filterOptions,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,
    query,
    setQuery,
    baseAsset,
    setBaseAsset,
    quoteAsset,
    setQuoteAsset,
    venue,
    setVenue,
    quoteAssetType,
    setQuoteAssetType,
    resetFilters,
    setCursor,
  } = useCryptoMarkets({ limit: 25 });

  const items = data?.items || [];
  const coverage = data?.coverage_summary;

  const handleRowSelect = (market: CryptoSpotMarketDirectoryItem) => {
    selectEntity(market.instrument_entity_id);
    setInspectorOpen(true);
  };

  const handleCloseInspector = () => {
    setInspectorOpen(false);
  };

  const isFiltered =
    query.trim() !== "" ||
    baseAsset !== "all" ||
    quoteAsset !== "all" ||
    venue !== "all" ||
    quoteAssetType !== "all";

  const activeInspectorId =
    inspectorOpen && selectedEntityId ? selectedEntityId : null;

  // Pagination navigation
  const handleNextPage = () => {
    if (data?.next_cursor) {
      setCursor(data.next_cursor);
      setCursorHistory((prev) => [...prev, data.next_cursor || null]);
      setCurrentPageIndex((prev) => prev + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPageIndex > 0) {
      const prevIndex = currentPageIndex - 1;
      const targetCursor = cursorHistory[prevIndex] || null;
      setCursor(targetCursor);
      setCurrentPageIndex(prevIndex);
      setCursorHistory((prev) => prev.slice(0, prevIndex + 1));
    }
  };

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Sub-Navigation */}
      <MarketsNavigationTabs />

      {/* 2. Crypto Header */}
      <CryptoHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 3. Error Banner with Retry */}
      {!isLoading && isError && (
        <div className="flex flex-col items-center justify-center py-10 px-4 bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded-md text-center mb-6">
          <h3 className="text-sm font-semibold text-rose-400">
            Failed to load cryptocurrency spot markets
          </h3>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-4">
            {error?.message || "An error occurred while fetching crypto market data."}
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
      {!isError && <CryptoCoverageSummary summary={coverage} isLoading={isLoading} />}

      {/* 5. Directory Filters */}
      {!isError && (
        <CryptoMarketFilters
          query={query}
          onQueryChange={setQuery}
          baseAsset={baseAsset}
          onBaseAssetChange={setBaseAsset}
          quoteAsset={quoteAsset}
          onQuoteAssetChange={setQuoteAsset}
          venue={venue}
          onVenueChange={setVenue}
          quoteAssetType={quoteAssetType}
          onQuoteAssetTypeChange={setQuoteAssetType}
          onReset={resetFilters}
          filterOptions={filterOptions}
          totalMatched={data?.total_count || 0}
          isLoading={isLoading}
        />
      )}

      {/* 6. Empty State */}
      {!isLoading && !isError && items.length === 0 && (
        <CryptoEmptyState
          isFiltered={isFiltered}
          onResetFilters={resetFilters}
        />
      )}

      {/* 7. Loading Skeleton */}
      {isLoading && items.length === 0 && (
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-8 text-center animate-pulse text-xs text-[var(--atlas-text-tertiary)]">
          Loading ATLAS Cryptocurrency Markets Directory...
        </div>
      )}

      {/* 8. Main Workspace Grid: Table + Inspector */}
      {!isError && items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Table Area */}
          <div className={activeInspectorId ? "lg:col-span-8 space-y-4" : "lg:col-span-12 space-y-4"}>
            <CryptoSpotMarketTable
              markets={items}
              selectedPairId={selectedEntityId}
              onSelectPair={handleRowSelect}
              isLoading={isLoading}
              totalCount={data?.total_count || 0}
              nextCursor={data?.next_cursor}
              onNextPage={handleNextPage}
              onPreviousPage={handlePreviousPage}
              hasPreviousPage={currentPageIndex > 0}
            />
          </div>

          {/* Right Inspector Panel */}
          {activeInspectorId && (
            <div className="lg:col-span-4 sticky top-4">
              <CryptoMarketInspector
                selectedPairId={activeInspectorId}
                onClose={handleCloseInspector}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
