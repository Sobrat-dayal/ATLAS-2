"use client";

/**
 * Custom React hook for Stage 79 Advanced Watchlist Enrichment.
 *
 * Coordinates batched enrichment retrieval:
 * - Identifies enabled enrichment columns from active configuration.
 * - Queries backend planner only for visible/enabled columns (zero hidden cost).
 * - Avoids per-cell N×M fanout.
 * - Reuses existing canonical fundamental, technical, event, and news data.
 * - Handles abort controllers on rapid watchlist switching.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { WatchlistColumnConfigV1, WatchlistRowCellValue } from "@/lib/watchlists/columns/types";
import { queryWatchlistEnrichment } from "@/lib/watchlists/enrichment/api";
import { WatchlistEnrichmentRequest } from "@/lib/watchlists/enrichment/types";
import { CanonicalLiveQuote } from "@/lib/watchlists/live";
import { WatchlistDetail } from "@/lib/watchlists/types";

export interface UseWatchlistEnrichmentReturn {
  enrichmentData: Map<string, Record<string, WatchlistRowCellValue>>;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

const ENRICHMENT_PREFIXES = [
  "fundamentals.",
  "valuation.",
  "technical.",
  "events.",
  "earnings.",
  "news.",
];

export function isEnrichmentColumnId(colId: string): boolean {
  return ENRICHMENT_PREFIXES.some((p) => colId.startsWith(p));
}

export function useWatchlistEnrichment(
  activeWatchlist: WatchlistDetail | null,
  columnConfig: WatchlistColumnConfigV1,
  liveQuotes?: Map<string, CanonicalLiveQuote>
): UseWatchlistEnrichmentReturn {
  const [enrichmentData, setEnrichmentData] = useState<
    Map<string, Record<string, WatchlistRowCellValue>>
  >(new Map());
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const activeWatchlistId = activeWatchlist?.id || null;
  const items = activeWatchlist?.items || [];
  const abortControllerRef = useRef<AbortController | null>(null);

  // Identify visible enrichment columns
  const visibleEnrichmentCols = columnConfig.visible_column_ids.filter(isEnrichmentColumnId);
  const visibleEnrichmentColsKey = visibleEnrichmentCols.join(",");

  const fetchEnrichment = useCallback(async () => {
    if (!activeWatchlistId || items.length === 0 || visibleEnrichmentCols.length === 0) {
      setEnrichmentData(new Map());
      setIsLoading(false);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const ac = new AbortController();
    abortControllerRef.current = ac;

    try {
      setIsLoading(true);
      setError(null);

      const request: WatchlistEnrichmentRequest = {
        watchlist_id: activeWatchlistId,
        selected_column_ids: visibleEnrichmentCols,
        items: items.map((it) => {
          const lq = liveQuotes?.get(it.instrument_entity_id?.toLowerCase());
          const effectivePrice = lq?.last_price ?? it.last_price;
          const parsedPrice = effectivePrice ? parseFloat(effectivePrice) : null;

          return {
            item_id: it.id,
            instrument_entity_id: it.instrument_entity_id,
            company_entity_id: it.issuer_entity_id,
            market_series_id: it.market_series_id,
            asset_class: it.asset_class,
            last_price: parsedPrice && !isNaN(parsedPrice) ? parsedPrice : null,
            quote_currency: it.quote_currency || "USD",
          };
        }),
      };

      const resp = await queryWatchlistEnrichment(activeWatchlistId, request, ac.signal);

      const resultMap = new Map<string, Record<string, WatchlistRowCellValue>>();
      for (const [itemId, colMap] of Object.entries(resp.results)) {
        const itemRecord: Record<string, WatchlistRowCellValue> = {};
        for (const [colId, val] of Object.entries(colMap)) {
          itemRecord[colId] = {
            status: val.status,
            value: val.value,
            unit: val.unit,
            currency: val.currency,
            fiscal_period: val.fiscal_period,
            fiscal_year: val.fiscal_year,
            period_end_date: val.period_end_date,
            observation_time: val.observation_time,
            publication_time: val.publication_time,
            as_of: val.as_of_date,
            source_id: val.source_id,
            methodology: val.methodology_id,
            methodology_id: val.methodology_id,
            headline: val.headline,
            publisher: val.publisher,
            url: val.url,
            event_status: val.event_status,
            reason: val.reason,
          };
        }
        resultMap.set(itemId, itemRecord);
      }

      setEnrichmentData(resultMap);
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load enrichment data");
    } finally {
      setIsLoading(false);
    }
  }, [activeWatchlistId, items, visibleEnrichmentColsKey, liveQuotes]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Asynchronous enrichment retrieval on watchlist/column configuration updates
    fetchEnrichment();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchEnrichment]);

  return {
    enrichmentData,
    isLoading,
    error,
    refetch: fetchEnrichment,
  };
}
