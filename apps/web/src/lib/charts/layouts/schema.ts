/**
 * Runtime Schema Validation and Guard Utilities for Saved Chart Layouts (Stage 74).
 */

import {
  SavedChartLayoutDocumentV1,
  SavedChartPanelV1,
  SavedDrawingV1,
  SavedIndicatorInstanceV1,
  SavedSyncGroupV1,
} from "./types";
import { ChartLayoutId } from "../workspace/types";
import { ChartRenderMode } from "../types";

export const VALID_LAYOUT_IDS: ChartLayoutId[] = [
  "single",
  "two-columns",
  "two-rows",
  "three-left-focus",
  "three-top-focus",
  "four-grid",
];

export const VALID_CHART_TYPES: ChartRenderMode[] = [
  "candlestick",
  "bar",
  "line",
  "area",
];

export const MAX_PANELS_PER_LAYOUT = 4;
export const MAX_INDICATORS_PER_PANEL = 12;
export const MAX_DRAWINGS_PER_PANEL = 250;
export const MAX_SYNC_GROUPS_PER_LAYOUT = 4;
export const MAX_DOCUMENT_BYTES = 512 * 1024; // 512 KiB

const FORBIDDEN_KEYWORDS = [
  "password",
  "token",
  "secret",
  "api_key",
  "apikey",
  "credentials",
  "access_token",
  "refresh_token",
  "session_id",
  "bars_array",
  "ohlcv_data",
  "calculated_series",
  "indicator_cache",
];

export class LayoutValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LayoutValidationError";
  }
}

export function scanForForbiddenContent(obj: unknown): void {
  if (!obj || typeof obj !== "object") return;

  if (Array.isArray(obj)) {
    for (const item of obj) {
      scanForForbiddenContent(item);
    }
    return;
  }

  const record = obj as Record<string, unknown>;
  for (const [key, val] of Object.entries(record)) {
    const lowerKey = key.toLowerCase();
    for (const forbidden of FORBIDDEN_KEYWORDS) {
      if (lowerKey.includes(forbidden)) {
        throw new LayoutValidationError(
          `Forbidden property or keyword '${key}' detected in chart layout. ` +
          `Saved layouts must not store credentials, raw market data, or calculated indicator caches.`
        );
      }
    }
    scanForForbiddenContent(val);
  }
}

export function validateLayoutDocument(data: unknown): SavedChartLayoutDocumentV1 {
  if (!data || typeof data !== "object") {
    throw new LayoutValidationError("Layout document must be an object.");
  }

  // 1. Check serialized payload size
  const serialized = JSON.stringify(data);
  if (serialized.length > MAX_DOCUMENT_BYTES) {
    throw new LayoutValidationError(
      `Layout document size (${serialized.length} bytes) exceeds maximum permitted limit of ${MAX_DOCUMENT_BYTES} bytes.`
    );
  }

  // 2. Scan for forbidden properties
  scanForForbiddenContent(data);

  const doc = data as Record<string, any>;

  // 3. Schema Version
  if (doc.schema_version !== 1) {
    throw new LayoutValidationError(
      `Unsupported schema_version '${doc.schema_version}'. Only schema version 1 is supported.`
    );
  }

  // 4. Layout ID Preset
  if (!VALID_LAYOUT_IDS.includes(doc.layout_id)) {
    throw new LayoutValidationError(
      `Invalid layout_id '${doc.layout_id}'. Must be one of ${VALID_LAYOUT_IDS.join(", ")}.`
    );
  }

  // 5. Panel Order
  if (!Array.isArray(doc.panel_order) || doc.panel_order.length === 0) {
    throw new LayoutValidationError("panel_order must be a non-empty array of panel IDs.");
  }
  if (doc.panel_order.length > MAX_PANELS_PER_LAYOUT) {
    throw new LayoutValidationError(
      `panel_order exceeds maximum allowed panels (${MAX_PANELS_PER_LAYOUT}).`
    );
  }

  // 6. Panels List
  if (!Array.isArray(doc.panels) || doc.panels.length === 0) {
    throw new LayoutValidationError("panels must be a non-empty array of panel configurations.");
  }
  if (doc.panels.length > MAX_PANELS_PER_LAYOUT) {
    throw new LayoutValidationError(
      `panels count exceeds maximum allowed panels (${MAX_PANELS_PER_LAYOUT}).`
    );
  }

  const panelIds = new Set<string>();
  for (const panel of doc.panels) {
    if (!panel || typeof panel !== "object") {
      throw new LayoutValidationError("Each panel in panels must be an object.");
    }
    if (!panel.panel_id || typeof panel.panel_id !== "string") {
      throw new LayoutValidationError("Each panel must have a string panel_id.");
    }
    if (panelIds.has(panel.panel_id)) {
      throw new LayoutValidationError(`Duplicate panel_id detected: '${panel.panel_id}'.`);
    }
    panelIds.add(panel.panel_id);

    if (!panel.symbol || typeof panel.symbol !== "string") {
      throw new LayoutValidationError(`Panel '${panel.panel_id}' must specify a valid symbol.`);
    }

    if (panel.chart_type && !VALID_CHART_TYPES.includes(panel.chart_type)) {
      throw new LayoutValidationError(
        `Panel '${panel.panel_id}' specifies unsupported chart_type '${panel.chart_type}'.`
      );
    }

    if (Array.isArray(panel.indicators) && panel.indicators.length > MAX_INDICATORS_PER_PANEL) {
      throw new LayoutValidationError(
        `Panel '${panel.panel_id}' exceeds maximum allowed indicators (${MAX_INDICATORS_PER_PANEL}).`
      );
    }

    if (Array.isArray(panel.drawings) && panel.drawings.length > MAX_DRAWINGS_PER_PANEL) {
      throw new LayoutValidationError(
        `Panel '${panel.panel_id}' exceeds maximum allowed drawings (${MAX_DRAWINGS_PER_PANEL}).`
      );
    }
  }

  // 7. Verify panel_order consistency
  for (const pid of doc.panel_order) {
    if (!panelIds.has(pid)) {
      throw new LayoutValidationError(
        `panel_order references panel '${pid}' which does not exist in panels list.`
      );
    }
  }

  // 8. Active Panel ID Consistency
  if (!doc.active_panel_id || typeof doc.active_panel_id !== "string") {
    throw new LayoutValidationError("active_panel_id must be specified.");
  }
  if (!panelIds.has(doc.active_panel_id)) {
    throw new LayoutValidationError(
      `active_panel_id '${doc.active_panel_id}' does not match any valid panel in panels list.`
    );
  }

  // 9. Split Ratios Validation
  if (doc.split_ratios && typeof doc.split_ratios === "object") {
    for (const [k, val] of Object.entries(doc.split_ratios)) {
      if (typeof val !== "number" || isNaN(val) || !isFinite(val) || val < 0.05 || val > 0.95) {
        throw new LayoutValidationError(
          `split_ratio for '${k}' must be a finite number between 0.05 and 0.95, got ${val}.`
        );
      }
    }
  }

  // 10. Synchronization Groups Validation
  if (Array.isArray(doc.synchronization_groups)) {
    if (doc.synchronization_groups.length > MAX_SYNC_GROUPS_PER_LAYOUT) {
      throw new LayoutValidationError(
        `synchronization_groups exceeds maximum allowed groups (${MAX_SYNC_GROUPS_PER_LAYOUT}).`
      );
    }
    for (const group of doc.synchronization_groups) {
      if (!group || typeof group !== "object" || !group.group_id || !group.name) {
        throw new LayoutValidationError("Each synchronization group must specify group_id and name.");
      }
      if (Array.isArray(group.member_panel_ids)) {
        for (const mid of group.member_panel_ids) {
          if (!panelIds.has(mid)) {
            throw new LayoutValidationError(
              `Sync group '${group.group_id}' references unknown panel '${mid}'.`
            );
          }
        }
      }
    }
  }

  return doc as SavedChartLayoutDocumentV1;
}
