/**
 * TypeScript Contracts for Stage 75: Historical Chart Replay V1.
 *
 * Defines:
 * - Replay session statuses and step directions
 * - Public DTOs matching backend Pydantic schemas
 * - Replay capability and historical coverage contracts
 * - Playback controller state structures
 */

import { ChartBarDTO } from "../types";

export type ReplaySessionStatus =
  | "INITIALIZING"
  | "READY"
  | "PLAYING"
  | "PAUSED"
  | "END_OF_DATA"
  | "ERROR"
  | "CLOSED";

export type ReplayStepDirection = "forward" | "backward";

export type ReplaySpeed = 0.5 | 1 | 2 | 5 | 10;

export interface ReplaySourceSnapshot {
  instrument_entity_id: string;
  display_symbol: string;
  canonical_market_series_identity: Record<string, any>;
  interval: string;
  provider: string;
  venue: string;
  price_basis: string;
  adjustment_basis: string;
  quote_unit: string;
  source_revision_fingerprint: string;
}

export interface ReplaySessionDTO {
  session_id: string;
  owner_user_id: string;
  target_panel_id: string;
  instrument_entity_id: string;
  display_symbol: string;
  interval: string;
  status: ReplaySessionStatus;
  cursor_index: int;
  start_index: int;
  cursor_bar: ChartBarDTO | null;
  revealed_bars_count: number;
  total_bars: number;
  playback_speed: number;
  source_snapshot: ReplaySourceSnapshot;
  created_at: string;
  expires_at: string;
}

// Helper int type alias
type int = number;

export interface ReplayStartRequest {
  panel_id?: string;
  instrument_id?: string;
  symbol?: string;
  interval?: string;
  start_time?: string | null;
  start_index?: number | null;
  history_window?: number;
  playback_speed?: number;
}

export interface ReplayStartResponse {
  session: ReplaySessionDTO;
  revealed_bars: ChartBarDTO[];
}

export interface ReplayStepRequest {
  direction?: ReplayStepDirection;
  count?: number;
  expected_cursor_index?: number | null;
}

export interface ReplayStepResponse {
  session_id: string;
  status: ReplaySessionStatus;
  cursor_index: number;
  cursor_bar: ChartBarDTO | null;
  direction: string;
  revealed_bar: ChartBarDTO | null;
  removed_bar_index: number | null;
  is_end_of_data: boolean;
  is_start_of_data: boolean;
  revealed_bars_count: number;
  total_bars: number;
}

export interface ReplaySeekRequest {
  target_index?: number | null;
  target_time?: string | null;
}

export interface ReplaySeekResponse {
  session: ReplaySessionDTO;
  revealed_bars: ChartBarDTO[];
}

export interface ReplayCapabilityResponse {
  instrument_id: string;
  display_symbol: string;
  is_replay_supported: boolean;
  supported_intervals: string[];
  earliest_available_bar: string | null;
  latest_available_bar: string | null;
  total_bars_available: number;
  point_in_time_guarantee: boolean;
  methodological_notice: string;
}
