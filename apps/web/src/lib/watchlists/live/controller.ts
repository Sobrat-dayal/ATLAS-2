/**
 * Watchlist Live Controller (Stage 78).
 *
 * Coordinates:
 * - Shared WebSocket connection integration (Stage 43)
 * - Viewport-aware subscription planning with bounded overscan
 * - Background tab suspension & resumption (document.visibilityState)
 * - Canonical event validation, ordering, and deduplication
 * - Snapshot-and-stream race reconciliation
 * - Coalesced UI rendering updates (batched emissions)
 * - Financial quote semantics (Last vs Bid vs Ask vs Mid vs NAV)
 * - Accessible directional movement cues (up / down / flat)
 * - Safe lifecycle management and cleanup
 */

import {
  RealtimeConnectionState,
  RealtimeSubscriptionState,
  LiveEventMessageOut,
  QuoteSnapshotMessage,
} from "@/lib/realtime/types";
import { SharedWebSocketClient, sharedWebSocketClient } from "@/lib/realtime/client";
import { WatchlistItem, ChangeDirection, FreshnessStatus, DeliveryDelayStatus } from "../types";
import {
  CanonicalLiveQuote,
  IncomingQuoteEvent,
  LiveDataQuality,
  RawMarketQuotePayload,
  VisibleRowRange,
  WatchlistLiveStatus,
} from "./types";
import { validateCanonicalQuoteEvent } from "./event-validation";
import { EventOrderingTracker } from "./event-ordering";
import { SnapshotStreamReconciler } from "./reconciliation";
import { calculateDesiredSubscriptionPlan } from "./subscription-plan";
import { RenderBatcher } from "./render-batching";

export interface WatchlistLiveControllerOptions {
  watchlistId: string;
  items: WatchlistItem[];
  wsClient?: SharedWebSocketClient;
  coalesceIntervalMs?: number;
  overscan?: number;
  maxBudget?: number;
  allowsNegativePriceMap?: Record<string, boolean>;
  onQuoteBatch?: (quotes: Map<string, CanonicalLiveQuote>) => void;
  onStatusChange?: (status: WatchlistLiveStatus) => void;
  onResyncRequired?: () => void;
}

export class WatchlistLiveController {
  private readonly watchlistId: string;
  private readonly consumerId: string;
  private readonly wsClient: SharedWebSocketClient;
  private readonly orderingTracker: EventOrderingTracker;
  private readonly reconciler: SnapshotStreamReconciler;
  private readonly renderBatcher: RenderBatcher;

  private items: WatchlistItem[] = [];
  private visibleRange: VisibleRowRange | null = null;
  private allowsNegativePriceMap: Record<string, boolean> = {};

  private currentQuotes: Map<string, CanonicalLiveQuote> = new Map();
  private connectionState: RealtimeConnectionState = "DISCONNECTED";
  private subscriptionStates: Map<string, { state: RealtimeSubscriptionState; reason?: string }> =
    new Map();

  private isTabVisible: boolean = true;
  private isDestroyed: boolean = false;
  private scrollDebounceTimer: ReturnType<typeof setTimeout> | null = null;

  // Metrics
  private eventsReceivedCount: number = 0;
  private eventsAppliedCount: number = 0;
  private eventsRejectedCount: number = 0;
  private lastObservationTime: string | null = null;
  private lastEventTime: string | null = null;

  private readonly onQuoteBatch?: (quotes: Map<string, CanonicalLiveQuote>) => void;
  private readonly onStatusChange?: (status: WatchlistLiveStatus) => void;
  private readonly onResyncRequired?: () => void;

  private unsubscribeWsConnection: (() => void) | null = null;
  private unsubscribeResync: (() => void) | null = null;
  private visibilityListener: (() => void) | null = null;

  constructor(options: WatchlistLiveControllerOptions) {
    this.watchlistId = options.watchlistId;
    this.consumerId = `watchlist_view_${options.watchlistId}`;
    this.items = options.items || [];
    this.allowsNegativePriceMap = options.allowsNegativePriceMap || {};
    this.wsClient = options.wsClient || sharedWebSocketClient;

    this.onQuoteBatch = options.onQuoteBatch;
    this.onStatusChange = options.onStatusChange;
    this.onResyncRequired = options.onResyncRequired;

    this.orderingTracker = new EventOrderingTracker(500);
    this.reconciler = new SnapshotStreamReconciler({ maxBufferSize: 100 });

    this.renderBatcher = new RenderBatcher({
      batchIntervalMs: options.coalesceIntervalMs ?? 80,
      onFlush: (batch) => {
        if (this.onQuoteBatch) {
          this.onQuoteBatch(batch);
        }
        this.emitStatus();
      },
    });

    // Populate initial quote state from items
    this.initializeQuotesFromItems(this.items);
  }

  /**
   * Starts the controller, hooks into shared WebSocket, and sets up visibility listeners.
   */
  public start(): void {
    if (this.isDestroyed) return;

    // 1. Connection state tracking
    this.unsubscribeWsConnection = this.wsClient.onConnectionStateChange((state) => {
      this.connectionState = state;
      this.emitStatus();
    });

    // 2. Resync listener
    this.unsubscribeResync = this.wsClient.onSystemResync((reason) => {
      console.warn(`System resync requested for watchlist ${this.watchlistId}: ${reason}`);
      if (this.onResyncRequired) {
        this.onResyncRequired();
      }
    });

    // 3. Tab visibility listener
    if (typeof document !== "undefined") {
      this.isTabVisible = document.visibilityState === "visible";
      const onVisChange = () => {
        this.isTabVisible = document.visibilityState === "visible";
        this.syncSubscriptions();
        this.emitStatus();
      };
      document.addEventListener("visibilitychange", onVisChange);
      this.visibilityListener = () => {
        document.removeEventListener("visibilitychange", onVisChange);
      };
    }

    // 4. Initial subscription synchronization
    this.syncSubscriptions();
    this.emitStatus();
  }

  /**
   * Initializes canonical quote state from existing membership item snapshots.
   */
  public initializeQuotesFromItems(items: WatchlistItem[]): void {
    this.items = items;
    for (const item of items) {
      if (!item.instrument_entity_id) continue;
      const key = item.instrument_entity_id.toLowerCase();

      if (!this.currentQuotes.has(key)) {
        this.currentQuotes.set(key, {
          instrument_entity_id: item.instrument_entity_id,
          symbol: item.symbol,
          market_series_id: item.market_series_id,
          quote_measure: item.quote_measure || "Last",
          last_price: item.last_price,
          bid_price: item.bid_price,
          ask_price: item.ask_price,
          previous_close: null,
          absolute_change: item.absolute_change,
          percentage_change: item.percentage_change,
          change_direction: item.change_direction || "flat",
          source_timestamp: item.source_timestamp,
          received_at: null,
          freshness_status: item.freshness_status,
          delivery_delay_status: item.delivery_delay_status,
          delay_seconds: item.delay_seconds,
          provider: item.provider,
          venue: item.venue,
          quote_currency: item.quote_currency,
          quote_unit: item.quote_unit,
        });

        if (item.source_timestamp) {
          this.orderingTracker.updateSnapshotWatermark(
            item.instrument_entity_id,
            item.source_timestamp
          );
        }
      }
    }

    if (items.length > 0) {
      this.reconciler.markSnapshotLoaded();
    }
  }

  /**
   * Updates visible viewport range and debounces subscription plan reconciliation.
   */
  public updateVisibleRange(range: VisibleRowRange | null): void {
    this.visibleRange = range;
    if (this.scrollDebounceTimer) {
      clearTimeout(this.scrollDebounceTimer);
    }
    // Debounce fast scrolling (150ms) to avoid subscription storms
    this.scrollDebounceTimer = setTimeout(() => {
      this.scrollDebounceTimer = null;
      this.syncSubscriptions();
    }, 150);
  }

  /**
   * Updates membership items list (e.g. after adding, removing, or reordering).
   */
  public updateItems(items: WatchlistItem[]): void {
    this.items = items;
    this.initializeQuotesFromItems(items);
    this.syncSubscriptions();
  }

  /**
   * Synchronizes desired series subscriptions with the shared WebSocket manager.
   */
  private syncSubscriptions(): void {
    if (this.isDestroyed) return;

    const plan = calculateDesiredSubscriptionPlan(this.items, this.visibleRange, {
      isTabVisible: this.isTabVisible,
    });

    this.wsClient.reconcileConsumerSubscriptions(this.consumerId, plan, {
      onSnapshot: (snap) => this.handleIncomingSnapshot(snap),
      onLiveEvent: (event) => this.handleIncomingLiveEvent(event),
      onStatusChange: () => {
        // Track subscription status
        this.emitStatus();
      },
    });
  }

  /**
   * Handles incoming market.quote.snapshot message.
   */
  public handleIncomingSnapshot(msg: QuoteSnapshotMessage): void {
    if (this.isDestroyed || !msg.series?.instrument_entity_id) return;
    const entityId = msg.series.instrument_entity_id.toLowerCase();
    const snap = msg.snapshot as RawMarketQuotePayload | null;
    if (!snap) return;

    const sourceTs = snap.as_of || snap.source_timestamp || null;

    // Reconcile with snapshot stream reconciler
    const { applySnapshot } = this.reconciler.reconcileOnSnapshotLoaded(
      sourceTs,
      entityId,
      this.orderingTracker
    );

    if (applySnapshot) {
      this.applyQuoteData(entityId, snap);
    }
  }

  /**
   * Handles incoming live.event message (market.quote.updated).
   */
  public handleIncomingLiveEvent(msg: LiveEventMessageOut): boolean {
    if (this.isDestroyed) return false;
    this.eventsReceivedCount++;
    this.lastEventTime = new Date().toISOString();

    const rawEvent = (msg.event || msg) as IncomingQuoteEvent;
    const legacyInstId = (rawEvent as IncomingQuoteEvent & { instrument_id?: string }).instrument_id;
    const entityId = (rawEvent.instrument_entity_id || legacyInstId || "").toLowerCase();

    // 1. Validate event schema & data
    const allowsNegative = !!this.allowsNegativePriceMap[entityId];
    const validation = validateCanonicalQuoteEvent(rawEvent, {
      allowsNegativePrice: allowsNegative,
    });

    if (!validation.accepted || !validation.sanitizedQuote || !validation.instrumentEntityId) {
      this.eventsRejectedCount++;
      return false;
    }

    // 2. Buffer if snapshot pending
    if (!this.reconciler.getIsSnapshotLoaded()) {
      const buffered = this.reconciler.bufferEvent(rawEvent);
      if (!buffered && this.onResyncRequired) {
        this.onResyncRequired();
      }
      return true;
    }

    // 3. Chronological source ordering & deduplication
    const quotePayload = validation.sanitizedQuote;
    const sourceTs =
      validation.sourceTimestamp || quotePayload.as_of || quotePayload.source_timestamp || "";

    const ordering = this.orderingTracker.evaluate(
      validation.instrumentEntityId,
      validation.eventId,
      sourceTs,
      quotePayload.sequence,
      quotePayload.source_epoch
    );

    if (!ordering.accepted) {
      this.eventsRejectedCount++;
      return false;
    }

    // 4. Apply qualified quote update
    this.eventsAppliedCount++;
    this.lastObservationTime = sourceTs;
    this.applyQuoteData(validation.instrumentEntityId, quotePayload);

    return true;
  }

  /**
   * Applies validated quote payload to the canonical quote state map and enqueues render batch.
   */
  private applyQuoteData(
    entityId: string,
    raw: RawMarketQuotePayload
  ): void {
    const existing = this.currentQuotes.get(entityId);
    const item = this.items.find((i) => i.instrument_entity_id?.toLowerCase() === entityId);

    const assetClass = item?.asset_class || "equity";
    let quoteMeasure = existing?.quote_measure || item?.quote_measure || "Last";

    if (assetClass === "fund") quoteMeasure = "NAV";
    else if (assetClass === "bond") quoteMeasure = "Clean Price";
    else if (assetClass === "currency" || assetClass === "fx") quoteMeasure = "Mid";

    const lastPrice =
      raw.last_price !== undefined && raw.last_price !== null
        ? String(raw.last_price)
        : existing?.last_price ?? item?.last_price ?? null;

    const bidPrice =
      raw.bid_price !== undefined && raw.bid_price !== null
        ? String(raw.bid_price)
        : existing?.bid_price ?? item?.bid_price ?? null;

    const askPrice =
      raw.ask_price !== undefined && raw.ask_price !== null
        ? String(raw.ask_price)
        : existing?.ask_price ?? item?.ask_price ?? null;

    // Reference close & change calculation
    const prevClose =
      raw.previous_close !== undefined && raw.previous_close !== null
        ? String(raw.previous_close)
        : existing?.previous_close ?? null;

    let absoluteChange = existing?.absolute_change ?? item?.absolute_change ?? null;
    let percentageChange = existing?.percentage_change ?? item?.percentage_change ?? null;
    let changeDirection: ChangeDirection =
      existing?.change_direction ?? item?.change_direction ?? "flat";

    if (prevClose !== null && lastPrice !== null) {
      try {
        const prev = Number(prevClose);
        const curr = Number(lastPrice);
        if (Number.isFinite(prev) && Number.isFinite(curr)) {
          const diff = curr - prev;
          absoluteChange = diff >= 0 ? `+${diff.toFixed(2)}` : diff.toFixed(2);
          if (prev !== 0) {
            const pct = (diff / prev) * 100;
            percentageChange = pct >= 0 ? `+${pct.toFixed(2)}%` : `${pct.toFixed(2)}%`;
          }
          if (diff > 0) changeDirection = "up";
          else if (diff < 0) changeDirection = "down";
          else changeDirection = "flat";
        }
      } catch {}
    }

    // Determine movement cue (up / down / flat) compared to previous displayed price
    let movementCue: "up" | "down" | "flat" | null = null;
    if (existing?.last_price !== null && lastPrice !== null && existing?.last_price !== undefined) {
      const oldVal = Number(existing.last_price);
      const newVal = Number(lastPrice);
      if (Number.isFinite(oldVal) && Number.isFinite(newVal)) {
        if (newVal > oldVal) movementCue = "up";
        else if (newVal < oldVal) movementCue = "down";
        else movementCue = "flat";
      }
    }

    const updatedQuote: CanonicalLiveQuote = {
      instrument_entity_id: item?.instrument_entity_id || entityId,
      symbol: item?.symbol || existing?.symbol || "",
      market_series_id: item?.market_series_id || existing?.market_series_id || "",
      quote_measure: quoteMeasure,
      last_price: lastPrice,
      bid_price: bidPrice,
      ask_price: askPrice,
      previous_close: prevClose,
      absolute_change: absoluteChange,
      percentage_change: percentageChange,
      change_direction: changeDirection,
      source_timestamp: raw.as_of || raw.source_timestamp || existing?.source_timestamp || null,
      received_at: raw.received_at || new Date().toISOString(),
      freshness_status: (raw.freshness_status as FreshnessStatus) || "fresh",
      delivery_delay_status:
        (raw.delay_status as DeliveryDelayStatus) || item?.delivery_delay_status || "realtime",
      delay_seconds: item?.delay_seconds ?? null,
      provider: raw.provider || item?.provider || existing?.provider || null,
      venue: raw.venue_id || item?.venue || existing?.venue || null,
      quote_currency: item?.quote_currency || existing?.quote_currency || null,
      quote_unit: item?.quote_unit || existing?.quote_unit || null,
      sequence: raw.sequence || undefined,
      source_epoch: raw.source_epoch || undefined,
      last_movement_cue: movementCue,
      movement_timestamp: movementCue ? Date.now() : existing?.movement_timestamp,
    };

    this.currentQuotes.set(entityId, updatedQuote);
    this.renderBatcher.enqueue(updatedQuote);
  }

  public getStatus(): WatchlistLiveStatus {
    // Determine aggregate data quality
    let realtimeCount = 0;
    let delayedCount = 0;
    let staleCount = 0;

    for (const q of this.currentQuotes.values()) {
      if (q.freshness_status === "stale") staleCount++;
      else if (q.delivery_delay_status === "delayed") delayedCount++;
      else if (q.delivery_delay_status === "realtime") realtimeCount++;
    }

    let dataQuality: LiveDataQuality = "realtime";
    if (this.currentQuotes.size === 0) {
      dataQuality = "unavailable";
    } else if (staleCount > 0 && staleCount === this.currentQuotes.size) {
      dataQuality = "stale";
    } else if (delayedCount > 0 && realtimeCount > 0) {
      dataQuality = "mixed";
    } else if (delayedCount > 0) {
      dataQuality = "delayed";
    }

    const activeCount = this.wsClient.getActiveSubscriptionCount();

    return {
      connection: this.connectionState,
      dataQuality,
      activeSubscriptionsCount: activeCount,
      totalSubscribedCount: this.currentQuotes.size,
      totalItemsCount: this.items.length,
      eventsReceivedCount: this.eventsReceivedCount,
      eventsAppliedCount: this.eventsAppliedCount,
      eventsRejectedCount: this.eventsRejectedCount,
      lastObservationTime: this.lastObservationTime,
      lastEventTime: this.lastEventTime,
      isTabVisible: this.isTabVisible,
    };
  }

  public getCurrentQuotes(): Map<string, CanonicalLiveQuote> {
    return this.currentQuotes;
  }

  private emitStatus(): void {
    if (this.onStatusChange) {
      this.onStatusChange(this.getStatus());
    }
  }

  /**
   * Reconnects live streaming if disconnected.
   */
  public async reconnect(): Promise<void> {
    await this.wsClient.connect();
    this.syncSubscriptions();
  }

  /**
   * Destroys controller and tears down all consumer references.
   */
  public destroy(): void {
    this.isDestroyed = true;

    if (this.scrollDebounceTimer) {
      clearTimeout(this.scrollDebounceTimer);
      this.scrollDebounceTimer = null;
    }

    if (this.unsubscribeWsConnection) {
      this.unsubscribeWsConnection();
      this.unsubscribeWsConnection = null;
    }

    if (this.unsubscribeResync) {
      this.unsubscribeResync();
      this.unsubscribeResync = null;
    }

    if (this.visibilityListener) {
      this.visibilityListener();
      this.visibilityListener = null;
    }

    this.renderBatcher.destroy();
    this.orderingTracker.clear();
    this.reconciler.clear();

    // Release all subscriptions for this consumer
    this.wsClient.reconcileConsumerSubscriptions(this.consumerId, [], {
      onSnapshot: () => {},
      onLiveEvent: () => {},
    });

    this.currentQuotes.clear();
  }
}
