/**
 * Shared Reference-Counted Live Market Data Subscription Manager for Multi-Chart Workspaces (Stage 72).
 *
 * Implements:
 * - Shared, deduplicated live quote streaming across multiple chart panels
 * - Subscription reference counting per canonical series (instrument_entity_id / display_symbol)
 * - Zero duplicated network connections or controller instances when multiple panels display the same series
 * - Independent panel pause/resume state (pausing Panel A does not pause Panel B)
 * - Safe lifecycle management: unmounting one panel decrements reference count; teardown only occurs on ref count = 0
 * - Bounded live subscription capacity (respecting WORKSPACE_RESOURCE_BUDGET.maxLiveSubscriptions)
 */

import { ChartInstrumentMetadata, LiveQuoteDTO } from "../types";
import { LiveChartController, LiveChartStatus } from "../live-controller";
import { WORKSPACE_RESOURCE_BUDGET } from "./types";

export type PanelQuoteListener = (quote: LiveQuoteDTO, status: LiveChartStatus) => void;
export type PanelStatusListener = (status: LiveChartStatus) => void;

interface SeriesSubscription {
  subscriptionKey: string;
  instrument: ChartInstrumentMetadata;
  controller: LiveChartController;
  listeners: Map<
    string,
    {
      onQuote: PanelQuoteListener;
      onStatus?: PanelStatusListener;
      isPaused: boolean;
    }
  >;
  lastQuote: LiveQuoteDTO | null;
  lastStatus: LiveChartStatus | null;
}

export class SharedChartSubscriptionManager {
  private static instance: SharedChartSubscriptionManager;

  // Map of subscriptionKey -> SeriesSubscription
  private subscriptions: Map<string, SeriesSubscription> = new Map();

  public static getInstance(): SharedChartSubscriptionManager {
    if (!SharedChartSubscriptionManager.instance) {
      SharedChartSubscriptionManager.instance = new SharedChartSubscriptionManager();
    }
    return SharedChartSubscriptionManager.instance;
  }

  /**
   * Generates a canonical subscription key from instrument metadata.
   */
  public getSubscriptionKey(instrument: ChartInstrumentMetadata): string {
    return (instrument.entity_id || instrument.display_symbol).toUpperCase();
  }

  /**
   * Subscribes a panel to live market data updates for a canonical instrument.
   * If a stream for this instrument already exists, reuses it and increments the reference count.
   */
  public subscribe(
    panelId: string,
    instrument: ChartInstrumentMetadata,
    onQuote: PanelQuoteListener,
    onStatus?: PanelStatusListener
  ): () => void {
    const key = this.getSubscriptionKey(instrument);
    let sub = this.subscriptions.get(key);

    if (!sub) {
      // Enforce live subscription quota
      if (this.subscriptions.size >= WORKSPACE_RESOURCE_BUDGET.maxLiveSubscriptions) {
        console.warn(
          `Live subscription limit (${WORKSPACE_RESOURCE_BUDGET.maxLiveSubscriptions}) reached. Cannot subscribe panel ${panelId}.`
        );
        return () => {};
      }

      // Initialize single underlying controller for this series
      const controller = new LiveChartController({
        instrumentId: instrument.entity_id || instrument.display_symbol,
        symbol: instrument.display_symbol,
        allowsNegativePrice: instrument.allows_negative_price,
        onQuoteUpdate: (quote, status) => {
          this.handleQuoteUpdate(key, quote, status);
        },
        onStatusChange: (status) => {
          this.handleStatusChange(key, status);
        },
      });

      sub = {
        subscriptionKey: key,
        instrument,
        controller,
        listeners: new Map(),
        lastQuote: null,
        lastStatus: null,
      };

      this.subscriptions.set(key, sub);
      controller.start();
    }

    // Register panel listener
    sub.listeners.set(panelId, {
      onQuote,
      onStatus,
      isPaused: false,
    });

    // Deliver cached latest state immediately if available
    if (sub.lastQuote && sub.lastStatus) {
      onQuote(sub.lastQuote, sub.lastStatus);
    }
    if (sub.lastStatus && onStatus) {
      onStatus(sub.lastStatus);
    }

    // Return cleanup unsubscription function
    return () => {
      this.unsubscribe(panelId, key);
    };
  }

  /**
   * Unsubscribes a panel from a series. Decrements reference count and tears down controller if ref count reaches 0.
   */
  public unsubscribe(panelId: string, subscriptionKey: string): void {
    const sub = this.subscriptions.get(subscriptionKey);
    if (!sub) return;

    sub.listeners.delete(panelId);

    // If no more panels are listening to this series, cleanly destroy the underlying controller
    if (sub.listeners.size === 0) {
      sub.controller.destroy();
      this.subscriptions.delete(subscriptionKey);
    }
  }

  /**
   * Toggles or sets pause state for a specific panel without affecting other consumers of the shared stream.
   */
  public setPanelPaused(panelId: string, subscriptionKey: string, isPaused: boolean): void {
    const sub = this.subscriptions.get(subscriptionKey);
    if (!sub) return;

    const listener = sub.listeners.get(panelId);
    if (listener) {
      listener.isPaused = isPaused;
    }
  }

  private handleQuoteUpdate(
    key: string,
    quote: LiveQuoteDTO,
    status: LiveChartStatus
  ): void {
    const sub = this.subscriptions.get(key);
    if (!sub) return;

    sub.lastQuote = quote;
    sub.lastStatus = status;

    // Dispatch to all active (unpaused) panel listeners
    sub.listeners.forEach((listener) => {
      if (!listener.isPaused) {
        try {
          listener.onQuote(quote, status);
        } catch (err) {
          console.error("Error in panel quote listener:", err);
        }
      }
    });
  }

  private handleStatusChange(key: string, status: LiveChartStatus): void {
    const sub = this.subscriptions.get(key);
    if (!sub) return;

    sub.lastStatus = status;

    sub.listeners.forEach((listener) => {
      if (listener.onStatus) {
        try {
          listener.onStatus(status);
        } catch (err) {
          console.error("Error in panel status listener:", err);
        }
      }
    });
  }

  public getActiveSubscriptionCount(): number {
    return this.subscriptions.size;
  }

  public getReferenceCount(subscriptionKey: string): number {
    return this.subscriptions.get(subscriptionKey)?.listeners.size ?? 0;
  }

  public clear(): void {
    this.subscriptions.forEach((sub) => {
      sub.controller.destroy();
    });
    this.subscriptions.clear();
  }
}

export const sharedSubscriptionManager = SharedChartSubscriptionManager.getInstance();
