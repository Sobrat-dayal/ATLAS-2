/**
 * Source-Scoped Event Ordering, Deduplication, and Gap Detection (Stage 78).
 *
 * Implements:
 * - Duplicate event protection (bounded cache of processed event IDs)
 * - Chronological ordering: rejects older or stale events (incoming timestamp <= current timestamp)
 * - Source-scoped sequence tracking and gap detection
 * - Protection against older events overwriting newer snapshots or events
 */

export interface EventOrderingDecision {
  accepted: boolean;
  reason?: string;
  isDuplicate?: boolean;
  isOutOfOrder?: boolean;
  hasSequenceGap?: boolean;
}

interface InstrumentSequenceState {
  lastSourceTimestampUnix: number;
  lastSequenceNumber: number | null;
  lastSourceEpoch: string | null;
}

export class EventOrderingTracker {
  private readonly maxTrackedEventIds: number;
  private readonly processedEventIds: Set<string> = new Set();
  private readonly eventIdQueue: string[] = [];

  // instrumentEntityId -> sequence state
  private readonly instrumentStates: Map<string, InstrumentSequenceState> = new Map();

  constructor(maxTrackedEventIds: number = 500) {
    this.maxTrackedEventIds = maxTrackedEventIds;
  }

  /**
   * Evaluates an incoming event for duplication, ordering, and sequence gaps.
   */
  public evaluate(
    instrumentId: string,
    eventId: string | undefined,
    sourceTimestampStr: string,
    sequenceStr?: string | null,
    sourceEpoch?: string | null
  ): EventOrderingDecision {
    const canonicalId = instrumentId.toLowerCase();

    // 1. Duplicate event ID check
    if (eventId) {
      if (this.processedEventIds.has(eventId)) {
        return {
          accepted: false,
          reason: `DUPLICATE_EVENT_ID: Event ${eventId} was already processed`,
          isDuplicate: true,
        };
      }
    }

    const incomingUnix = Date.parse(sourceTimestampStr);
    if (Number.isNaN(incomingUnix)) {
      return {
        accepted: false,
        reason: `INVALID_TIMESTAMP: Could not parse "${sourceTimestampStr}"`,
      };
    }

    const state = this.instrumentStates.get(canonicalId);

    if (state) {
      // Check for source epoch change (e.g. server/feed restart)
      const epochChanged =
        sourceEpoch && state.lastSourceEpoch && sourceEpoch !== state.lastSourceEpoch;

      if (!epochChanged) {
        // 2. Chronological ordering check: incoming must be strictly newer than current
        if (incomingUnix < state.lastSourceTimestampUnix) {
          return {
            accepted: false,
            reason: `OUT_OF_ORDER_EVENT: Incoming timestamp (${sourceTimestampStr}) is older than current state (${new Date(state.lastSourceTimestampUnix).toISOString()})`,
            isOutOfOrder: true,
          };
        }

        if (incomingUnix === state.lastSourceTimestampUnix) {
          // If timestamps are equal, check if sequence is present and strictly greater
          if (sequenceStr && state.lastSequenceNumber !== null) {
            const incomingSeq = Number(sequenceStr);
            if (!Number.isNaN(incomingSeq) && incomingSeq <= state.lastSequenceNumber) {
              return {
                accepted: false,
                reason: `DUPLICATE_OR_STALE_SEQUENCE: Sequence ${sequenceStr} <= last sequence ${state.lastSequenceNumber}`,
                isDuplicate: true,
              };
            }
          } else {
            // Equal timestamp without monotonic sequence -> duplicate
            return {
              accepted: false,
              reason: `DUPLICATE_EVENT_TIMESTAMP: Event has identical observation timestamp (${sourceTimestampStr})`,
              isDuplicate: true,
            };
          }
        }
      }

      // 3. Sequence gap detection
      let hasSequenceGap = false;
      if (sequenceStr && state.lastSequenceNumber !== null && !epochChanged) {
        const incomingSeq = Number(sequenceStr);
        if (!Number.isNaN(incomingSeq) && incomingSeq > state.lastSequenceNumber + 1) {
          hasSequenceGap = true;
        }
      }

      // Record updated state
      state.lastSourceTimestampUnix = incomingUnix;
      if (sequenceStr) {
        const num = Number(sequenceStr);
        if (!Number.isNaN(num)) state.lastSequenceNumber = num;
      }
      if (sourceEpoch) state.lastSourceEpoch = sourceEpoch;

      this.recordEventId(eventId);

      return {
        accepted: true,
        hasSequenceGap,
      };
    }

    // First event for this instrument
    const newState: InstrumentSequenceState = {
      lastSourceTimestampUnix: incomingUnix,
      lastSequenceNumber: sequenceStr ? Number(sequenceStr) || null : null,
      lastSourceEpoch: sourceEpoch || null,
    };
    this.instrumentStates.set(canonicalId, newState);

    this.recordEventId(eventId);

    return { accepted: true, hasSequenceGap: false };
  }

  /**
   * Sets or updates baseline timestamp from authoritative snapshot.
   */
  public updateSnapshotWatermark(
    instrumentId: string,
    snapshotTimestampStr: string
  ): void {
    const canonicalId = instrumentId.toLowerCase();
    const snapUnix = Date.parse(snapshotTimestampStr);
    if (Number.isNaN(snapUnix)) return;

    const state = this.instrumentStates.get(canonicalId);
    if (state) {
      if (snapUnix > state.lastSourceTimestampUnix) {
        state.lastSourceTimestampUnix = snapUnix;
      }
    } else {
      this.instrumentStates.set(canonicalId, {
        lastSourceTimestampUnix: snapUnix,
        lastSequenceNumber: null,
        lastSourceEpoch: null,
      });
    }
  }

  private recordEventId(eventId?: string): void {
    if (!eventId) return;

    this.processedEventIds.add(eventId);
    this.eventIdQueue.push(eventId);

    if (this.eventIdQueue.length > this.maxTrackedEventIds) {
      const oldest = this.eventIdQueue.shift();
      if (oldest) this.processedEventIds.delete(oldest);
    }
  }

  public clear(): void {
    this.processedEventIds.clear();
    this.eventIdQueue.length = 0;
    this.instrumentStates.clear();
  }
}
