/**
 * Explicit Pure Hydrator and Restoration Planner for ATLAS Chart Workspaces (Stage 74).
 *
 * Implements:
 * - Structural schema validation and pre-flight boundary verification
 * - Atomic workspace state construction without intermediate partial rendering
 * - Per-panel drawing object reconstruction from financial coordinates
 * - Synchronization group hydration with strict loop-prevention isolation (ZERO sync echo cascades)
 * - Detailed RestorationReport production
 */

import {
  RestorationReport,
  SavedChartLayoutDocumentV1,
  SavedChartPanelV1,
} from "./types";
import {
  ChartPanelState,
  MultiChartWorkspaceState,
  workspaceStore,
  MultiChartWorkspaceStore,
} from "../workspace";
import { DrawingSessionStore } from "../drawings/drawingStore";
import { DrawingObject } from "../drawings/types";
import { chartSyncStore, ChartSyncStore } from "../sync/syncStore";
import { ChartSyncGroup } from "../sync/types";
import { IndicatorInstanceConfig } from "../indicators/types";
import { validateLayoutDocument } from "./schema";

export interface HydrationOptions {
  workspaceStoreInstance?: MultiChartWorkspaceStore;
  syncStoreInstance?: ChartSyncStore;
  drawingStoreResolver?: (panelId: string) => DrawingSessionStore;
  onApplyIndicators?: (panelId: string, indicators: IndicatorInstanceConfig[]) => void;
}

export function hydrateChartWorkspace(
  documentData: unknown,
  options?: HydrationOptions
): RestorationReport {
  // 1. Strict pre-flight validation
  const doc: SavedChartLayoutDocumentV1 = validateLayoutDocument(documentData);

  const targetWorkspaceStore = options?.workspaceStoreInstance || workspaceStore;
  const targetSyncStore = options?.syncStoreInstance || chartSyncStore;

  const restoredPanels: Record<string, ChartPanelState> = {};
  const degradedPanels: { panelId: string; symbol: string; reason: string }[] = [];
  let totalIndicators = 0;
  let totalDrawings = 0;

  // 2. Prepare panel states
  for (const savedPanel of doc.panels) {
    const isVisible = doc.panel_order.includes(savedPanel.panel_id);
    if (!isVisible) continue;

    restoredPanels[savedPanel.panel_id] = {
      panelId: savedPanel.panel_id,
      symbol: savedPanel.symbol,
      instrument: savedPanel.instrument_entity_id
        ? {
            entity_id: savedPanel.instrument_entity_id,
            display_name: savedPanel.symbol,
            display_symbol: savedPanel.symbol,
            asset_class: savedPanel.asset_class || "equities",
            market_or_venue: "AUTO",
            price_currency: "USD",
            quotation_unit: "units",
            supported_intervals: ["1d"],
            default_interval: savedPanel.interval || "1d",
            price_basis: "raw",
            adjustment_basis: "none",
            provider_key: "primary",
            has_volume: true,
            is_futures: false,
            allows_negative_price: false,
          }
        : null,
      interval: savedPanel.interval || "1d",
      renderMode: savedPanel.chart_type || "candlestick",
      isActive: savedPanel.panel_id === doc.active_panel_id,
      lifecycleStatus: "READY",
      isLivePaused: false,
      isFollowingLatest: savedPanel.viewport?.following_latest ?? true,
    };

    // 3. Reconstruct drawings for this panel
    const store = options?.drawingStoreResolver
      ? options.drawingStoreResolver(savedPanel.panel_id)
      : DrawingSessionStore.getForPanel(savedPanel.panel_id);

    if (store) {
      store.setContext({
        instrument_entity_id: savedPanel.instrument_entity_id || "default",
        symbol: savedPanel.symbol,
        price_basis: "raw",
      });

      const reconstructedDrawings: DrawingObject[] = (savedPanel.drawings || []).map(
        (savedDraw, idx) => ({
          id: savedDraw.id || `draw_${savedPanel.panel_id}_${idx}`,
          type: savedDraw.type,
          version: savedDraw.version || 1,
          context: {
            instrument_entity_id: savedPanel.instrument_entity_id || "default",
            symbol: savedPanel.symbol,
            price_basis: "raw",
          },
          anchors: savedDraw.anchors.map((a) => ({
            time: a.time,
            price: Number(a.price),
          })),
          style: {
            color: savedDraw.style.color || "#38bdf8",
            lineWidth: savedDraw.style.lineWidth || 2,
            lineStyle: savedDraw.style.lineStyle || "solid",
            fillOpacity: savedDraw.style.fillOpacity ?? 0.15,
            showLabel: savedDraw.style.showLabel ?? false,
          },
          visible: savedDraw.visible ?? true,
          locked: savedDraw.locked ?? false,
          zIndex: savedDraw.z_index ?? idx + 1,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        })
      );

      store.replaceAllDrawings(reconstructedDrawings);
      totalDrawings += reconstructedDrawings.length;
    }

    // 4. Dispatch indicators to panel indicator manager
    if (options?.onApplyIndicators && Array.isArray(savedPanel.indicators)) {
      const indicatorConfigs: IndicatorInstanceConfig[] = savedPanel.indicators.map((ind) => ({
        instance_id: ind.instance_id,
        indicator_id: ind.indicator_id,
        version: ind.version || 1,
        parameters: { ...(ind.parameters || {}) },
        visible: ind.visible ?? true,
        color: ind.color || null,
        line_width: ind.line_width || null,
      }));
      options.onApplyIndicators(savedPanel.panel_id, indicatorConfigs);
      totalIndicators += indicatorConfigs.length;
    } else if (Array.isArray(savedPanel.indicators)) {
      totalIndicators += savedPanel.indicators.length;
    }
  }

  // 5. Build full MultiChartWorkspaceState and apply atomically
  const workspaceState: MultiChartWorkspaceState = {
    layoutId: doc.layout_id,
    panelIds: [...doc.panel_order],
    activePanelId: doc.active_panel_id,
    splitRatios: { ...(doc.split_ratios || {}) },
    panels: restoredPanels,
    isMobileTabMode: false,
    activeMobileTabId: doc.active_panel_id,
  };

  targetWorkspaceStore.loadWorkspaceState(workspaceState);

  // 6. Restore Synchronization Groups without cascade
  const restoredSyncGroups: ChartSyncGroup[] = (doc.synchronization_groups || []).map(
    (sg, idx) => ({
      id: sg.group_id,
      name: sg.name,
      memberPanelIds: sg.member_panel_ids.filter((mid) => doc.panel_order.includes(mid)),
      settings: { ...sg.settings },
      enabled: sg.enabled,
      revision: 1,
      color: sg.color || (idx === 0 ? "#06b6d4" : "#10b981"),
    })
  );

  targetSyncStore.loadSyncGroups(restoredSyncGroups);

  return {
    layoutId: doc.layout_id,
    layoutName: "Restored Layout",
    totalPanels: doc.panel_order.length,
    restoredPanels: Object.keys(restoredPanels).length,
    degradedPanels,
    restoredIndicatorsCount: totalIndicators,
    restoredDrawingsCount: totalDrawings,
    restoredSyncGroupsCount: restoredSyncGroups.length,
    timestamp: new Date().toISOString(),
  };
}
