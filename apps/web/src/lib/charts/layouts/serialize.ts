/**
 * Explicit Pure Serializer for ATLAS Chart Workspaces (Stage 74).
 *
 * Critical architectural principle:
 * A saved chart layout is a versioned description of the user's chart workspace configuration,
 * NOT a stored copy of live financial market data or active browser runtime objects.
 *
 * Persists:
 * - Layout preset (single, two-columns, two-rows, three-left-focus, three-top-focus, four-grid)
 * - Panel order and stable logical panel IDs
 * - Split ratios (finite, normalized)
 * - Active panel preference
 * - Canonical instrument identity (entity_id UUID, symbol, asset_class)
 * - Bar intervals and chart render modes (candlestick, bar, line, area)
 * - Viewport preferences (followingLatest, visible range)
 * - Price scale settings (normal, logarithmic, invert)
 * - Technical indicator instances & parameters (NO calculated point arrays!)
 * - Drawing objects & financial anchors (NO screen pixels, NO undo/redo stacks!)
 * - Synchronization groups & property settings (NO active cursor positions, NO event queues!)
 *
 * Forbids & Excludes:
 * - OHLCV historical arrays
 * - Live Quotes / last price caches
 * - Calculated indicator output series
 * - Raw mouse / pointer / drag coordinates
 * - Canvas instances, SVG DOM nodes, React refs
 * - WebSocket objects / subscription tokens
 * - API keys, Provider credentials, authentication tokens
 * - Trading orders or portfolio holdings
 */

import {
  SavedChartLayoutDocumentV1,
  SavedChartPanelV1,
  SavedDrawingV1,
  SavedIndicatorInstanceV1,
  SavedSyncGroupV1,
} from "./types";
import { MultiChartWorkspaceState } from "../workspace/types";
import { DrawingSessionStore } from "../drawings/drawingStore";
import { ChartSyncStore } from "../sync/syncStore";
import { IndicatorInstanceConfig } from "../indicators/types";
import { validateLayoutDocument } from "./schema";

export interface SerializationOptions {
  panelIndicatorsMap?: Record<string, IndicatorInstanceConfig[]>;
  drawingStoreResolver?: (panelId: string) => DrawingSessionStore;
  syncStore?: ChartSyncStore;
}

export function serializeChartWorkspace(
  workspaceState: MultiChartWorkspaceState,
  options?: SerializationOptions
): SavedChartLayoutDocumentV1 {
  const panelOrder = [...workspaceState.panelIds];
  const panels: SavedChartPanelV1[] = [];

  for (const panelId of panelOrder) {
    const panel = workspaceState.panels[panelId];
    if (!panel) continue;

    // 1. Serialize indicators for this panel (configuration only)
    const rawIndicators = options?.panelIndicatorsMap?.[panelId] || [];
    const indicators: SavedIndicatorInstanceV1[] = rawIndicators.map((ind) => ({
      instance_id: ind.instance_id,
      indicator_id: ind.indicator_id,
      version: ind.version || 1,
      parameters: { ...(ind.parameters || {}) },
      visible: ind.visible ?? true,
      color: ind.color || null,
      line_width: ind.line_width || null,
    }));

    // 2. Serialize drawings for this panel (financial coordinates only)
    const store = options?.drawingStoreResolver
      ? options.drawingStoreResolver(panelId)
      : DrawingSessionStore.getForPanel(panelId);

    const rawDrawings = store ? store.getDrawings() : [];
    const drawings: SavedDrawingV1[] = rawDrawings.map((draw) => ({
      id: draw.id,
      type: draw.type,
      version: draw.version || 1,
      anchors: draw.anchors.map((a) => ({
        time: a.time,
        price: Number(a.price),
      })),
      style: {
        color: draw.style.color,
        lineWidth: draw.style.lineWidth,
        lineStyle: draw.style.lineStyle,
        fillOpacity: draw.style.fillOpacity,
        showLabel: draw.style.showLabel,
      },
      visible: draw.visible ?? true,
      locked: draw.locked ?? false,
      z_index: draw.zIndex ?? 1,
    }));

    // 3. Assemble panel aggregate
    panels.push({
      panel_id: panel.panelId,
      instrument_entity_id: panel.instrument?.entity_id || null,
      symbol: panel.symbol,
      asset_class: panel.instrument?.asset_class || null,
      interval: panel.interval || "1d",
      chart_type: panel.renderMode || "candlestick",
      viewport: {
        visible_start: null,
        visible_end: null,
        following_latest: panel.isFollowingLatest ?? true,
      },
      price_scale_settings: {
        mode: "normal",
        invert: false,
        logarithmic: false,
      },
      indicators,
      drawings,
    });
  }

  // 4. Serialize Synchronization Groups (configuration only)
  const syncStore = options?.syncStore;
  const rawGroups = syncStore ? syncStore.getAllGroups() : [];
  const synchronization_groups: SavedSyncGroupV1[] = rawGroups.map((g) => ({
    group_id: g.id,
    name: g.name,
    member_panel_ids: g.memberPanelIds.filter((mid) => panelOrder.includes(mid)),
    settings: { ...g.settings },
    enabled: g.enabled,
    color: g.color,
  }));

  // 5. Clean normalized split ratios
  const split_ratios: Record<string, number> = {};
  if (workspaceState.splitRatios) {
    for (const [key, val] of Object.entries(workspaceState.splitRatios)) {
      if (typeof val === "number" && isFinite(val)) {
        split_ratios[key] = Math.round(val * 1000) / 1000;
      }
    }
  }

  const document: SavedChartLayoutDocumentV1 = {
    schema_version: 1,
    layout_id: workspaceState.layoutId,
    panel_order: panelOrder,
    split_ratios,
    active_panel_id: workspaceState.activePanelId || panelOrder[0] || "panel-1",
    panels,
    synchronization_groups,
  };

  // 6. Enforce strict validation
  return validateLayoutDocument(document);
}
