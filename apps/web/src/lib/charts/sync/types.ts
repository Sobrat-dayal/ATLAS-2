/**
 * Chart Synchronization Domain Model and Event Contracts for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Session-level synchronization groups (bounded to 4 panels)
 * - Fine-grained per-property synchronization settings (crosshairs, visible time ranges, instruments, intervals, chart types, drawings)
 * - Strongly typed synchronization events with origin tracking (USER vs SYNC_APPLIED)
 * - Monotonic sequence ordering, group revision tracking, and source generation tokens
 * - Strict loop-prevention metadata and suppression contracts
 * - Canonical financial instrument resolution contracts
 * - Temporal mapping and market calendar alignment results
 * - Read-only financial integrity (no fabricated bars, no fake OHLC)
 */

import {
  ChartInstrumentMetadata,
  ChartRenderMode,
  HoveredBarData,
} from "../types";

export type ChartSyncProperty =
  | "crosshair"
  | "visibleTimeRange"
  | "instrument"
  | "interval"
  | "chartType"
  | "drawings";

export interface ChartSyncSettings {
  crosshair: boolean;
  visibleTimeRange: boolean;
  instrument: boolean;
  interval: boolean;
  chartType: boolean;
  drawings: boolean;
}

export const DEFAULT_SYNC_SETTINGS: ChartSyncSettings = {
  crosshair: false,
  visibleTimeRange: false,
  instrument: false,
  interval: false,
  chartType: false,
  drawings: false,
};

export interface ChartSyncGroup {
  id: string; // e.g. "group-a", "group-b"
  name: string; // e.g. "Group A"
  memberPanelIds: string[]; // Panel IDs belonging to this group (max 4 in workspace)
  settings: ChartSyncSettings;
  enabled: boolean;
  revision: number; // Monotonically increasing configuration revision
  color: string; // Hex color for badge (cyan, emerald, amber, purple)
}

export type ChartSyncEventOrigin = "USER" | "SYNC_APPLIED";

export interface ChartSyncEvent<T = any> {
  eventId: string;
  groupId: string;
  groupRevision: number;
  sourcePanelId: string;
  sourceGeneration: number;
  property: ChartSyncProperty;
  sequence: number;
  origin: ChartSyncEventOrigin;
  timestampMs: number;
  payload: T;
}

// 1. Crosshair Synchronization Payload
export interface CrosshairSyncPayload {
  timestampSeconds: number | null; // UTC Unix seconds (null means crosshair left chart)
  isoTime: string | null;
  sourceInterval: string;
  price?: number | null; // Optional price (for same-instrument price guide)
  sourceSymbol: string;
}

// 2. Visible Time Range Synchronization Payload
export interface TimeRangeSyncPayload {
  from: number; // UTC Unix seconds
  to: number; // UTC Unix seconds
  sourceBarsCount: number;
}

// 3. Instrument Synchronization Payload
export interface InstrumentSyncPayload {
  canonicalInstrumentId: string; // UUID or entity ID
  symbol: string;
  assetClass: string;
  currency: string;
  venue?: string;
  instrument: ChartInstrumentMetadata;
}

// 4. Interval Synchronization Payload
export interface IntervalSyncPayload {
  intervalId: string; // e.g. "1m", "5m", "15m", "1h", "1d"
}

// 5. Chart Type Synchronization Payload
export interface ChartTypeSyncPayload {
  renderMode: ChartRenderMode;
}

// 6. Drawing Synchronization Payload
export interface DrawingSyncPayload {
  action: "ADD" | "UPDATE" | "DELETE" | "CLEAR";
  drawingId: string;
  drawingData?: any;
  canonicalInstrumentId: string;
  priceBasis?: string;
}

// Result codes for target panel synchronization application
export type SyncApplyResultCode =
  | "APPLIED"
  | "UNCHANGED"
  | "UNSUPPORTED"
  | "NOT_READY"
  | "NOT_ENTITLED"
  | "OUT_OF_COVERAGE"
  | "STALE_EVENT"
  | "IGNORED_ECHO"
  | "ERROR";

export interface SyncApplyResult {
  panelId: string;
  property: ChartSyncProperty;
  result: SyncApplyResultCode;
  reason?: string;
}

// Temporal Session Alignment Mapping Result
export type TemporalAlignmentMatchType =
  | "EXACT_INSTANT"
  | "SAME_TRADING_SESSION"
  | "NEAREST_AVAILABLE_BAR"
  | "OUT_OF_BOUNDS"
  | "NO_MATCH";

export interface TemporalMappingResult {
  matchType: TemporalAlignmentMatchType;
  targetTimestamp: number | null;
  hasBarAtTimestamp: boolean;
  notes?: string;
}

// Target Panel Capability Contract
export interface ChartSyncCapabilities {
  canSyncCrosshair: boolean;
  canSyncTimeRange: boolean;
  canSyncInstrument: boolean;
  canSyncInterval: boolean;
  canSyncChartType: boolean;
  canSyncDrawings: boolean;
  supportedIntervals: string[];
  supportedChartTypes: ChartRenderMode[];
  hasOHLC: boolean;
}

export const DEFAULT_PANEL_CAPABILITIES: ChartSyncCapabilities = {
  canSyncCrosshair: true,
  canSyncTimeRange: true,
  canSyncInstrument: true,
  canSyncInterval: true,
  canSyncChartType: true,
  canSyncDrawings: false, // Strict compatibility gate required
  supportedIntervals: ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
  supportedChartTypes: ["candlestick", "bar", "line", "area"],
  hasOHLC: true,
};

// Target Chart Panel Synchronization Adapter Contract
export interface ChartSynchronizationAdapter {
  panelId: string;
  generation: number;

  getInstrument(): ChartInstrumentMetadata | null;
  getInterval(): string;
  getChartType(): ChartRenderMode;
  getVisibleTimeRange(): { from: number; to: number } | null;

  applyCrosshair(payload: CrosshairSyncPayload): SyncApplyResult;
  clearCrosshair(): void;

  applyVisibleTimeRange(payload: TimeRangeSyncPayload): SyncApplyResult;
  applyInstrument(payload: InstrumentSyncPayload): Promise<SyncApplyResult>;
  applyInterval(payload: IntervalSyncPayload): Promise<SyncApplyResult>;
  applyChartType(payload: ChartTypeSyncPayload): SyncApplyResult;
  applyDrawing?(payload: DrawingSyncPayload): SyncApplyResult;

  getCapabilities(): ChartSyncCapabilities;
  isReady(): boolean;
}
