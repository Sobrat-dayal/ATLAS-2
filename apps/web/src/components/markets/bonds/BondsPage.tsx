"use client";

import React, { useState } from "react";
import { useSelectedEntity } from "@/hooks/entity";
import { useBondDirectory, useBondOverview } from "@/hooks/markets";
import { BondDirectoryItem } from "@/lib/markets/bonds";
import { MarketsNavigationTabs } from "../MarketsNavigationTabs";
import { BondCoverageSummary } from "./BondCoverageSummary";
import { BondDirectoryFilters } from "./BondDirectoryFilters";
import { BondDirectoryTable } from "./BondDirectoryTable";
import { BondInspector } from "./BondInspector";
import { BondsHeader } from "./BondsHeader";

export function BondsPage() {
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);

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
    issuerType,
    setIssuerType,
    bondType,
    setBondType,
    currency,
    setCurrency,
    couponType,
    setCouponType,
    maturityBucket,
    setMaturityBucket,
    resetFilters,
    setCursor,
  } = useBondDirectory({ limit: 25 });

  const {
    data: overviewData,
    isLoading: isOverviewLoading,
  } = useBondOverview(selectedEntityId);

  const items = data?.items || [];
  const coverage = data?.coverage;
  const hasMore = Boolean(data?.has_more);
  const nextCursor = data?.next_cursor;

  const hasActiveFilters =
    query.trim() !== "" ||
    issuerType !== "all" ||
    bondType !== "all" ||
    currency !== "all" ||
    couponType !== "all" ||
    maturityBucket !== "all";

  const handleRowSelect = (item: BondDirectoryItem) => {
    selectEntity(item.instrument_entity_id);
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

  const activeInspector = inspectorOpen && selectedEntityId;

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Sub-Navigation */}
      <MarketsNavigationTabs />

      {/* 2. Bonds Header */}
      <BondsHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 3. Error Banner with Retry */}
      {!isLoading && isError && (
        <div
          role="alert"
          className="flex flex-col items-center justify-center py-8 px-4 bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded text-center mb-4"
        >
          <h3 className="text-sm font-semibold text-rose-400">
            Failed to load fixed-income debt securities
          </h3>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-3">
            {error?.message || "An error occurred while fetching bond market data."}
          </p>
          <button
            type="button"
            onClick={() => refetch()}
            className="px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* 4. Coverage Summary */}
      {!isError && (
        <BondCoverageSummary coverage={coverage} isLoading={isLoading} />
      )}

      {/* 5. Directory Filters */}
      {!isError && (
        <BondDirectoryFilters
          query={query}
          onQueryChange={setQuery}
          issuerType={issuerType}
          onIssuerTypeChange={setIssuerType}
          bondType={bondType}
          onBondTypeChange={setBondType}
          currency={currency}
          onCurrencyChange={setCurrency}
          couponType={couponType}
          onCouponTypeChange={setCouponType}
          maturityBucket={maturityBucket}
          onMaturityBucketChange={setMaturityBucket}
          onResetFilters={resetFilters}
          filterOptions={filterOptions}
          totalResults={data?.total ?? 0}
        />
      )}

      {/* 6. Main Workspace Grid: Table + Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Table Area */}
        <div
          className={
            activeInspector
              ? "lg:col-span-8 space-y-4"
              : "lg:col-span-12 space-y-4"
          }
        >
          <BondDirectoryTable
            items={items}
            isLoading={isLoading}
            isError={isError}
            errorMessage={error?.message}
            total={data?.total ?? 0}
            selectedId={selectedEntityId}
            onSelect={handleRowSelect}
            onResetFilters={resetFilters}
            onRetry={refetch}
            nextCursor={nextCursor}
            hasMore={hasMore}
            onNextPage={handleNextPage}
            hasActiveFilters={hasActiveFilters}
          />
        </div>

        {/* Right Inspector Panel */}
        {activeInspector && (
          <div className="lg:col-span-4 sticky top-4">
            <BondInspector
              overview={overviewData}
              isLoading={isOverviewLoading}
              onClose={handleCloseInspector}
            />
          </div>
        )}
      </div>
    </div>
  );
}
