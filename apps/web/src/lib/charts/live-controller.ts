/**
 * Live Chart Streaming Controller for ATLAS Charts V1 (Stage 67).
 *
 * Orchestrates:
 * - Canonical instrument subscription lifecycle
 * - Authoritative initial snapshot bootstrap
 * - Bounded bootstrap event queue (max 100 items)
 * - Snapshot-to-event race reconciliation
 * - Source-time chronological ordering (rejecting stale and duplicate events)
 * - Strict financial data integrity:
 *   - Quote snapshot is NOT a complete trade feed.
 *   - Bid/Ask are NOT Last.
 *   - Indicative midpoint is NEVER presented as executed Last trade.
 *   - Quote count is NEVER calculated as Volume.
 *   - Valid negative futures prices supported (e.g. CLZ26).
 *   - Historical OHLC candles are NEVER mutated by quote updates.
 * - Coalesced rendering emissions (default 100ms throttle) to prevent UI thread lock
 * - Pause / Resume live streaming controls
 * - Disconnect & Reconnect recovery
 * - Rapid instrument switching without stale data leaks
 * - Strict cleanup on unmount
 */

import {
  ChartConnectionState,
  ChartLiveCapability,
  ChartLiveStateResponse,
  ChartMarketDataFreshness,
  LiveChartEvent,
  LiveQuoteDTO,
} from "./types";
import { fetchChartLiveState } from "./api";

export interface LiveChartStatus {
  connection: ChartConnectionState;
  freshness: ChartMarketDataFreshness;
  delay: string;
  capability: ChartLiveCapability;
  isPaused: boolean;
  provider: string;
  venue: string;
}

export interface LiveChartControllerOptions {
  instrumentId: string;
  symbol: string;
  allowsNegativePrice?: boolean;
  coalesceIntervalMs?: number;
  maxBufferSize?: number;
  initialStateFetcher?: (params: {
    instrumentId?: string;
    symbol?: string;
  }) => Promise<ChartLiveStateResponse>;
  onQuoteUpdate?: (quote: LiveQuoteDTO, status: LiveChartStatus) => void;
  onStatusChange?: (status: LiveChartStatus) => void;
  onError?: (error: string) => void;
}

export class LiveChartController {
  private readonly instrumentId: string;
  private readonly symbol: string;
  private readonly allowsNegativePrice: boolean;
  private readonly coalesceIntervalMs: number;
  private readonly maxBufferSize: number;
  private readonly initialStateFetcher: (params: {
    instrumentId?: string;
    symbol?: string;
  }) => Promise<ChartLiveStateResponse>;

  private readonly onQuoteUpdate?: (quote: LiveQuoteDTO, status: LiveChartStatus) => void;
  private readonly onStatusChange?: (status: LiveChartStatus) => void;
  private readonly onError?: (error: string) => void;

  private currentQuote: LiveQuoteDTO | null = null;
  private connection: ChartConnectionState = "DISCONNECTED";
  private freshness: ChartMarketDataFreshness = "UNKNOWN";
  private delay: string = "UNKNOWN";
  private capability: ChartLiveCapability = "HISTORICAL_ONLY";
  private isPaused: boolean = false;
  private isFollowingLatest: boolean = true;
  private provider: string = "canonical_feed";
  private venue: string = "Primary Venue";

  private bootstrapBuffer: LiveChartEvent[] = [];
  private isBootstrapped: boolean = false;
  private isDestroyed: boolean = false;
  private abortController: AbortController | null = null;

  private pendingCoalescedQuote: LiveQuoteDTO | null = null;
  private coalesceTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(options: LiveChartControllerOptions) {
    this.instrumentId = options.instrumentId;
    this.symbol = options.symbol;
    this.allowsNegativePrice = !!options.allowsNegativePrice;
    this.coalesceIntervalMs = options.coalesceIntervalMs ?? 100;
    this.maxBufferSize = options.maxBufferSize ?? 100;
    this.initialStateFetcher = options.initialStateFetcher ?? fetchChartLiveState;
    this.onQuoteUpdate = options.onQuoteUpdate;
    this.onStatusChange = options.onStatusChange;
    this.onError = options.onError;
  }

  public getStatus(): LiveChartStatus {
    return {
      connection: this.connection,
      freshness: this.freshness,
      delay: this.delay,
      capability: this.capability,
      isPaused: this.isPaused,
      provider: this.provider,
      venue: this.venue,
    };
  }

  public getCurrentQuote(): LiveQuoteDTO | null {
    return this.currentQuote;
  }

  public getIsPaused(): boolean {
    return this.isPaused;
  }

  public getIsFollowingLatest(): boolean {
    return this.isFollowingLatest;
  }

  public setFollowingLatest(following: boolean): void {
    this.isFollowingLatest = following;
  }

  /**
   * Initializes the subscription and fetches the initial authoritative quote snapshot.
   */
  public async start(): Promise<void> {
    if (this.isDestroyed) return;

    this.connection = "CONNECTING";
    this.emitStatus();

    this.abortController = new AbortController();

    try {
      const response = await this.initialStateFetcher({
        instrumentId: this.instrumentId,
        symbol: this.symbol,
      });

      if (this.isDestroyed) return;

      // Ensure snapshot matches current instrument
      if (
        response.instrument_entity_id &&
        response.instrument_entity_id.toLowerCase() !== this.instrumentId.toLowerCase()
      ) {
        return; // Stale async response from previous instrument switch
      }

      this.provider = response.provider || "canonical_feed";
      this.venue = response.market_or_venue || "Primary Venue";
      this.delay = response.delay_status || "REALTIME";
      this.freshness = (response.freshness_status as ChartMarketDataFreshness) || "LIVE";
      this.capability =
        (response.live_capability as ChartLiveCapability) || "LIVE_PRICE_AVAILABLE";

      if (response.quote) {
        this.currentQuote = response.quote;
      }

      this.connection = "CONNECTED";
      this.isBootstrapped = true;

      // Reconcile any events received while snapshot was in flight
      this.reconcileBootstrapBuffer();

      this.emitStatus();

      if (this.currentQuote && !this.isPaused) {
        this.scheduleQuoteEmission(this.currentQuote);
      }
    } catch (err: unknown) {
      if (this.isDestroyed) return;
      this.connection = "ERROR";
      this.freshness = "UNAVAILABLE";
      this.emitStatus();
      if (this.onError) {
        const msg = err instanceof Error ? err.message : String(err);
        this.onError(msg || "Failed to initialize live chart stream.");
      }
    }
  }

  /**
   * Dispatches an incoming typed event from WebSocket transport.
   */
  public handleIncomingEvent(event: LiveChartEvent): boolean {
    if (this.isDestroyed) return false;

    // 1. Buffer events while initial HTTP snapshot is in-flight
    if (!this.isBootstrapped) {
      if (this.bootstrapBuffer.length >= this.maxBufferSize) {
        // Bounded bootstrap queue overflow: drop buffer and request fresh state
        this.bootstrapBuffer = [];
        this.freshness = "UNKNOWN";
        this.emitStatus();
        this.start();
        return false;
      }
      this.bootstrapBuffer.push(event);
      return true;
    }

    // 2. Validate and reconcile event
    const validation = this.validateAndReconcileEvent(event);
    if (!validation.accepted || !validation.reconciledQuote) {
      return false;
    }

    this.currentQuote = validation.reconciledQuote;
    this.connection = "CONNECTED";
    this.freshness = "LIVE";

    // 3. Emit if not paused
    if (!this.isPaused) {
      this.scheduleQuoteEmission(this.currentQuote);
    }

    return true;
  }

  /**
   * Pauses live chart updates to the visible canvas.
   */
  public pause(): void {
    if (this.isPaused) return;
    this.isPaused = true;
    this.emitStatus();
  }

  /**
   * Resumes live chart streaming and reconciles with authoritative latest state.
   */
  public async resume(): Promise<void> {
    if (!this.isPaused) return;
    this.isPaused = false;
    this.emitStatus();

    // Reconcile fresh state on resume to ensure no missed market state
    try {
      const response = await this.initialStateFetcher({
        instrumentId: this.instrumentId,
        symbol: this.symbol,
      });

      if (this.isDestroyed || this.isPaused) return;

      if (response.quote) {
        const snapDt = response.quote.as_of ? new Date(response.quote.as_of).getTime() : 0;
        const curDt = this.currentQuote?.as_of ? new Date(this.currentQuote.as_of).getTime() : 0;

        if (snapDt >= curDt) {
          this.currentQuote = response.quote;
        }
      }

      this.connection = "CONNECTED";
      this.freshness = (response.freshness_status as ChartMarketDataFreshness) || "LIVE";
      this.emitStatus();

      if (this.currentQuote) {
        this.scheduleQuoteEmission(this.currentQuote);
      }
    } catch {
      // Keep existing state if fetch fails
    }
  }

  /**
   * Validates incoming event and reconciles with current quote state.
   */
  public validateAndReconcileEvent(event: LiveChartEvent): {
    accepted: boolean;
    reason: string;
    reconciledQuote: LiveQuoteDTO | null;
  } {
    // A. Schema version check
    if (event.schema_version !== undefined && event.schema_version !== 1) {
      return { accepted: false, reason: "UNSUPPORTED_SCHEMA_VERSION", reconciledQuote: null };
    }

    // B. Instrument UUID match
    const eventEntityId = event.instrument_entity_id || event.instrument_id;
    if (!eventEntityId) {
      return { accepted: false, reason: "MISSING_INSTRUMENT_ENTITY_ID", reconciledQuote: null };
    }
    if (eventEntityId.toLowerCase() !== this.instrumentId.toLowerCase()) {
      return {
        accepted: false,
        reason: `INSTRUMENT_MISMATCH: expected ${this.instrumentId}, got ${eventEntityId}`,
        reconciledQuote: null,
      };
    }

    // C. Extract quote data
    const payload = event.payload || event;
    const quoteData: Partial<LiveQuoteDTO> = payload.quote || payload;

    const asOfStr = quoteData.as_of || event.source_timestamp || new Date().toISOString();
    const incomingDt = new Date(asOfStr).getTime();
    if (isNaN(incomingDt)) {
      return { accepted: false, reason: "INVALID_TIMESTAMP_FORMAT", reconciledQuote: null };
    }

    // D. Chronological source-time ordering (stale/duplicate rejection)
    if (this.currentQuote && this.currentQuote.as_of) {
      const currentDt = new Date(this.currentQuote.as_of).getTime();
      if (incomingDt <= currentDt) {
        return {
          accepted: false,
          reason: `STALE_OR_DUPLICATE_EVENT: incoming ${asOfStr} <= current ${this.currentQuote.as_of}`,
          reconciledQuote: null,
        };
      }
    }

    // E. Price parsing and decimal validation
    const rawQuote = quoteData as Record<string, unknown>;
    const bidVal = this.parsePrice(quoteData.bid_price ?? rawQuote.bid);
    const askVal = this.parsePrice(quoteData.ask_price ?? rawQuote.ask);
    const lastVal = this.parsePrice(quoteData.last_price ?? rawQuote.last);
    const lastSizeVal = this.parsePrice(quoteData.last_size ?? rawQuote.size);

    // F. Negative price checks
    for (const [name, val] of [
      ["bid", bidVal],
      ["ask", askVal],
      ["last", lastVal],
    ] as const) {
      if (val !== null && val < 0 && !this.allowsNegativePrice) {
        return {
          accepted: false,
          reason: `NEGATIVE_PRICE_REJECTED: ${name}=${val} not allowed for this asset class`,
          reconciledQuote: null,
        };
      }
    }

    // G. Last trade qualification
    // Bid/ask are NOT Last. Midpoint is NOT an executed trade.
    const hasGenuineLast = lastVal !== null;
    const isMidpoint = !!quoteData.is_midpoint;

    const finalLast = hasGenuineLast
      ? lastVal
      : this.currentQuote?.last_price ?? null;

    const finalHasLast = hasGenuineLast || (this.currentQuote?.has_genuine_last ?? false);

    const reconciled: LiveQuoteDTO = {
      bid_price: bidVal !== null ? bidVal : (this.currentQuote?.bid_price ?? null),
      ask_price: askVal !== null ? askVal : (this.currentQuote?.ask_price ?? null),
      bid_size: this.parsePrice(quoteData.bid_size) ?? null,
      ask_size: this.parsePrice(quoteData.ask_size) ?? null,
      last_price: finalLast,
      last_size: lastSizeVal !== null ? lastSizeVal : (this.currentQuote?.last_size ?? null),
      as_of: asOfStr,
      is_midpoint: isMidpoint,
      has_genuine_last: finalHasLast,
    };

    return { accepted: true, reason: "ACCEPTED", reconciledQuote: reconciled };
  }

  /**
   * Replays events buffered while the initial HTTP snapshot was fetching.
   */
  private reconcileBootstrapBuffer(): void {
    if (this.bootstrapBuffer.length === 0) return;

    const snapshotTs = this.currentQuote?.as_of
      ? new Date(this.currentQuote.as_of).getTime()
      : 0;

    for (const event of this.bootstrapBuffer) {
      const payload = (event.payload || event) as Record<string, unknown>;
      const q = (payload.quote || payload) as Record<string, unknown>;
      const asOfStr =
        typeof q.as_of === "string"
          ? q.as_of
          : typeof event.source_timestamp === "string"
            ? event.source_timestamp
            : undefined;
      const eventTs = asOfStr ? new Date(asOfStr).getTime() : 0;

      // Only apply buffered events strictly newer than snapshot
      if (eventTs > snapshotTs) {
        const val = this.validateAndReconcileEvent(event);
        if (val.accepted && val.reconciledQuote) {
          this.currentQuote = val.reconciledQuote;
        }
      }
    }

    this.bootstrapBuffer = [];
  }

  /**
   * Coalesces high-frequency quotes into a single emission every coalesceIntervalMs.
   */
  private scheduleQuoteEmission(quote: LiveQuoteDTO): void {
    this.pendingCoalescedQuote = quote;

    if (!this.coalesceTimer) {
      this.coalesceTimer = setTimeout(() => {
        this.coalesceTimer = null;
        if (this.pendingCoalescedQuote && !this.isDestroyed && !this.isPaused) {
          if (this.onQuoteUpdate) {
            this.onQuoteUpdate(this.pendingCoalescedQuote, this.getStatus());
          }
        }
      }, this.coalesceIntervalMs);
    }
  }

  private emitStatus(): void {
    if (this.isDestroyed) return;
    if (this.onStatusChange) {
      this.onStatusChange(this.getStatus());
    }
  }

  private parsePrice(val: unknown): number | null {
    if (val === null || val === undefined || val === "") return null;
    const str = String(val).trim().toLowerCase();
    if (
      str === "nan" ||
      str === "inf" ||
      str === "-inf" ||
      str === "infinity" ||
      str === "-infinity"
    ) {
      return null;
    }
    const num = Number(val);
    return isNaN(num) || !isFinite(num) ? null : num;
  }

  /**
   * Completely tears down timers, in-flight requests, and subscriptions.
   */
  public destroy(): void {
    this.isDestroyed = true;
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
    if (this.coalesceTimer) {
      clearTimeout(this.coalesceTimer);
      this.coalesceTimer = null;
    }
    this.bootstrapBuffer = [];
    this.connection = "DISCONNECTED";
  }
}
