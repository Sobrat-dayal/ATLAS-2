"use client";

/**
 * React Hook for Chart Synchronization Management in ATLAS (Stage 73).
 *
 * Exposes:
 * - Reactive synchronization groups and panel assignments
 * - Per-property synchronization toggles (crosshair, range, instrument, interval, type, drawings)
 * - Safe group lifecycle (create, rename, delete, enable, disable)
 * - Member panel assignment and removal (with default independent mode)
 * - User action dispatchers with loop-prevention and frame coalescing
 * - Align group to active chart panel action
 */

import { useEffect, useState, useCallback } from "react";
import {
  ChartSyncGroup,
  ChartSyncProperty,
  ChartSyncSettings,
  CrosshairSyncPayload,
  DrawingSyncPayload,
  InstrumentSyncPayload,
  IntervalSyncPayload,
  TimeRangeSyncPayload,
  ChartTypeSyncPayload,
  chartSyncStore,
  chartSyncController,
} from "@/lib/charts/sync";

export function useChartSync() {
  const [groups, setGroups] = useState<ChartSyncGroup[]>(() =>
    chartSyncStore.getAllGroups()
  );

  useEffect(() => {
    const unsubscribe = chartSyncStore.subscribe(() => {
      setGroups(chartSyncStore.getAllGroups());
    });
    return unsubscribe;
  }, []);

  const getPanelGroup = useCallback((panelId: string): ChartSyncGroup | null => {
    return chartSyncStore.getGroupByPanelId(panelId);
  }, []);

  const createGroup = useCallback((name: string, color?: string) => {
    return chartSyncStore.createGroup(name, color);
  }, []);

  const renameGroup = useCallback((groupId: string, name: string) => {
    chartSyncStore.renameGroup(groupId, name);
  }, []);

  const deleteGroup = useCallback((groupId: string) => {
    chartSyncStore.deleteGroup(groupId);
  }, []);

  const setGroupEnabled = useCallback((groupId: string, enabled: boolean) => {
    chartSyncStore.setGroupEnabled(groupId, enabled);
  }, []);

  const toggleProperty = useCallback(
    (groupId: string, property: ChartSyncProperty) => {
      chartSyncStore.toggleProperty(groupId, property);
    },
    []
  );

  const updateSettings = useCallback(
    (groupId: string, settings: Partial<ChartSyncSettings>) => {
      chartSyncStore.updateSettings(groupId, settings);
    },
    []
  );

  const assignPanel = useCallback((panelId: string, groupId: string) => {
    chartSyncStore.assignPanelToGroup(panelId, groupId);
  }, []);

  const removePanel = useCallback((panelId: string) => {
    chartSyncStore.removePanelFromGroup(panelId);
  }, []);

  const resetToIndependentMode = useCallback(() => {
    chartSyncStore.resetToIndependentMode();
  }, []);

  // Action dispatchers for user interaction
  const syncCrosshair = useCallback(
    (sourcePanelId: string, payload: CrosshairSyncPayload) => {
      chartSyncController.dispatchCrosshairMove(sourcePanelId, payload);
    },
    []
  );

  const syncVisibleRange = useCallback(
    async (sourcePanelId: string, payload: TimeRangeSyncPayload) => {
      return await chartSyncController.dispatchUserAction(
        sourcePanelId,
        "visibleTimeRange",
        payload
      );
    },
    []
  );

  const syncInstrument = useCallback(
    async (sourcePanelId: string, payload: InstrumentSyncPayload) => {
      return await chartSyncController.dispatchUserAction(
        sourcePanelId,
        "instrument",
        payload
      );
    },
    []
  );

  const syncInterval = useCallback(
    async (sourcePanelId: string, payload: IntervalSyncPayload) => {
      return await chartSyncController.dispatchUserAction(
        sourcePanelId,
        "interval",
        payload
      );
    },
    []
  );

  const syncChartType = useCallback(
    async (sourcePanelId: string, payload: ChartTypeSyncPayload) => {
      return await chartSyncController.dispatchUserAction(
        sourcePanelId,
        "chartType",
        payload
      );
    },
    []
  );

  const syncDrawing = useCallback(
    async (sourcePanelId: string, payload: DrawingSyncPayload) => {
      return await chartSyncController.dispatchUserAction(
        sourcePanelId,
        "drawings",
        payload
      );
    },
    []
  );

  /**
   * Align all member panels of a group to a specified source panel's current configuration.
   */
  const alignGroupToPanel = useCallback(
    async (groupId: string, sourcePanelId: string) => {
      const group = chartSyncStore.getGroup(groupId);
      const adapter = chartSyncController.getAdapter(sourcePanelId);
      if (!group || !adapter) return;

      const inst = adapter.getInstrument();
      if (inst) {
        await chartSyncController.dispatchUserAction(sourcePanelId, "instrument", {
          canonicalInstrumentId: inst.entity_id,
          symbol: inst.display_symbol,
          assetClass: inst.asset_class,
          currency: inst.price_currency,
          venue: inst.market_or_venue,
          instrument: inst,
        });
      }

      const intv = adapter.getInterval();
      if (intv) {
        await chartSyncController.dispatchUserAction(sourcePanelId, "interval", {
          intervalId: intv,
        });
      }

      const cType = adapter.getChartType();
      if (cType) {
        await chartSyncController.dispatchUserAction(sourcePanelId, "chartType", {
          renderMode: cType,
        });
      }

      const range = adapter.getVisibleTimeRange();
      if (range) {
        await chartSyncController.dispatchUserAction(sourcePanelId, "visibleTimeRange", {
          from: range.from,
          to: range.to,
          sourceBarsCount: 0,
        });
      }
    },
    []
  );

  return {
    groups,
    getPanelGroup,
    createGroup,
    renameGroup,
    deleteGroup,
    setGroupEnabled,
    toggleProperty,
    updateSettings,
    assignPanel,
    removePanel,
    resetToIndependentMode,
    syncCrosshair,
    syncVisibleRange,
    syncInstrument,
    syncInterval,
    syncChartType,
    syncDrawing,
    alignGroupToPanel,
  };
}
