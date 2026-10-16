"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import {
  useCommodities,
  useFuturesContractOverview,
  useFuturesContracts,
} from "@/hooks/markets";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { CommodityDirectoryTable } from "./CommodityDirectoryTable";
import { FuturesContractFilters } from "./FuturesContractFilters";
import { FuturesContractInspector } from "./FuturesContractInspector";
import { FuturesContractTable } from "./FuturesContractTable";
import { FuturesCoverageSummary } from "./FuturesCoverageSummary";
import { FuturesHeader } from "./FuturesHeader";
import { FuturesMarketTabs, FuturesTab } from "./FuturesMarketTabs";
import { SpotBenchmarkDirectoryTable } from "./SpotBenchmarkDirectoryTable";

export function FuturesMarketsPage() {
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [activeTab, setActiveTab] = useState<FuturesTab>("contracts");
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);

  // Contracts Query Hook
  const {
    data,
    filterOptions,
    isLoading: isContractsLoading,
    isRefetching,
    isError: isContractsError,
    error: contractsError,
    refetch: refetchContracts,
    query,
    setQuery,
    category,
    setCategory,
    exchange,
    setExchange,
    productEntityId,
    setProductEntityId,
    contractMonth,
    setContractMonth,
    settlementType,
    setSettlementType,
    lifecycleStatus,
    setLifecycleStatus,
    resetFilters,
    cursor,
    setCursor,
  } = useFuturesContracts({ limit: 25 });

  // Commodities Query Hook
  const {
    data: commoditiesData,
    spotBenchmarks: spotData,
    isLoading: isCommoditiesLoading,
    category: commodityCategory,
    setCategory: setCommodityCategory,
    query: commodityQuery,
    setQuery: setCommodityQuery,
    refetch: refetchCommodities,
  } = useCommodities();

  // Selected Contract Overview
  const {
    data: overviewData,
    isLoading: isOverviewLoading,
  } = useFuturesContractOverview(selectedEntityId);

  const contracts = data?.items || [];
  const coverage = data?.coverage;
  const hasMore = Boolean(data?.has_more);
  const nextCursor = data?.next_cursor;

  const handleContractSelect = (instrumentEntityId: string) => {
    selectEntity(instrumentEntityId);
    setInspectorOpen(true);
  };

  const handleCloseInspector = () => {
    setInspectorOpen(false);
  };

  const handleNextPage = () => {
    if (nextCursor) {
      setCursor(nextCursor);
    }
  };

  const handlePrevPage = () => {
    // Keyset pagination rewind
    setCursor(null);
  };

  const handleRefresh = async () => {
    if (activeTab === "contracts") {
      await refetchContracts();
    } else {
      await refetchCommodities();
    }
  };

  const showInspector = Boolean(inspectorOpen && selectedEntityId && overviewData);

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Sub-Navigation (Stages 56-62) */}
      <MarketsNavigationTabs />

      {/* 2. Futures Header */}
      <FuturesHeader
        onRefresh={handleRefresh}
        isRefreshing={isRefetching}
        isLoading={isContractsLoading || isCommoditiesLoading}
      />

      {/* 3. Coverage Summary */}
      <FuturesCoverageSummary
        coverage={coverage}
        isLoading={isContractsLoading}
      />

      {/* 4. Sub-View Tabs (Contracts / Commodities / Spot) */}
      <FuturesMarketTabs
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        contractsCount={coverage?.total_contracts}
        commoditiesCount={coverage?.total_commodities}
        spotCount={spotData?.total || 5}
      />

      {/* 5. Error Banner */}
      {!isContractsLoading && isContractsError && (
        <div
          role="alert"
          className="flex flex-col items-center justify-center py-6 px-4 bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded text-center mb-4"
        >
          <h3 className="text-sm font-semibold text-rose-400">
            Failed to load futures market data
          </h3>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-3">
            {contractsError?.message || "An error occurred while fetching derivatives data."}
          </p>
          <button
            type="button"
            onClick={() => refetchContracts()}
            className="px-3 py-1.5 text-xs font-medium rounded bg-rose-500/10 text-rose-300 border border-rose-500/30 hover:bg-rose-500/20 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* 6. Main Tab Content */}
      {activeTab === "contracts" && (
        <div>
          {/* Filters */}
          <FuturesContractFilters
            query={query}
            onQueryChange={setQuery}
            category={category}
            onCategoryChange={setCategory}
            exchange={exchange}
            onExchangeChange={setExchange}
            productEntityId={productEntityId}
            onProductEntityIdChange={setProductEntityId}
            contractMonth={contractMonth}
            onContractMonthChange={setContractMonth}
            settlementType={settlementType}
            onSettlementTypeChange={setSettlementType}
            lifecycleStatus={lifecycleStatus}
            onLifecycleStatusChange={setLifecycleStatus}
            onReset={resetFilters}
            filterOptions={filterOptions}
            totalMatches={data?.total || 0}
          />

          {/* Table & Inspector Split View */}
          <div
            className={`grid gap-4 items-start ${
              showInspector ? "grid-cols-1 lg:grid-cols-3" : "grid-cols-1"
            }`}
          >
            <div className={showInspector ? "lg:col-span-2" : "col-span-1"}>
              <FuturesContractTable
                contracts={contracts}
                selectedContractId={selectedEntityId}
                onSelectContract={handleContractSelect}
                isLoading={isContractsLoading}
                total={data?.total || 0}
                hasMore={hasMore}
                onNextPage={handleNextPage}
                onPrevPage={handlePrevPage}
                canPrevPage={Boolean(cursor)}
                onResetFilters={resetFilters}
              />
            </div>

            {showInspector && (
              <div className="lg:col-span-1 lg:sticky lg:top-4">
                <FuturesContractInspector
                  overview={overviewData}
                  isLoading={isOverviewLoading}
                  onClose={handleCloseInspector}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "commodities" && (
        <CommodityDirectoryTable
          commodities={commoditiesData?.items || []}
          isLoading={isCommoditiesLoading}
          category={commodityCategory}
          onCategoryChange={setCommodityCategory}
          query={commodityQuery}
          onQueryChange={setCommodityQuery}
        />
      )}

      {activeTab === "spot" && (
        <SpotBenchmarkDirectoryTable
          benchmarks={spotData?.items || []}
          isLoading={isCommoditiesLoading}
        />
      )}
    </div>
  );
}
