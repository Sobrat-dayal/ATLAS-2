"use client";

import React from "react";
import { MarketsNavigationTabs } from "@/components/markets/MarketsNavigationTabs";
import {
  useMarketMovers,
  useMoverMetrics,
  useMoverUniverses,
} from "@/hooks/markets";
import { MarketMoversHeader } from "./MarketMoversHeader";
import { MarketMoversTable } from "./MarketMoversTable";
import { MarketMoverInspector } from "./MarketMoverInspector";
import { MoverCategoryTabs } from "./MoverCategoryTabs";
import { MoverCoverageSummary } from "./MoverCoverageSummary";
import { MoverEmptyState, MoverErrorState } from "./MoverEmptyErrorStates";
import { MoverFilters } from "./MoverFilters";
import { MoverUniverseSelector } from "./MoverUniverseSelector";
import { MoverWindowSelector } from "./MoverWindowSelector";

export function MarketMoversPage() {
  const { universes, defaultUniverseId } = useMoverUniverses();

  const {
    data,
    items,
    coverage,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,
    universeId,
    setUniverseId,
    category,
    setCategory,
    window: selectedWindow,
    setWindow,
    exchange,
    setExchange,
    cursor,
    setCursor,
    selectedItem,
    setSelectedItem,
    resetFilters,
  } = useMarketMovers({
    initialUniverseId: defaultUniverseId,
  });

  const {
    supportedCategories,
    supportedWindows,
    activityMetricLabel,
  } = useMoverMetrics(universeId);

  // Active universe object
  const activeUniverse = universes.find((u) => u.universe_id === universeId) || universes[0];

  const handleNextPage = () => {
    if (data?.next_cursor) {
      setCursor(data.next_cursor);
    }
  };

  const handlePrevPage = () => {
    // Keyset backward navigation resets cursor to top of snapshot
    setCursor(null);
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-3 sm:px-4 md:px-6 py-4 flex flex-col min-h-screen">
      {/* 1. Global Markets Module Navigation */}
      <MarketsNavigationTabs />

      {/* 2. Market Movers Header */}
      <MarketMoversHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
        rankingCalculatedAt={data?.calculated_at}
        universeDisplayName={activeUniverse?.display_name}
      />

      {/* 3. Universe & Window Selectors */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-zinc-950/40 p-3 rounded-lg border border-[var(--atlas-border-subtle)] mb-4">
        <MoverUniverseSelector
          universes={universes}
          selectedUniverseId={universeId}
          onSelectUniverse={setUniverseId}
          disabled={isLoading && items.length === 0}
        />

        {activeUniverse && (
          <MoverWindowSelector
            supportedWindows={supportedWindows}
            selectedWindow={selectedWindow}
            defaultWindow={activeUniverse.default_window}
            onSelectWindow={setWindow}
            disabled={isLoading && items.length === 0}
          />
        )}
      </div>

      {/* 4. Category Tabs (Gainers / Losers / Most Active) */}
      <MoverCategoryTabs
        selectedCategory={category}
        onSelectCategory={setCategory}
        supportedCategories={supportedCategories}
        activityLabel={activityMetricLabel}
        disabled={isLoading && items.length === 0}
      />

      {/* 5. Filters (Venue / Exchange) */}
      <MoverFilters
        exchangeScope={activeUniverse?.exchange_scope || []}
        selectedExchange={exchange}
        onSelectExchange={setExchange}
        onReset={resetFilters}
        disabled={isLoading && items.length === 0}
      />

      {/* 6. Institutional Coverage Summary */}
      <MoverCoverageSummary
        coverage={coverage}
        universeDisplayName={activeUniverse?.display_name}
      />

      {/* 7. Error or Empty State */}
      {isError && (
        <MoverErrorState error={error} onRetry={() => refetch()} />
      )}

      {!isError && !isLoading && items.length === 0 && (
        <MoverEmptyState
          universeDisplayName={activeUniverse?.display_name}
          categoryLabel={category === "gainers" ? "gainers" : category === "losers" ? "losers" : "active securities"}
          onResetFilters={exchange !== "all" ? resetFilters : undefined}
        />
      )}

      {/* 8. Main Data Workspace: Table + Inspector */}
      {(!isError && (items.length > 0 || isLoading)) && (
        <div className="flex flex-col lg:flex-row gap-4 items-start w-full mt-2">
          <div className="flex-1 w-full overflow-hidden">
            <MarketMoversTable
              items={items}
              category={category}
              selectedItem={selectedItem}
              onSelectItem={setSelectedItem}
              isLoading={isLoading}
              hasMore={data?.has_more || false}
              nextCursor={data?.next_cursor}
              currentCursor={cursor}
              onNextPage={handleNextPage}
              onPrevPage={handlePrevPage}
            />
          </div>

          {selectedItem && (
            <MarketMoverInspector
              item={selectedItem}
              onClose={() => setSelectedItem(null)}
            />
          )}
        </div>
      )}
    </div>
  );
}
