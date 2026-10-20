"use client";

/**
 * Custom React hook for Stage 78 Live Watchlist Updates.
 *
 * Coordinates live market data streaming, viewport visible range prioritization,
 * coalesced state updates, connection health, and cleanup.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { WatchlistDetail } from "@/lib/watchlists/types";
import {
  CanonicalLiveQuote,
  LiveWatchlistStatus,
  VisibleRowRange,
  WatchlistLiveController,
} from "@/lib/watchlists/live";

export interface UseWatchlistLiveReturn {
  liveQuotes: Map<string, CanonicalLiveQuote>;
  status: LiveWatchlistStatus;
  reconnect: () => Promise<void>;
  updateVisibleRange: (range: VisibleRowRange | null) => void;
  getQuoteForInstrument: (instrumentEntityId: string) => CanonicalLiveQuote | null;
}

const DEFAULT_STATUS: LiveWatchlistStatus = {
  connection: "DISCONNECTED",
  dataQuality: "unavailable",
  activeSubscriptionsCount: 0,
  totalSubscribedCount: 0,
  totalItemsCount: 0,
  eventsReceivedCount: 0,
  eventsAppliedCount: 0,
  eventsRejectedCount: 0,
  lastObservationTime: null,
  lastEventTime: null,
  isTabVisible: true,
};

export function useWatchlistLive(
  activeWatchlist: WatchlistDetail | null
): UseWatchlistLiveReturn {
  const [liveQuotes, setLiveQuotes] = useState<Map<string, CanonicalLiveQuote>>(new Map());
  const [status, setStatus] = useState<LiveWatchlistStatus>(DEFAULT_STATUS);

  const controllerRef = useRef<WatchlistLiveController | null>(null);
  const activeId = activeWatchlist?.id || null;

  // 1. Controller lifecycle on active watchlist switch
  useEffect(() => {
    if (!activeWatchlist || !activeWatchlist.id) {
      if (controllerRef.current) {
        controllerRef.current.destroy();
        controllerRef.current = null;
      }
      setLiveQuotes(new Map());
      setStatus(DEFAULT_STATUS);
      return;
    }

    // Clean up previous controller
    if (controllerRef.current) {
      controllerRef.current.destroy();
      controllerRef.current = null;
    }

    const controller = new WatchlistLiveController({
      watchlistId: activeWatchlist.id,
      items: activeWatchlist.items || [],
      onQuoteBatch: (batch) => {
        setLiveQuotes((prev) => {
          const next = new Map(prev);
          for (const [key, quote] of batch.entries()) {
            next.set(key, quote);
          }
          return next;
        });
      },
      onStatusChange: (newStatus) => {
        setStatus(newStatus);
      },
      onResyncRequired: () => {
        // Can trigger a refresh if needed
      },
    });

    controllerRef.current = controller;
    controller.start();

    // Populate initial state from controller
    setLiveQuotes(new Map(controller.getCurrentQuotes()));
    setStatus(controller.getStatus());

    return () => {
      controller.destroy();
      if (controllerRef.current === controller) {
        controllerRef.current = null;
      }
    };
  }, [activeId]);

  // 2. Synchronize item membership updates without resetting controller
  useEffect(() => {
    if (controllerRef.current && activeWatchlist?.items) {
      controllerRef.current.updateItems(activeWatchlist.items);
    }
  }, [activeWatchlist?.items]);

  const reconnect = useCallback(async () => {
    if (controllerRef.current) {
      await controllerRef.current.reconnect();
    }
  }, []);

  const updateVisibleRange = useCallback((range: VisibleRowRange | null) => {
    if (controllerRef.current) {
      controllerRef.current.updateVisibleRange(range);
    }
  }, []);

  const getQuoteForInstrument = useCallback(
    (instrumentEntityId: string): CanonicalLiveQuote | null => {
      if (!instrumentEntityId) return null;
      return liveQuotes.get(instrumentEntityId.toLowerCase()) || null;
    },
    [liveQuotes]
  );

  return {
    liveQuotes,
    status,
    reconnect,
    updateVisibleRange,
    getQuoteForInstrument,
  };
}
