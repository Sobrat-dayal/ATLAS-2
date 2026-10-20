/**
 * TypeScript definitions for Live Watchlist Updates V1 (Stage 78).
 */

import { QuoteSubscriptionKeyDTO, RealtimeConnectionState } from "@/lib/realtime/types";
import { FreshnessStatus, DeliveryDelayStatus, ChangeDirection } from "../types";

export type { QuoteSubscriptionKeyDTO, RealtimeConnectionState };

export type LiveDataQuality = "realtime" | "delayed" | "stale" | "unavailable" | "mixed";

export interface CanonicalLiveQuote {
  instrument_entity_id: string;
  symbol: string;
  market_series_id: string;
  quote_measure: string; // "Last" | "Bid" | "Ask" | "Mid" | "NAV" | "Clean Price" | "Fixing" | "Settlement"
  last_price: string | null;
  bid_price: string | null;
  ask_price: string | null;
  previous_close: string | null;
  absolute_change: string | null;
  percentage_change: string | null;
  change_direction: ChangeDirection;
  source_timestamp: string | null;
  received_at: string | null;
  freshness_status: FreshnessStatus;
  delivery_delay_status: DeliveryDelayStatus;
  delay_seconds: number | null;
  provider: string | null;
  venue: string | null;
  quote_currency: string | null;
  quote_unit: string | null;
  sequence?: string;
  source_epoch?: string;
  last_movement_cue?: "up" | "down" | "flat" | null;
  movement_timestamp?: number;
  is_denied?: boolean;
  denial_reason?: string;
}

export interface VisibleRowRange {
  startIndex: number;
  endIndex: number;
}

export interface WatchlistLiveStatus {
  connection: RealtimeConnectionState;
  dataQuality: LiveDataQuality;
  activeSubscriptionsCount: number;
  totalSubscribedCount: number;
  totalItemsCount: number;
  eventsReceivedCount: number;
  eventsAppliedCount: number;
  eventsRejectedCount: number;
  lastObservationTime: string | null;
  lastEventTime: string | null;
  isTabVisible: boolean;
}

export type LiveWatchlistStatus = WatchlistLiveStatus;

export interface RawMarketQuotePayload {
  last_price?: string | number | null;
  price?: string | number | null;
  bid_price?: string | number | null;
  ask_price?: string | number | null;
  bid_size?: string | number | null;
  ask_size?: string | number | null;
  previous_close?: string | number | null;
  as_of?: string | null;
  source_timestamp?: string | null;
  received_at?: string | null;
  venue_id?: string | null;
  session?: string | null;
  sequence?: string | null;
  source_epoch?: string | null;
  provider?: string | null;
  freshness_status?: string | null;
  delay_status?: string | null;
  [key: string]: unknown;
}

export interface IncomingQuoteEvent {
  schema_version?: number;
  event_id?: string;
  event_type?: string;
  emitted_at?: string;
  instrument_entity_id?: string;
  provider_key?: string;
  payload?: {
    quote?: RawMarketQuotePayload;
    received_at?: string;
    cached_at?: string;
    source_timestamp?: string;
    sequence?: string;
    source_epoch?: string;
    variant?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}
