/**
 * TypeScript Type Definitions for Company Earnings Intelligence (Stage 84).
 */

export const EarningsEventType = {
  EARNINGS_RELEASE: "EARNINGS_RELEASE",
  EARNINGS_CALL: "EARNINGS_CALL",
  RESULTS_PRESENTATION: "RESULTS_PRESENTATION",
  SHAREHOLDER_MEETING: "SHAREHOLDER_MEETING",
} as const;
export type EarningsEventType = typeof EarningsEventType[keyof typeof EarningsEventType];

export const EarningsEventStatus = {
  CONFIRMED: "CONFIRMED",
  ESTIMATED: "ESTIMATED",
  TENTATIVE: "TENTATIVE",
  POSTPONED: "POSTPONED",
  CANCELLED: "CANCELLED",
  COMPLETED: "COMPLETED",
} as const;
export type EarningsEventStatus = typeof EarningsEventStatus[keyof typeof EarningsEventStatus];

export const MarketSession = {
  BEFORE_MARKET: "BEFORE_MARKET",
  AFTER_MARKET: "AFTER_MARKET",
  DURING_HOURS: "DURING_HOURS",
  UNSPECIFIED: "UNSPECIFIED",
} as const;
export type MarketSession = typeof MarketSession[keyof typeof MarketSession];

export type EarningsPeriodType = "QUARTERLY" | "ANNUAL" | "SEMI_ANNUAL";

export type AccountingBasis = "GAAP" | "NON_GAAP" | "IFRS";

export const SurpriseClassification = {
  BEAT: "BEAT",
  MISS: "MISS",
  IN_LINE: "IN_LINE",
  NOT_COMPARABLE: "NOT_COMPARABLE",
  UNAVAILABLE: "UNAVAILABLE",
} as const;
export type SurpriseClassification = typeof SurpriseClassification[keyof typeof SurpriseClassification];

export type GuidanceMetricType =
  | "REVENUE"
  | "EPS"
  | "OPERATING_INCOME"
  | "NET_INCOME"
  | "GROSS_MARGIN"
  | "CAPEX";

export const GuidanceStatus = {
  ACTIVE: "ACTIVE",
  REVISED: "REVISED",
  WITHDRAWN: "WITHDRAWN",
  SUPERSEDED: "SUPERSEDED",
} as const;
export type GuidanceStatus = typeof GuidanceStatus[keyof typeof GuidanceStatus];

export const TranscriptStatus = {
  AVAILABLE: "AVAILABLE",
  LICENSED_ONLY: "LICENSED_ONLY",
  PROCESSING: "PROCESSING",
  SCHEDULED: "SCHEDULED",
  RESTRICTED: "RESTRICTED",
  PENDING: "PENDING",
  UNAVAILABLE: "UNAVAILABLE",
} as const;
export type TranscriptStatus = typeof TranscriptStatus[keyof typeof TranscriptStatus];

export interface EarningsEventDTO {
  event_id: string;
  company_id: string;
  fiscal_period: string;
  fiscal_year: number;
  fiscal_quarter?: string | null;
  event_type: EarningsEventType;
  status: EarningsEventStatus;
  announced_date?: string | null;
  announced_time?: string | null;
  timezone: string;
  market_session: MarketSession;
  is_confirmed: boolean;
  source: string;
  webcast_url?: string | null;
}

export interface ConsensusSnapshotDTO {
  consensus_id: string;
  fiscal_period: string;
  period_type: EarningsPeriodType;
  consensus_eps?: number | null;
  consensus_revenue?: number | null;
  formatted_eps: string;
  formatted_revenue: string;
  eps_high?: number | null;
  eps_low?: number | null;
  revenue_high?: number | null;
  revenue_low?: number | null;
  analyst_count: number;
  methodology: string;
  snapshot_timestamp?: string | null;
  pre_release_cutoff: boolean;
}

export interface QuarterlyEarningsItemDTO {
  fiscal_period: string;
  fiscal_year: number;
  fiscal_quarter?: string | null;
  announced_date?: string | null;
  market_session: MarketSession;
  status: EarningsEventStatus;
  // EPS
  actual_eps?: number | null;
  formatted_actual_eps: string;
  estimate_eps?: number | null;
  formatted_estimate_eps: string;
  eps_surprise_abs?: number | null;
  eps_surprise_pct?: number | null;
  formatted_eps_surprise_pct: string;
  eps_classification: SurpriseClassification;
  // Revenue
  actual_revenue?: number | null;
  formatted_actual_revenue: string;
  estimate_revenue?: number | null;
  formatted_estimate_revenue: string;
  revenue_surprise_abs?: number | null;
  revenue_surprise_pct?: number | null;
  formatted_revenue_surprise_pct: string;
  revenue_classification: SurpriseClassification;
  currency: string;
  is_restated: boolean;
  source: string;
}

export interface ManagementGuidanceDTO {
  guidance_id: string;
  fiscal_period: string;
  metric: GuidanceMetricType;
  low_value?: number | null;
  high_value?: number | null;
  point_value?: number | null;
  formatted_range: string;
  currency: string;
  accounting_basis: AccountingBasis;
  issued_at: string;
  status: GuidanceStatus;
  notes?: string | null;
  source_document?: string | null;
}

export interface EarningsCallDTO {
  call_id: string;
  fiscal_period: string;
  call_datetime?: string | null;
  timezone: string;
  webcast_url?: string | null;
  presentation_url?: string | null;
  transcript_document_id?: string | null;
  transcript_status: TranscriptStatus;
  audio_available: boolean;
  key_topics: string[];
}

export interface CompanyEarningsOverviewDTO {
  company_id: string;
  company_name: string;
  latest_completed?: QuarterlyEarningsItemDTO | null;
  next_scheduled?: EarningsEventDTO | null;
  next_consensus?: ConsensusSnapshotDTO | null;
  active_guidance: ManagementGuidanceDTO[];
  latest_call?: EarningsCallDTO | null;
  recent_history: QuarterlyEarningsItemDTO[];
}

export interface EarningsHistoryResponseDTO {
  company_id: string;
  company_name: string;
  period_type: EarningsPeriodType;
  total_count: number;
  items: QuarterlyEarningsItemDTO[];
}

export interface EarningsEventsResponseDTO {
  company_id: string;
  company_name: string;
  total_count: number;
  events: EarningsEventDTO[];
}

export interface GuidanceResponseDTO {
  company_id: string;
  company_name: string;
  total_count: number;
  guidance_items: ManagementGuidanceDTO[];
}

export interface EarningsCallsResponseDTO {
  company_id: string;
  company_name: string;
  total_count: number;
  calls: EarningsCallDTO[];
}

// Aliases for convenience
export type QuarterlyEarningsItem = QuarterlyEarningsItemDTO;
export type ManagementGuidanceItem = ManagementGuidanceDTO;
export type EarningsCallItem = EarningsCallDTO;
export type EarningsEvent = EarningsEventDTO;
