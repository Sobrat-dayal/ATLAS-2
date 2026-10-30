/**
 * Typed Event Bus for ATLAS Stage 121: Global Workspace Linking.
 *
 * Implements:
 * 1. In-browser typed event pub/sub.
 * 2. Monotonic channel revision tracking (stale event dropping).
 * 3. Causation-chain loop prevention (echo suppression).
 * 4. Deduplication cache for repeated event delivery.
 * 5. Bounded subscriber fan-out by channel and dimension.
 * 6. Optional BroadcastChannel synchronization for USER_APPLICATION scope.
 */

import { ContextDimension, ContextSelectionEvent, ContextScope } from "./types";

export type EventSubscriberCallback = (event: ContextSelectionEvent) => void;

interface SubscriptionRecord {
  subscriptionId: string;
  channelId: string;
  panelInstanceId?: string;
  inboundDimensions: ContextDimension[];
  callback: EventSubscriberCallback;
}

class ContextEventBus {
  private subscribers: Map<string, SubscriptionRecord> = new Map();
  private processedEventIds: Set<string> = new Set();
  private channelRevisions: Map<string, number> = new Map();
  private broadcastChannel: BroadcastChannel | null = null;

  constructor() {
    if (typeof window !== "undefined" && "BroadcastChannel" in window) {
      try {
        this.broadcastChannel = new BroadcastChannel("atlas_global_context_bus");
        this.broadcastChannel.onmessage = (msgEvent) => {
          if (msgEvent.data && typeof msgEvent.data === "object") {
            const event = msgEvent.data as ContextSelectionEvent;
            // Only accept USER_APPLICATION or USER_CROSS_TAB
            if (event.scope === "USER_APPLICATION" || event.scope === "USER_CROSS_TAB") {
              this.dispatchLocal(event, false);
            }
          }
        };
      } catch {
        // BroadcastChannel unavailable in sandboxed environment
        this.broadcastChannel = null;
      }
    }
  }

  /**
   * Subscribe a panel or component to context events.
   */
  public subscribe(
    channelId: string,
    panelInstanceId: string | undefined,
    inboundDimensions: ContextDimension[],
    callback: EventSubscriberCallback
  ): () => void {
    const subId = `sub_${Math.random().toString(36).substring(2, 9)}`;
    const record: SubscriptionRecord = {
      subscriptionId: subId,
      channelId,
      panelInstanceId,
      inboundDimensions,
      callback,
    };
    this.subscribers.set(subId, record);

    return () => {
      this.subscribers.delete(subId);
    };
  }

  /**
   * Set or update current revision for a channel.
   */
  public setChannelRevision(channelId: string, revision: number): void {
    const current = this.channelRevisions.get(channelId) || 0;
    if (revision > current) {
      this.channelRevisions.set(channelId, revision);
    }
  }

  public getChannelRevision(channelId: string): number {
    return this.channelRevisions.get(channelId) || 1;
  }

  /**
   * Publish an event from a panel.
   */
  public publish(event: ContextSelectionEvent): {
    status: "DELIVERED" | "DUPLICATE_DROPPED" | "STALE_DROPPED" | "LOOP_PREVENTED";
    deliveredCount: number;
  } {
    // 1. Deduplication
    if (this.processedEventIds.has(event.event_id)) {
      return { status: "DUPLICATE_DROPPED", deliveredCount: 0 };
    }

    // 2. Monotonic Revision Check
    const currentRev = this.channelRevisions.get(event.channel_id) || 1;
    if (event.context_revision < currentRev) {
      return { status: "STALE_DROPPED", deliveredCount: 0 };
    }

    // Advance channel revision
    this.channelRevisions.set(event.channel_id, event.context_revision);

    // 3. Broadcast cross-tab if application-scoped
    if (
      this.broadcastChannel &&
      (event.scope === "USER_APPLICATION" || event.scope === "USER_CROSS_TAB")
    ) {
      try {
        this.broadcastChannel.postMessage(event);
      } catch {
        // Broadcast failed
      }
    }

    // 4. Dispatch locally
    const deliveredCount = this.dispatchLocal(event, true);
    return { status: "DELIVERED", deliveredCount };
  }

  private dispatchLocal(event: ContextSelectionEvent, recordEvent: boolean): number {
    if (recordEvent) {
      this.processedEventIds.add(event.event_id);
      if (this.processedEventIds.size > 5000) {
        this.processedEventIds.clear();
      }
    }

    let count = 0;
    for (const sub of this.subscribers.values()) {
      // Must match channel
      if (sub.channelId !== event.channel_id) continue;

      // Echo suppression: do not deliver back to origin panel
      if (sub.panelInstanceId && sub.panelInstanceId === event.origin_panel_instance_id) {
        continue;
      }

      // Dimension compatibility filter
      if (!sub.inboundDimensions.includes(event.dimension)) {
        continue;
      }

      try {
        sub.callback(event);
        count++;
      } catch (err) {
        console.error("Context subscriber delivery error", err);
      }
    }

    return count;
  }

  public clear(): void {
    this.subscribers.clear();
    this.processedEventIds.clear();
    this.channelRevisions.clear();
  }
}

export const globalEventBus = new ContextEventBus();

