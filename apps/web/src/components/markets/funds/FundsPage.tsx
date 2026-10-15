"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import { useFundDirectory } from "@/hooks/markets/useFundDirectory";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { FundsHeader } from "./FundsHeader";
import { FundCoverageSummary } from "./FundCoverageSummary";
import { FundTypeSelector } from "./FundTypeSelector";
import { FundDirectoryFilters } from "./FundDirectoryFilters";
import { FundDirectoryTable } from "./FundDirectoryTable";
import { FundInspector } from "./FundInspector";
import { FundEmptyState } from "./FundEmptyState";

export function FundsPage() {
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);

  const {
    data,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,
    query,
    setQuery,
    fundType,
    setFundType,
    marketCountry,
    setMarketCountry,
    exchange,
    setExchange,
    domicile,
    setDomicile,
    fundCategory,
    setFundCategory,
    shareClassCurrency,
    setShareClassCurrency,
    resetFilters,
    cursor,
    setCursor,
  } = useFundDirectory({ limit: 25 });

  const items = data?.items || [];
  const coverage = data?.coverage;
  const availableFilters = data?.available_filters;

  const handleRowSelect = (instrumentEntityId: string) => {
    selectEntity(instrumentEntityId);
    setInspectorOpen(true);
  };

  const handleCloseInspector = () => {
    setInspectorOpen(false);
  };

  const isFiltered =
    query.trim() !== "" ||
    fundType !== "ALL" ||
    marketCountry !== "all" ||
    exchange !== "all" ||
    domicile !== "all" ||
    fundCategory !== "all" ||
    shareClassCurrency !== "all";

  const activeInspectorId =
    inspectorOpen && selectedEntityId ? selectedEntityId : null;

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Sub-Navigation */}
      <MarketsNavigationTabs />

      {/* 2. Funds Header */}
      <FundsHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 3. Error State with Retry */}
      {!isLoading && isError && (
        <div className="flex flex-col items-center justify-center py-10 px-4 bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded-md text-center mb-6">
          <h3 className="text-sm font-semibold text-rose-400">
            Failed to load funds directory
          </h3>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-4">
            {error?.message || "An error occurred while fetching the fund catalog."}
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
      {!isError && (
        <FundCoverageSummary
          coverage={coverage}
          generatedAt={data?.generated_at}
          scope={data?.scope}
        />
      )}

      {/* 5. Fund Type Selector */}
      {!isError && (
        <FundTypeSelector
          selectedType={fundType}
          onSelectType={setFundType}
          options={availableFilters?.fund_types}
        />
      )}

      {/* 6. Directory Filters */}
      {!isError && (
        <FundDirectoryFilters
          query={query}
          onQueryChange={setQuery}
          marketCountry={marketCountry}
          onCountryChange={setMarketCountry}
          exchange={exchange}
          onExchangeChange={setExchange}
          domicile={domicile}
          onDomicileChange={setDomicile}
          fundCategory={fundCategory}
          onCategoryChange={setFundCategory}
          shareClassCurrency={shareClassCurrency}
          onCurrencyChange={setShareClassCurrency}
          onReset={resetFilters}
          options={availableFilters}
          totalMatched={data?.total_matched}
        />
      )}

      {/* 7. Empty State */}
      {!isLoading && !isError && items.length === 0 && (
        <FundEmptyState
          isSearchOrFiltered={isFiltered}
          onResetFilters={resetFilters}
        />
      )}

      {/* 8. Loading Skeleton */}
      {isLoading && items.length === 0 && (
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-8 text-center animate-pulse text-xs text-[var(--atlas-text-tertiary)]">
          Loading ATLAS Fund Directory...
        </div>
      )}

      {/* 9. Split View: Table + Inspector */}
      {!isError && items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          <div className={`${activeInspectorId ? "lg:col-span-8" : "lg:col-span-12"} transition-all`}>
            <FundDirectoryTable
              items={items}
              isLoading={isLoading}
              selectedEntityId={selectedEntityId}
              onSelectEntity={handleRowSelect}
              hasMore={data?.has_more || false}
              nextCursor={data?.next_cursor}
              cursor={cursor}
              onPageChange={setCursor}
              totalMatched={data?.total_matched}
            />
          </div>

          {activeInspectorId && (
            <div className="lg:col-span-4 sticky top-4">
              <FundInspector
                instrumentEntityId={activeInspectorId}
                onClose={handleCloseInspector}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
