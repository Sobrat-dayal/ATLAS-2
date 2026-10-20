/**
 * Render Batching & Event Coalescing for High-Performance Table Updates (Stage 78).
 *
 * Implements:
 * - Coalesces incoming rapid quote updates into bounded render frames (default 80ms)
 * - Prevents UI main-thread thrashing when processing dozens/hundreds of market updates per second
 * - Flushes pending updates cleanly on demand or on component unmount
 */

import { CanonicalLiveQuote } from "./types";

export interface RenderBatcherOptions {
  batchIntervalMs?: number;
  onFlush: (batch: Map<string, CanonicalLiveQuote>) => void;
}

export class RenderBatcher {
  private readonly batchIntervalMs: number;
  private readonly onFlush: (batch: Map<string, CanonicalLiveQuote>) => void;
  private pendingUpdates: Map<string, CanonicalLiveQuote> = new Map();
  private timer: ReturnType<typeof setTimeout> | null = null;
  private isDestroyed: boolean = false;

  constructor(options: RenderBatcherOptions) {
    this.batchIntervalMs = options.batchIntervalMs ?? 80;
    this.onFlush = options.onFlush;
  }

  /**
   * Enqueues an incremental quote update into the pending batch.
   */
  public enqueue(quote: CanonicalLiveQuote): void {
    if (this.isDestroyed) return;

    this.pendingUpdates.set(quote.instrument_entity_id.toLowerCase(), quote);

    if (!this.timer) {
      this.timer = setTimeout(() => {
        this.flush();
      }, this.batchIntervalMs);
    }
  }

  /**
   * Immediately flushes all pending updates to the registered listener.
   */
  public flush(): void {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    if (this.pendingUpdates.size === 0) return;

    const batch = new Map(this.pendingUpdates);
    this.pendingUpdates.clear();

    try {
      this.onFlush(batch);
    } catch (err) {
      console.error("Error in render batch flush callback:", err);
    }
  }

  public getPendingCount(): number {
    return this.pendingUpdates.size;
  }

  public destroy(): void {
    this.isDestroyed = true;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.pendingUpdates.clear();
  }
}
