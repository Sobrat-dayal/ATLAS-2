/**
 * Master Chart Synchronization Controller and Event Router for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Panel adapter lifecycle registry (mount/unmount)
 * - Deterministic, loop-free event routing
 * - Group membership and per-property entitlement validation
 * - Stale-event rejection, sequence monotonicity, and duplicate prevention
 * - Feedback suppression across programmatic target updates
 * - High-frequency crosshair event coalescing (requestAnimationFrame scheduling)
 * - Safe error boundaries and low-cardinality observability metrics
 */

import {
  ChartSyncCapabilities,
  ChartSyncEvent,
  ChartSyncProperty,
  ChartSynchronizationAdapter,
  CrosshairSyncPayload,
  DrawingSyncPayload,
  InstrumentSyncPayload,
  IntervalSyncPayload,
  SyncApplyResult,
  TimeRangeSyncPayload,
  ChartTypeSyncPayload,
} from "./types";
import { chartSyncStore } from "./syncStore";
import { loopPreventionCoordinator } from "./loopPrevention";
import {
  validateInstrumentSync,
  validateIntervalSync,
  validateChartTypeSync,
  validateDrawingSyncCompatibility,
} from "./compatibility";
import { prepareDrawingForSync } from "./drawingSync";

export interface SyncControllerMetrics {
  eventsDispatched: number;
  eventsApplied: number;
  eventsDroppedDuplicate: number;
  eventsDroppedStale: number;
  eventsDroppedSuppressed: number;
  eventsDroppedIncompatible: number;
}

export class ChartSyncController {
  private adapters = new Map<string, ChartSynchronizationAdapter>();
  private monotonicSequence = 0;

  // Pending high-frequency crosshair event per source panel (coalesced)
  private pendingCrosshairEvents = new Map<string, CrosshairSyncPayload>();
  private crosshairAnimFrameId: number | null = null;

  public metrics: SyncControllerMetrics = {
    eventsDispatched: 0,
    eventsApplied: 0,
    eventsDroppedDuplicate: 0,
    eventsDroppedStale: 0,
    eventsDroppedSuppressed: 0,
    eventsDroppedIncompatible: 0,
  };

  /**
   * Register a chart panel synchronization adapter on mount.
   */
  public registerAdapter(adapter: ChartSynchronizationAdapter): void {
    this.adapters.set(adapter.panelId, adapter);
    loopPreventionCoordinator.registerPanelGeneration(adapter.panelId);
  }

  /**
   * Unregister a chart panel synchronization adapter on disposal.
   */
  public unregisterAdapter(panelId: string): void {
    this.adapters.delete(panelId);
    loopPreventionCoordinator.releasePanel(panelId);
    this.pendingCrosshairEvents.delete(panelId);
    chartSyncStore.removePanelFromGroup(panelId);
  }

  public getAdapter(panelId: string): ChartSynchronizationAdapter | null {
    return this.adapters.get(panelId) ?? null;
  }

  /**
   * High-Frequency Crosshair Dispatcher with frame-rate coalescing.
   * Drops redundant intermediary cursor movements and executes latest position per animation frame.
   */
  public dispatchCrosshairMove(
    sourcePanelId: string,
    payload: CrosshairSyncPayload
  ): void {
    // If feedback is suppressed on source, ignore
    if (loopPreventionCoordinator.isSuppressed(sourcePanelId, "crosshair")) {
      this.metrics.eventsDroppedSuppressed++;
      return;
    }

    // Coalesce into pending map
    this.pendingCrosshairEvents.set(sourcePanelId, payload);

    if (this.crosshairAnimFrameId === null) {
      if (typeof window !== "undefined" && window.requestAnimationFrame) {
        this.crosshairAnimFrameId = window.requestAnimationFrame(() => {
          this.flushPendingCrosshairs();
        });
      } else {
        // Fallback for non-DOM / test environments
        this.flushPendingCrosshairs();
      }
    }
  }

  private flushPendingCrosshairs(): void {
    this.crosshairAnimFrameId = null;
    for (const [sourcePanelId, payload] of Array.from(this.pendingCrosshairEvents.entries())) {
      this.pendingCrosshairEvents.delete(sourcePanelId);
      this.dispatchUserAction(sourcePanelId, "crosshair", payload);
    }
  }

  /**
   * Dispatch a user-originated chart action to the source panel's synchronization group.
   */
  public async dispatchUserAction<T>(
    sourcePanelId: string,
    property: ChartSyncProperty,
    payload: T
  ): Promise<SyncApplyResult[]> {
    // 1. Loop-prevention guard: if source is currently in a sync suppression window, do NOT emit!
    if (loopPreventionCoordinator.isSuppressed(sourcePanelId, property)) {
      this.metrics.eventsDroppedSuppressed++;
      return [];
    }

    // 2. Resolve synchronization group
    const group = chartSyncStore.getGroupByPanelId(sourcePanelId);
    if (!group || !group.enabled || !group.settings[property]) {
      // Group not active or property disabled - charts remain independent
      return [];
    }

    // 3. Create typed event envelope
    this.monotonicSequence++;
    const eventId = `sync_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const event: ChartSyncEvent<T> = {
      eventId,
      groupId: group.id,
      groupRevision: group.revision,
      sourcePanelId,
      sourceGeneration: loopPreventionCoordinator.getPanelGeneration(sourcePanelId),
      property,
      sequence: this.monotonicSequence,
      origin: "USER",
      timestampMs: Date.now(),
      payload,
    };

    this.metrics.eventsDispatched++;

    // 4. Validate monotonic sequence & duplicate protection
    const isValidSequence = loopPreventionCoordinator.validateEventSequence(
      event.eventId,
      sourcePanelId,
      property,
      event.sequence
    );

    if (!isValidSequence) {
      this.metrics.eventsDroppedDuplicate++;
      return [];
    }

    // 5. Route to all destination members in the group (excluding source panel)
    const targetPanelIds = group.memberPanelIds.filter((id) => id !== sourcePanelId);
    const results: SyncApplyResult[] = [];

    for (const targetPanelId of targetPanelIds) {
      const adapter = this.adapters.get(targetPanelId);
      if (!adapter || !adapter.isReady()) {
        results.push({
          panelId: targetPanelId,
          property,
          result: "NOT_READY",
          reason: "Target panel adapter is not mounted or not ready",
        });
        continue;
      }

      // Check group revision guard (reject stale events if group was modified in flight)
      if (event.groupRevision < group.revision) {
        this.metrics.eventsDroppedStale++;
        results.push({
          panelId: targetPanelId,
          property,
          result: "STALE_EVENT",
          reason: "Group revision changed before application",
        });
        continue;
      }

      // 6. Apply with target suppression window (to prevent target callbacks from re-emitting)
      loopPreventionCoordinator.acquireSuppression(targetPanelId, property, 350);

      try {
        const applyResult = await this.routeEventToTarget(adapter, property, payload);
        results.push(applyResult);
        if (applyResult.result === "APPLIED") {
          this.metrics.eventsApplied++;
        } else if (applyResult.result === "UNSUPPORTED") {
          this.metrics.eventsDroppedIncompatible++;
        }
      } catch (err: any) {
        results.push({
          panelId: targetPanelId,
          property,
          result: "ERROR",
          reason: err?.message || "Unknown error during sync application",
        });
      } finally {
        // Leave suppression active for window duration so async callbacks are safely absorbed
      }
    }

    return results;
  }

  /**
   * Internal typed routing to target panel adapter.
   */
  private async routeEventToTarget(
    adapter: ChartSynchronizationAdapter,
    property: ChartSyncProperty,
    payload: any
  ): Promise<SyncApplyResult> {
    const caps = adapter.getCapabilities();

    switch (property) {
      case "crosshair": {
        const p = payload as CrosshairSyncPayload;
        if (p.timestampSeconds === null) {
          adapter.clearCrosshair();
          return { panelId: adapter.panelId, property, result: "APPLIED" };
        }
        return adapter.applyCrosshair(p);
      }

      case "visibleTimeRange": {
        const p = payload as TimeRangeSyncPayload;
        return adapter.applyVisibleTimeRange(p);
      }

      case "instrument": {
        const p = payload as InstrumentSyncPayload;
        const valid = validateInstrumentSync(p.instrument, adapter.panelId);
        if (!valid.isCompatible) {
          return {
            panelId: adapter.panelId,
            property,
            result: "UNSUPPORTED",
            reason: valid.reason,
          };
        }
        return await adapter.applyInstrument(p);
      }

      case "interval": {
        const p = payload as IntervalSyncPayload;
        const valid = validateIntervalSync(
          adapter.getInstrument()?.display_symbol || adapter.panelId,
          p.intervalId,
          caps.supportedIntervals
        );
        if (!valid.isCompatible) {
          return {
            panelId: adapter.panelId,
            property,
            result: "UNSUPPORTED",
            reason: valid.reason,
          };
        }
        return await adapter.applyInterval(p);
      }

      case "chartType": {
        const p = payload as ChartTypeSyncPayload;
        const valid = validateChartTypeSync(
          adapter.getInstrument()?.display_symbol || adapter.panelId,
          p.renderMode,
          caps.hasOHLC
        );
        if (!valid.isCompatible) {
          return {
            panelId: adapter.panelId,
            property,
            result: "UNSUPPORTED",
            reason: valid.reason,
          };
        }
        return adapter.applyChartType(p);
      }

      case "drawings": {
        const p = payload as DrawingSyncPayload;
        if (!adapter.applyDrawing) {
          return {
            panelId: adapter.panelId,
            property,
            result: "UNSUPPORTED",
            reason: "Target panel adapter does not support drawing synchronization",
          };
        }
        return adapter.applyDrawing(p);
      }

      default:
        return {
          panelId: adapter.panelId,
          property,
          result: "UNSUPPORTED",
          reason: `Unsupported property ${property}`,
        };
    }
  }

  /**
   * Reset state for testing or full workspace reload.
   */
  public reset(): void {
    this.adapters.clear();
    this.pendingCrosshairEvents.clear();
    if (this.crosshairAnimFrameId !== null && typeof window !== "undefined" && window.cancelAnimationFrame) {
      window.cancelAnimationFrame(this.crosshairAnimFrameId);
    }
    this.crosshairAnimFrameId = null;
    this.monotonicSequence = 0;
    this.metrics = {
      eventsDispatched: 0,
      eventsApplied: 0,
      eventsDroppedDuplicate: 0,
      eventsDroppedStale: 0,
      eventsDroppedSuppressed: 0,
      eventsDroppedIncompatible: 0,
    };
    loopPreventionCoordinator.reset();
  }
}

export const chartSyncController = new ChartSyncController();
