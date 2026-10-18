/**
 * Saved Chart Layouts Domain Models and Serialization Types for ATLAS Charts (Stage 74).
 *
 * Implements:
 * - Versioned layout-document schema (V1)
 * - Persistent multi-chart configuration aggregate (grid preset, panels, split ratios, active panel)
 * - Saved indicator configurations (definitions and parameters only; never calculated output arrays)
 * - Saved drawing objects (financial coordinates; never screen pixel coordinates)
 * - Saved synchronization groups and property settings (never active cursor pointers or event queues)
 * - Optimistic concurrency metadata (revisions, ETags, dirty-state tracking, conflict resolution)
 * - Portable export/import envelope contracts
 */

import { ChartLayoutId, ChartPanelState } from "../workspace/types";
import { ChartRenderMode } from "../types";
import { ChartSyncGroup, ChartSyncSettings } from "../sync/types";
import { DrawingAnchor, DrawingChartContext, DrawingObject, DrawingStyle, DrawingType } from "../drawings/types";
import { IndicatorInstanceConfig } from "../indicators/types";

export type LayoutDocumentSchemaVersion = 1;

// 1. Saved Viewport Configuration
export interface SavedViewportV1 {
  visible_start?: string | null;
  visible_end?: string | null;
  following_latest: boolean;
}

// 2. Saved Price Scale Settings
export interface SavedPriceScaleSettingsV1 {
  mode: "normal" | "logarithmic" | "percentage" | "indexed_to_100";
  invert: boolean;
  logarithmic: boolean;
}

// 3. Saved Indicator Instance (Configuration only)
export interface SavedIndicatorInstanceV1 {
  instance_id: string;
  indicator_id: string;
  version: number;
  parameters: Record<string, unknown>;
  visible: boolean;
  color?: string | null;
  line_width?: number | null;
}

// 4. Saved Drawing Object (Financial anchors only)
export interface SavedDrawingV1 {
  id: string;
  type: DrawingType;
  version: number;
  anchors: DrawingAnchor[];
  style: Partial<DrawingStyle>;
  visible: boolean;
  locked: boolean;
  z_index: number;
}

// 5. Saved Chart Panel Aggregate
export interface SavedChartPanelV1 {
  panel_id: string;
  instrument_entity_id?: string | null;
  symbol: string;
  asset_class?: string | null;
  interval: string;
  chart_type: ChartRenderMode;
  viewport?: SavedViewportV1 | null;
  price_scale_settings?: SavedPriceScaleSettingsV1 | null;
  indicators: SavedIndicatorInstanceV1[];
  drawings: SavedDrawingV1[];
}

// 6. Saved Synchronization Group
export interface SavedSyncGroupV1 {
  group_id: string;
  name: string;
  member_panel_ids: string[];
  settings: ChartSyncSettings;
  enabled: boolean;
  color: string;
}

// 7. Canonical Saved Chart Layout Document V1
export interface SavedChartLayoutDocumentV1 {
  schema_version: 1;
  layout_id: ChartLayoutId;
  panel_order: string[];
  split_ratios: Record<string, number>;
  active_panel_id: string;
  panels: SavedChartPanelV1[];
  synchronization_groups: SavedSyncGroupV1[];
}

// 8. Layout Metadata and Summary Records
export interface SavedLayoutSummary {
  id: string;
  name: string;
  description?: string | null;
  layout_type: ChartLayoutId;
  chart_count: number;
  is_default: boolean;
  revision: number;
  document_schema_version: number;
  created_at: string;
  updated_at: string;
}

export interface SavedLayoutDetail extends SavedLayoutSummary {
  owner_user_id: string;
  normalized_name: string;
  document: SavedChartLayoutDocumentV1;
}

// 9. Portable Export Envelope
export interface LayoutExportEnvelope {
  format: "atlas_chart_layout";
  export_version: 1;
  exported_at: string;
  layout_name: string;
  document_schema_version: 1;
  layout_document: SavedChartLayoutDocumentV1;
}

// 10. Concurrency Conflict Recovery State
export interface LayoutConflictState {
  layoutId: string;
  layoutName: string;
  expectedRevision: number;
  serverRevision: number;
  workingDocument: SavedChartLayoutDocumentV1;
}

// 11. Restoration Execution & Report
export interface RestorationReport {
  layoutId: string;
  layoutName: string;
  totalPanels: number;
  restoredPanels: number;
  degradedPanels: {
    panelId: string;
    symbol: string;
    reason: string;
  }[];
  restoredIndicatorsCount: number;
  restoredDrawingsCount: number;
  restoredSyncGroupsCount: number;
  timestamp: string;
}
