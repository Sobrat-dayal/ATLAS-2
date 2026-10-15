"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import { useEquityDirectory } from "@/hooks/markets/useEquityDirectory";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { EquitiesHeader } from "./EquitiesHeader";
import { EquityCoverageSummary } from "./EquityCoverageSummary";
import { EquityDirectoryFilters } from "./EquityDirectoryFilters";
import { EquityDirectoryTable } from "./EquityDirectoryTable";
import { EquityInspector } from "./EquityInspector";
import { EquityEmptyState } from "./EquityEmptyState";

export function EquitiesPage() {
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
    marketCountry,
    setMarketCountry,
    exchange,
    setExchange,
    equityType,
    setEquityType,
    listingStatus,
    setListingStatus,
    resetFilters,
    cursor,
    setCursor,
  } = useEquityDirectory({ limit: 25 });

  const items = data?.items || [];
  const coverage = data?.coverage;
  const availableFilters = data?.available_filters;

  const handleRowSelect = (instrumentEntityId: string) => {
    // 1. Select the canonical instrument entity in global context
    selectEntity(instrumentEntityId);
    // 2. Open inspector side panel
    setInspectorOpen(true);
  };

  const handleCloseInspector = () => {
    setInspectorOpen(false);
  };

  const isFiltered =
    query.trim() !== "" ||
    marketCountry !== "all" ||
    exchange !== "all" ||
    equityType !== "all" ||
    listingStatus !== "all";

  // Check if current selected entity is among visible equities or configured
  const activeInspectorId =
    inspectorOpen && selectedEntityId ? selectedEntityId : null;

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Module Sub-Navigation */}
      <MarketsNavigationTabs />

      {/* 2. Equities Header with Actions */}
      <EquitiesHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 3. Error State */}
      {!isLoading && isError && (
        <EquityEmptyState
          type="error"
          errorMessage={
            error?.message ||
            "Unable to retrieve equity securities from the ATLAS Markets endpoint."
          }
          onRetry={refetch}
        />
      )}

      {/* 4. Coverage Summary Metrics */}
      {!isError && (
        <EquityCoverageSummary
          coverage={coverage}
          generatedAt={data?.generated_at}
          scope={data?.scope}
        />
      )}

      {/* 5. Directory Filters */}
      {!isError && (
        <EquityDirectoryFilters
          query={query}
          onQueryChange={setQuery}
          marketCountry={marketCountry}
          onCountryChange={setMarketCountry}
          exchange={exchange}
          onExchangeChange={setExchange}
          equityType={equityType}
          onTypeChange={setEquityType}
          listingStatus={listingStatus}
          onListingStatusChange={setListingStatus}
          onReset={resetFilters}
          availableFilters={availableFilters}
          isLoading={isLoading}
        />
      )}

      {/* 6. Empty States */}
      {!isLoading && !isError && items.length === 0 && (
        <EquityEmptyState
          type={isFiltered ? "empty_search" : "empty_catalog"}
          onResetFilters={resetFilters}
        />
      )}

      {/* 7. Loading skeleton */}
      {isLoading && items.length === 0 && <EquityEmptyState type="loading" />}

      {/* 8. Split View: Table + Inspector */}
      {!isError && items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          <div className={`${activeInspectorId ? "lg:col-span-8" : "lg:col-span-12"} transition-all`}>
            <EquityDirectoryTable
              items={items}
              isLoading={isLoading}
              selectedEntityId={selectedEntityId}
              onSelectEntity={handleRowSelect}
              hasMore={data?.has_more || false}
              nextCursor={data?.next_cursor}
              cursor={cursor}
              onPageChange={setCursor}
            />
          </div>

          {activeInspectorId && (
            <div className="lg:col-span-4 sticky top-4">
              <EquityInspector
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
