/**
 * Typed Drawing Object Models and Context Definitions for ATLAS Charts V1 (Stage 71).
 *
 * Implements canonical financial coordinate anchoring:
 * - Drawings anchor strictly to financial { time, price }, NEVER raw screen pixels.
 * - Stable UUID identity and schema versioning for future Stage 74 compatibility.
 * - Financial chart context scoping (instrument, series, price basis).
 * - Full type definitions for all 9 supported drawing tools, snapping, history, and styles.
 */

export type DrawingType =
  | "trendline"
  | "horizontal_line"
  | "horizontal_ray"
  | "vertical_line"
  | "rectangle"
  | "price_range"
  | "time_range"
  | "price_time_measure"
  | "fibonacci_retracement";

export interface DrawingAnchor {
  /** UTC Unix timestamp in seconds */
  time: number;
  /** Validated financial price */
  price: number;
}

export interface DrawingChartContext {
  instrument_entity_id: string;
  symbol: string;
  price_basis: "raw" | "adjusted";
  quotation_unit?: string;
}

export type LineStrokeStyle = "solid" | "dashed" | "dotted";

export interface DrawingStyle {
  color: string;
  lineWidth: number; // 1, 2, 3, 4
  lineStyle: LineStrokeStyle;
  fillOpacity: number; // 0 to 1
  showLabel: boolean;
  fontSize?: number;
}

export interface DrawingObject {
  id: string;
  type: DrawingType;
  version: number;
  context: DrawingChartContext;
  anchors: DrawingAnchor[];
  style: DrawingStyle;
  visible: boolean;
  locked: boolean;
  zIndex: number;
  createdAt: string;
  updatedAt: string;
}

export interface DrawingToolDefinition {
  type: DrawingType;
  displayName: string;
  description: string;
  requiredAnchors: number;
  iconName: string;
  category: "line" | "zone" | "measurement" | "fibonacci";
}

export type SnappingMode = "OFF" | "NEAREST_BAR" | "OHLC";

export type InteractionState =
  | "IDLE"
  | "TOOL_ARMED"
  | "PLACING_FIRST_ANCHOR"
  | "PLACING_NEXT_ANCHOR"
  | "DRAGGING_DRAWING"
  | "DRAGGING_ANCHOR"
  | "DRAWING_SELECTED";

export type DrawingCommandType =
  | "CREATE"
  | "DELETE"
  | "MOVE"
  | "EDIT_ANCHOR"
  | "CHANGE_STYLE"
  | "LOCK"
  | "VISIBILITY"
  | "CLEAR";

export interface DrawingCommand {
  command_id: string;
  type: DrawingCommandType;
  before_state: DrawingObject[];
  after_state: DrawingObject[];
  target_drawing_ids: string[];
  timestamp: number;
}

export interface ScreenPoint {
  x: number;
  y: number;
}

export interface RenderedAnchor {
  time: number;
  price: number;
  x: number;
  y: number;
}
