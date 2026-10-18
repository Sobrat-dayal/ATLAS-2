/**
 * Centralized Historical Data Query Cache for Multi-Chart Workspaces (Stage 72).
 *
 * Implements:
 * - Shared, deduplicated caching of canonical historical OHLCV queries
 * - In-flight Promise deduplication (coalescing simultaneous panel requests)
 * - Strict query key isolation incorporating:
 *   - instrument_entity_id / canonical symbol
 *   - interval (1m, 5m, 1h, 1D, etc.)
 *   - requested range (start, end, before, limit)
 * - Immutable data returns (preventing cross-panel array mutation)
 * - Bounded LRU memory eviction (capacity limit from WORKSPACE_RESOURCE_BUDGET)
 * - Cache invalidation and per-instrument eviction
 */

import { ChartHistoryResponse } from "../types";
import { FetchChartHistoryParams, fetchChartHistory } from "../api";
import { WORKSPACE_RESOURCE_BUDGET } from "./types";

export interface CacheEntry {
  data: ChartHistoryResponse;
  timestamp: number;
}

export class ChartQueryCache {
  private static instance: ChartQueryCache;

  private cache: Map<string, CacheEntry> = new Map();
  private inFlightRequests: Map<string, Promise<ChartHistoryResponse>> = new Map();
  private readonly capacity: number;
  private readonly ttlMs: number;

  constructor(capacity = WORKSPACE_RESOURCE_BUDGET.queryCacheCapacity, ttlMs = 60_000) {
    this.capacity = capacity;
    this.ttlMs = ttlMs;
  }

  public static getInstance(): ChartQueryCache {
    if (!ChartQueryCache.instance) {
      ChartQueryCache.instance = new ChartQueryCache();
    }
    return ChartQueryCache.instance;
  }

  /**
   * Generates a deterministic canonical cache key from historical query dimensions.
   */
  public generateKey(params: FetchChartHistoryParams): string {
    const id = params.instrumentId || params.symbol || "UNKNOWN";
    const interval = params.interval || "1d";
    const start = params.start || "";
    const end = params.end || "";
    const before = params.before || "";
    const limit = params.limit !== undefined ? String(params.limit) : "";

    return `${id.toUpperCase()}:${interval.toLowerCase()}:${start}:${end}:${before}:${limit}`;
  }

  /**
   * Fetches historical data, deduplicating in-flight requests and returning cached results.
   */
  public async fetch(
    params: FetchChartHistoryParams,
    options?: { forceRefresh?: boolean }
  ): Promise<ChartHistoryResponse> {
    const key = this.generateKey(params);
    const now = Date.now();

    // 1. Check cache if not forcing refresh
    if (!options?.forceRefresh) {
      const cached = this.cache.get(key);
      if (cached && now - cached.timestamp < this.ttlMs) {
        // Return deep-cloned immutable snapshot to prevent accidental mutations
        return JSON.parse(JSON.stringify(cached.data));
      }
    }

    // 2. Check in-flight requests to deduplicate simultaneous calls across panels
    const pending = this.inFlightRequests.get(key);
    if (pending) {
      const result = await pending;
      return JSON.parse(JSON.stringify(result));
    }

    // 3. Dispatch fresh request with deduplication tracking
    const promise = (async () => {
      try {
        const response = await fetchChartHistory(params);
        // Cache result with LRU eviction
        this.set(key, response);
        return response;
      } finally {
        this.inFlightRequests.delete(key);
      }
    })();

    this.inFlightRequests.set(key, promise);
    const data = await promise;
    return JSON.parse(JSON.stringify(data));
  }

  /**
   * Inserts an entry into the cache, enforcing bounded memory limits via LRU eviction.
   */
  public set(key: string, data: ChartHistoryResponse): void {
    if (this.cache.size >= this.capacity) {
      // Evict oldest inserted entry (first key in iteration order)
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  /**
   * Invalidates entries matching an instrument or all entries.
   */
  public invalidate(instrumentIdentifier?: string): void {
    if (!instrumentIdentifier) {
      this.cache.clear();
      return;
    }
    const prefix = instrumentIdentifier.toUpperCase() + ":";
    for (const key of Array.from(this.cache.keys())) {
      if (key.startsWith(prefix)) {
        this.cache.delete(key);
      }
    }
  }

  public getCacheSize(): number {
    return this.cache.size;
  }

  public getInFlightCount(): number {
    return this.inFlightRequests.size;
  }

  public clear(): void {
    this.cache.clear();
    this.inFlightRequests.clear();
  }
}

export const chartQueryCache = ChartQueryCache.getInstance();
