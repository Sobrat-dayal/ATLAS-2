"use client";

/**
 * Custom React hook for Stage 67 Live Chart Streaming.
 *
 * Manages live market quote subscription lifecycle, authoritative snapshot
 * bootstrap, chronological event ordering, and pause/resume controls.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChartConnectionState,
  ChartInstrumentMetadata,
  ChartLiveCapability,
  ChartMarketDataFreshness,
  LiveChartController,
  LiveChartEvent,
  LiveChartStatus,
  LiveQuoteDTO,
} from "@/lib/charts";

export interface UseLiveChartReturn {
  quote: LiveQuoteDTO | null;
  connectionState: ChartConnectionState;
  freshnessStatus: ChartMarketDataFreshness;
  delayStatus: string;
  liveCapability: ChartLiveCapability;
  isPaused: boolean;
  isFollowingLatest: boolean;
  provider: string;
  venue: string;
  togglePause: () => void;
  setFollowingLatest: (following: boolean) => void;
  reconnect: () => Promise<void>;
  dispatchLiveEvent: (event: LiveChartEvent) => boolean;
}

const DEFAULT_STATUS: LiveChartStatus = {
  connection: "DISCONNECTED",
  freshness: "UNKNOWN",
  delay: "UNKNOWN",
  capability: "HISTORICAL_ONLY",
  isPaused: false,
  provider: "canonical_feed",
  venue: "Primary Venue",
};

export function useLiveChart(
  instrument: ChartInstrumentMetadata | null
): UseLiveChartReturn {
  const [quote, setQuote] = useState<LiveQuoteDTO | null>(null);
  const [status, setStatus] = useState<LiveChartStatus>(DEFAULT_STATUS);

  const currentEntityId = instrument?.entity_id ?? null;
  const [prevEntityId, setPrevEntityId] = useState<string | null>(currentEntityId);
  if (currentEntityId !== prevEntityId) {
    setPrevEntityId(currentEntityId);
    setQuote(null);
    setStatus(DEFAULT_STATUS);
  }

  const [isFollowingLatest, setIsFollowingLatest] = useState<boolean>(true);
  const controllerRef = useRef<LiveChartController | null>(null);

  // Manage controller lifecycle on instrument change
  useEffect(() => {
    if (!instrument || !instrument.entity_id) {
      if (controllerRef.current) {
        controllerRef.current.destroy();
        controllerRef.current = null;
      }
      return;
    }

    // Tear down previous controller if instrument changed
    if (controllerRef.current) {
      controllerRef.current.destroy();
      controllerRef.current = null;
    }

    const controller = new LiveChartController({
      instrumentId: instrument.entity_id,
      symbol: instrument.display_symbol,
      allowsNegativePrice: instrument.allows_negative_price,
      onQuoteUpdate: (newQuote, newStatus) => {
        setQuote(newQuote);
        setStatus(newStatus);
      },
      onStatusChange: (newStatus) => {
        setStatus(newStatus);
      },
    });

    controllerRef.current = controller;
    controller.start();

    return () => {
      controller.destroy();
      if (controllerRef.current === controller) {
        controllerRef.current = null;
      }
    };
  }, [instrument]);

  const togglePause = useCallback(() => {
    if (!controllerRef.current) return;
    if (controllerRef.current.getIsPaused()) {
      controllerRef.current.resume();
    } else {
      controllerRef.current.pause();
    }
  }, []);

  const handleSetFollowingLatest = useCallback((following: boolean) => {
    setIsFollowingLatest(following);
    if (controllerRef.current) {
      controllerRef.current.setFollowingLatest(following);
    }
  }, []);

  const reconnect = useCallback(async () => {
    if (!controllerRef.current) return;
    await controllerRef.current.start();
  }, []);

  const dispatchLiveEvent = useCallback((event: LiveChartEvent): boolean => {
    if (!controllerRef.current) return false;
    return controllerRef.current.handleIncomingEvent(event);
  }, []);

  return {
    quote,
    connectionState: status.connection,
    freshnessStatus: status.freshness,
    delayStatus: status.delay,
    liveCapability: status.capability,
    isPaused: status.isPaused,
    isFollowingLatest,
    provider: status.provider,
    venue: status.venue,
    togglePause,
    setFollowingLatest: handleSetFollowingLatest,
    reconnect,
    dispatchLiveEvent,
  };
}
