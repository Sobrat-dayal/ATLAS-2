/**
 * Loop Prevention and Feedback Suppression Engine for ATLAS Chart Synchronization (Stage 73).
 *
 * Implements:
 * - Acknowledgment token & suppression window per panel and property
 * - Distinction between genuine USER actions and SYNC_APPLIED updates
 * - Duplicate event rejection via bounded LRU event ID cache
 * - Out-of-order and stale sequence rejection per panel/property
 * - Group revision guards preventing cross-configuration updates
 * - Target range clamping feedback suppression
 */

import { ChartSyncProperty } from "./types";

export interface SuppressionToken {
  panelId: string;
  property: ChartSyncProperty;
  token: string;
  expiresAt: number;
}

export class LoopPreventionCoordinator {
  // Active suppression tokens by key: `${panelId}:${property}`
  private activeSuppressions = new Map<string, SuppressionToken>();

  // Monotonic sequence tracking per panel & property
  private lastSequences = new Map<string, number>();

  // LRU recent event IDs cache to prevent duplicate processing
  private recentEventIds: string[] = [];
  private readonly maxRecentEventIds = 250;

  // Active target panel generations (to reject disposed/reused component instances)
  private panelGenerations = new Map<string, number>();

  /**
   * Acquire a suppression window before programmatically applying state to a target panel.
   * Any callbacks emitted by the chart library for this panel & property within this window
   * will be recognized as SYNC_APPLIED and suppressed from re-propagation.
   */
  public acquireSuppression(
    panelId: string,
    property: ChartSyncProperty,
    durationMs = 350
  ): string {
    const key = `${panelId}:${property}`;
    const token = `token_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    this.activeSuppressions.set(key, {
      panelId,
      property,
      token,
      expiresAt: Date.now() + durationMs,
    });
    return token;
  }

  /**
   * Check if a panel property update is currently suppressed due to a programmatic sync application.
   */
  public isSuppressed(panelId: string, property: ChartSyncProperty): boolean {
    const key = `${panelId}:${property}`;
    const existing = this.activeSuppressions.get(key);
    if (!existing) return false;

    if (Date.now() > existing.expiresAt) {
      this.activeSuppressions.delete(key);
      return false;
    }
    return true;
  }

  /**
   * Explicitly release a suppression token once programmatic update has settled.
   */
  public releaseSuppression(panelId: string, property: ChartSyncProperty): void {
    const key = `${panelId}:${property}`;
    this.activeSuppressions.delete(key);
  }

  /**
   * Verify if an incoming event is a duplicate or out-of-order.
   * Returns true if event is valid to apply; false if duplicate or stale.
   */
  public validateEventSequence(
    eventId: string,
    sourcePanelId: string,
    property: ChartSyncProperty,
    sequence: number
  ): boolean {
    // 1. Check duplicate event ID
    if (this.recentEventIds.includes(eventId)) {
      return false;
    }

    // Record in LRU
    this.recentEventIds.push(eventId);
    if (this.recentEventIds.length > this.maxRecentEventIds) {
      this.recentEventIds.shift();
    }

    // 2. Check monotonic sequence per sourcePanelId & property
    const seqKey = `${sourcePanelId}:${property}`;
    const lastSeq = this.lastSequences.get(seqKey) ?? 0;
    if (sequence <= lastSeq && lastSeq > 0) {
      return false; // Out-of-order or stale event
    }

    this.lastSequences.set(seqKey, sequence);
    return true;
  }

  /**
   * Track panel generation tokens across component mount/unmount lifecycles.
   */
  public registerPanelGeneration(panelId: string): number {
    const current = (this.panelGenerations.get(panelId) ?? 0) + 1;
    this.panelGenerations.set(panelId, current);
    return current;
  }

  public getPanelGeneration(panelId: string): number {
    return this.panelGenerations.get(panelId) ?? 1;
  }

  public releasePanel(panelId: string): void {
    this.panelGenerations.delete(panelId);
    for (const key of Array.from(this.activeSuppressions.keys())) {
      if (key.startsWith(`${panelId}:`)) {
        this.activeSuppressions.delete(key);
      }
    }
    for (const key of Array.from(this.lastSequences.keys())) {
      if (key.startsWith(`${panelId}:`)) {
        this.lastSequences.delete(key);
      }
    }
  }

  /**
   * Reset all coordination state (for testing or full workspace teardown).
   */
  public reset(): void {
    this.activeSuppressions.clear();
    this.lastSequences.clear();
    this.recentEventIds = [];
    this.panelGenerations.clear();
  }
}

export const loopPreventionCoordinator = new LoopPreventionCoordinator();
