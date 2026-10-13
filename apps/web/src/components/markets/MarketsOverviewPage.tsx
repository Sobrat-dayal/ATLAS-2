"use client";

import React from "react";
import { useMarketsOverview } from "@/hooks/markets/useMarketsOverview";
import { MarketsHeader } from "./MarketsHeader";
import { MarketsCoverageSummary } from "./MarketsCoverageSummary";
import { MarketsGroupSelector } from "./MarketsGroupSelector";
import { FeaturedMarketInstruments } from "./FeaturedMarketInstruments";
import { MarketsInstrumentTable } from "./MarketsInstrumentTable";
import { MarketsEmptyState } from "./MarketsEmptyState";

export function MarketsOverviewPage() {
  const {
    data,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,
    selectedGroup,
    setSelectedGroup,
    cursor,
    setCursor,
  } = useMarketsOverview({ limit: 50 });

  const items = data?.items || [];
  const featuredItems = data?.featured_items || [];
  const groups = data?.groups || [];
  const coverage = data?.coverage;

  return (
    <div className="w-full min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* 1. Markets Header with Actions */}
      <MarketsHeader
        onRefresh={refetch}
        isRefreshing={isRefetching}
        isLoading={isLoading}
      />

      {/* 2. Error State */}
      {!isLoading && isError && (
        <MarketsEmptyState
          title="Markets Overview Disconnected"
          description={
            error?.message ||
            "Unable to retrieve market observations from the ATLAS Markets endpoint."
          }
          isError={true}
          onRetry={refetch}
        />
      )}

      {/* 3. Coverage Summary */}
      {!isError && (
        <MarketsCoverageSummary
          coverage={coverage}
          generatedAt={data?.generated_at}
          scope={data?.scope}
        />
      )}

      {/* 4. Featured Instruments Grid (Top Section) */}
      {!isError && featuredItems.length > 0 && selectedGroup === "all" && (
        <FeaturedMarketInstruments items={featuredItems} />
      )}

      {/* 5. Market Group Selector Tabs */}
      {!isError && groups.length > 0 && (
        <MarketsGroupSelector
          groups={groups}
          selectedGroup={selectedGroup}
          onSelectGroup={setSelectedGroup}
        />
      )}

      {/* 6. Empty Category or Empty Catalog */}
      {!isLoading && !isError && items.length === 0 && (
        <MarketsEmptyState
          title="No Market Instruments Found"
          description={
            selectedGroup !== "all"
              ? `No configured market instruments in the '${selectedGroup}' asset class.`
              : "No canonical market instruments configured for this overview."
          }
        />
      )}

      {/* 7. Detailed Market Instrument Table */}
      {!isError && (items.length > 0 || isLoading) && (
        <MarketsInstrumentTable
          items={items}
          isLoading={isLoading}
          hasMore={data?.has_more || false}
          nextCursor={data?.next_cursor}
          cursor={cursor}
          onPageChange={setCursor}
        />
      )}
    </div>
  );
}
