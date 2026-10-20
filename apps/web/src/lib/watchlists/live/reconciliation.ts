/**
 * Snapshot-and-Stream Reconciliation for Live Watchlists (Stage 78).
 *
 * Solves:
 * - Startup race: stream events arriving while initial HTTP snapshot is in-flight
 * - Stale snapshot overwriting newer streamed quote
 * - Bounded buffering (dropping oldest if buffer overflows, requesting canonical resync)
 * - Reconnection resync: reconciling current latest state after network restoration
 */

import { IncomingQuoteEvent } from "./types";
import { EventOrderingTracker } from "./event-ordering";

export interface SnapshotReconcileOptions {
  maxBufferSize?: number;
}

export class SnapshotStreamReconciler {
  private readonly maxBufferSize: number;
  private readonly buffer: IncomingQuoteEvent[] = [];
  private isSnapshotLoaded: boolean = false;

  constructor(options: SnapshotReconcileOptions = {}) {
    this.maxBufferSize = options.maxBufferSize ?? 100;
  }

  public getIsSnapshotLoaded(): boolean {
    return this.isSnapshotLoaded;
  }

  public markSnapshotPending(): void {
    this.isSnapshotLoaded = false;
    this.buffer.length = 0;
  }

  public markSnapshotLoaded(): void {
    this.isSnapshotLoaded = true;
  }

  /**
   * Buffers an event while snapshot is pending.
   * Returns false if buffer overflowed (triggering resync requirement).
   */
  public bufferEvent(event: IncomingQuoteEvent): boolean {
    if (this.buffer.length >= this.maxBufferSize) {
      // Bounded buffer exceeded: drop buffer to prevent memory leak and signal resync needed
      this.buffer.length = 0;
      return false;
    }
    this.buffer.push(event);
    return true;
  }

  /**
   * Reconciles snapshot with buffered events.
   * Compares snapshot timestamp with buffered events for the same instrument.
   * The chronologically newest observation always wins.
   */
  public reconcileOnSnapshotLoaded(
    snapshotTimestampStr: string | null,
    instrumentId: string,
    orderingTracker: EventOrderingTracker
  ): {
    applySnapshot: boolean;
    pendingEventsToReplay: IncomingQuoteEvent[];
  } {
    this.isSnapshotLoaded = true;

    if (!snapshotTimestampStr) {
      return { applySnapshot: true, pendingEventsToReplay: [...this.buffer] };
    }

    const snapUnix = Date.parse(snapshotTimestampStr);

    // Filter events for this instrument in the buffer
    const instrumentEvents = this.buffer.filter((e) => {
      const legacyId = (e as IncomingQuoteEvent & { instrument_id?: string }).instrument_id;
      const eid = (e.instrument_entity_id || legacyId || "").toLowerCase();
      return eid === instrumentId.toLowerCase();
    });

    // Find newest event timestamp in buffer for this instrument
    let newestEventUnix = 0;
    for (const ev of instrumentEvents) {
      const ts =
        ev.payload?.quote?.as_of ||
        ev.payload?.quote?.source_timestamp ||
        ev.payload?.source_timestamp ||
        ev.emitted_at;
      if (ts) {
        const u = Date.parse(ts);
        if (!Number.isNaN(u) && u > newestEventUnix) {
          newestEventUnix = u;
        }
      }
    }

    // If buffered stream event is newer than the snapshot, the snapshot is STALE and must not overwrite!
    const applySnapshot = !newestEventUnix || snapUnix >= newestEventUnix;

    if (applySnapshot) {
      orderingTracker.updateSnapshotWatermark(instrumentId, snapshotTimestampStr);
    }

    // Keep events for other instruments or newer events
    const pending = [...this.buffer];
    this.buffer.length = 0;

    return {
      applySnapshot,
      pendingEventsToReplay: pending,
    };
  }

  public clear(): void {
    this.buffer.length = 0;
    this.isSnapshotLoaded = false;
  }
}
