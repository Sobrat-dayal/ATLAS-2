/**
 * Technical Indicator TypeScript types and interfaces for ATLAS Charts (Stage 69).
 */

export type IndicatorCategory =
  | "TREND"
  | "MOMENTUM"
  | "VOLATILITY"
  | "VOLUME"
  | "STATISTICAL";

export type IndicatorRenderingTarget = "PRICE_OVERLAY" | "INDICATOR_PANE";

export type IndicatorParameterType = "INTEGER" | "DECIMAL" | "BOOLEAN" | "STRING";

export type IndicatorStatus =
  | "READY"
  | "WARMUP"
  | "DATA_GAP"
  | "INSUFFICIENT_HISTORY"
  | "INCOMPATIBLE_INPUT"
  | "MISSING_VOLUME"
  | "TALIB_UNAVAILABLE"
  | "UNSUPPORTED_INTERVAL"
  | "NOT_ENTITLED"
  | "CALCULATION_ERROR";

export interface IndicatorParameterDefinition {
  name: string;
  type: IndicatorParameterType;
  default: unknown;
  required: boolean;
  min_value?: number | null;
  max_value?: number | null;
  allowed_values?: unknown[] | null;
  description?: string | null;
}

export interface IndicatorDefinition {
  indicator_id: string;
  version: number;
  display_name: string;
  description: string;
  category: IndicatorCategory;
  rendering_target: IndicatorRenderingTarget;
  input_requirements: string[];
  parameters: IndicatorParameterDefinition[];
  output_names?: string[];
  default_color: string;
  default_line_width: number;
  supported_intervals: string[];
  min_history_bars: number;
}

export interface IndicatorPoint {
  timestamp: string;
  time_unix: number;
  value: number | null;
  status: IndicatorStatus;
}

export interface IndicatorOutputSeries {
  series_id: string;
  name: string;
  rendering_type: string;
  unit?: string | null;
  color?: string | null;
  line_width?: number | null;
  points: IndicatorPoint[];
}

export interface IndicatorInstanceConfig {
  instance_id: string;
  indicator_id: string;
  version: number;
  parameters: Record<string, unknown>;
  visible: boolean;
  color?: string | null;
  line_width?: number | null;
}

export interface IndicatorCalculationRequest {
  instrument_id?: string;
  symbol?: string;
  interval?: string;
  start?: string;
  end?: string;
  instances: IndicatorInstanceConfig[];
}

export interface IndicatorCalculationResult {
  instance_id: string;
  indicator_id: string;
  version: number;
  parameters: Record<string, unknown>;
  rendering_target: IndicatorRenderingTarget;
  status: IndicatorStatus;
  error_message?: string | null;
  required_lookback_bars: number;
  series: IndicatorOutputSeries[];
}

export interface IndicatorCalculationResponse {
  instrument_entity_id: string;
  symbol: string;
  interval: string;
  calculated_at: string;
  results: IndicatorCalculationResult[];
}

export interface IndicatorCatalogResponse {
  indicators: IndicatorDefinition[];
}
