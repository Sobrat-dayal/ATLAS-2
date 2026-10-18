/**
 * Deterministic Dirty-State Comparator for ATLAS Chart Workspaces (Stage 74).
 *
 * Implements:
 * - Canonical fingerprinting of persistent configuration
 * - Structural difference detection (grid, panels, instruments, intervals, chart types, indicators, drawings, sync groups)
 * - Exclusion of transient market data and interaction events:
 *   - Quote ticks & price updates
 *   - Market event stream updates
 *   - Pointer / mouse movement / crosshairs
 *   - Transient drawing creation previews
 *   - Canvas resizing / zoom interactions
 *   - Recalculated indicator numerical values
 */

import { SavedChartLayoutDocumentV1 } from "./types";

/**
 * Normalizes a layout document into a deterministic JSON string for comparison.
 * Excludes transient and non-deterministic keys (such as timestamps, random client IDs if identical).
 */
export function normalizeDocumentForComparison(doc: SavedChartLayoutDocumentV1 | null): string {
  if (!doc) return "";

  // Deep clone to avoid mutating argument
  const clone: any = {
    schema_version: doc.schema_version,
    layout_id: doc.layout_id,
    panel_order: [...doc.panel_order],
    split_ratios: { ...(doc.split_ratios || {}) },
    active_panel_id: doc.active_panel_id,
    panels: (doc.panels || []).map((p) => ({
      panel_id: p.panel_id,
      instrument_entity_id: p.instrument_entity_id || null,
      symbol: p.symbol,
      interval: p.interval,
      chart_type: p.chart_type,
      following_latest: p.viewport?.following_latest ?? true,
      price_scale_mode: p.price_scale_settings?.mode || "normal",
      indicators: (p.indicators || []).map((ind) => ({
        indicator_id: ind.indicator_id,
        version: ind.version,
        parameters: ind.parameters,
        visible: ind.visible,
      })),
      drawings: (p.drawings || []).map((d) => ({
        type: d.type,
        anchors: (d.anchors || []).map((a) => ({
          time: a.time,
          price: Math.round(Number(a.price) * 10000) / 10000,
        })),
        style: {
          color: d.style?.color,
          lineWidth: d.style?.lineWidth,
          lineStyle: d.style?.lineStyle,
        },
        visible: d.visible,
        locked: d.locked,
      })),
    })),
    synchronization_groups: (doc.synchronization_groups || []).map((g) => ({
      group_id: g.group_id,
      name: g.name,
      member_panel_ids: [...g.member_panel_ids].sort(),
      settings: g.settings,
      enabled: g.enabled,
    })),
  };

  // Sort panels deterministically by panel_id
  clone.panels.sort((a: any, b: any) => a.panel_id.localeCompare(b.panel_id));
  // Sort sync groups deterministically by group_id
  clone.synchronization_groups.sort((a: any, b: any) => a.group_id.localeCompare(b.group_id));

  return JSON.stringify(clone);
}

/**
 * Checks whether the current working document differs meaningfully from the last saved snapshot.
 */
export function isWorkspaceDirty(
  savedSnapshot: SavedChartLayoutDocumentV1 | null,
  currentWorkingDoc: SavedChartLayoutDocumentV1
): boolean {
  if (!savedSnapshot) {
    // If no saved layout was loaded yet, the workspace is clean if it is the default initial workspace
    return false;
  }

  const savedNorm = normalizeDocumentForComparison(savedSnapshot);
  const currentNorm = normalizeDocumentForComparison(currentWorkingDoc);

  return savedNorm !== currentNorm;
}
