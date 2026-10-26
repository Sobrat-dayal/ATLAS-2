/**
 * TypeScript Data Transfer Objects (DTOs) and Enums for Central Bank Intelligence (Stage 91).
 */

export type CentralBankInstitutionKind =
  | "CENTRAL_BANK"
  | "FEDERAL_CENTRAL_BANK"
  | "SUPRANATIONAL_CENTRAL_BANK"
  | "NATIONAL_CENTRAL_BANK"
  | "MONETARY_AUTHORITY"
  | "CURRENCY_BOARD"
  | "REGIONAL_RESERVE_BANK";

export type PolicyRateRepresentationKind =
  | "SINGLE_RATE"
  | "SINGLE_TARGET_RATE"
  | "TARGET_RANGE"
  | "CORRIDOR_FACILITIES"
  | "ADMINISTERED_BENCHMARK";

export type PolicyInstrumentCategory =
  | "PRIMARY_POLICY_RATE"
  | "TARGET_RANGE"
  | "DEPOSIT_FACILITY"
  | "DEPOSIT_FACILITY_RATE"
  | "LENDING_FACILITY"
  | "LENDING_FACILITY_RATE"
  | "REFINANCING_OPERATION"
  | "REFINANCING_RATE"
  | "DISCOUNT_WINDOW"
  | "REPO_RATE"
  | "REVERSE_REPO_RATE"
  | "OVERNIGHT_CALL_RATE"
  | "OVERNIGHT_RATE_TARGET"
  | "RESERVE_REMUNERATION_RATE"
  | "LOAN_PRIME_RATE"
  | "OTHER_ADMINISTERED_RATE";

export type PolicyDecisionKind =
  | "RATE_INCREASE"
  | "RATE_DECREASE"
  | "RATE_HOLD"
  | "MULTI_INSTRUMENT_CHANGE"
  | "ASSET_PURCHASE_CHANGE"
  | "FRAMEWORK_CHANGE";

export type MeetingKind =
  | "REGULAR_POLICY_MEETING"
  | "EXTRAORDINARY_MEETING"
  | "EMERGENCY_MEETING"
  | "UNSCHEDULED_INTERMEETING";

export type VotingOutcomeKind =
  | "FOR"
  | "AGAINST"
  | "ABSTAIN"
  | "ABSENT"
  | "NOT_DISCLOSED";

export type PublicationKind =
  | "POLICY_DECISION_STATEMENT"
  | "MONETARY_POLICY_MINUTES"
  | "MONETARY_POLICY_REPORT"
  | "ECONOMIC_PROJECTIONS"
  | "PRESS_RELEASE"
  | "SPEECH_TRANSCRIPT"
  | "BALANCE_SHEET_RELEASE";

export type ForwardGuidanceKind =
  | "DATE_BASED"
  | "STATE_CONTINGENT"
  | "QUALITATIVE_OUTLOOK"
  | "REACTION_FUNCTION"
  | "POLICY_REACTION_FRAMEWORK"
  | "OUTLOOK_STATEMENT"
  | "NOT_APPLICABLE";

export type PolicyCycleKind =
  | "TIGHTENING"
  | "EASING"
  | "HOLDING"
  | "TRANSITIONAL"
  | "MIXED_OR_TRANSITIONAL"
  | "UNKNOWN";

export type PolicyProgramKind =
  | "ASSET_PURCHASE_PROGRAM"
  | "BALANCE_SHEET_RUNOFF"
  | "REINVESTMENT_POLICY"
  | "LIQUIDITY_FACILITY"
  | "TARGETED_REFINANCING";

export interface CentralBankInstitutionDTO {
  central_bank_id: string;
  canonical_name: string;
  acronym: string;
  institution_kind: CentralBankInstitutionKind;
  primary_geography_id: string;
  monetary_area_id: string;
  currency_code: string;
  official_website_url: string;
  established_year: number;
  headquarters_city: string;
  primary_policy_committee: string;
  is_active: boolean;
  supported_instruments_count: number;
  notes?: string | null;
}

export interface MonetaryPolicyFrameworkDTO {
  central_bank_id: string;
  mandate_title: string;
  mandate_summary: string;
  operating_strategy: string;
  inflation_target_metric: string;
  inflation_target_pct?: number | null;
  target_lower_bound_pct?: number | null;
  target_upper_bound_pct?: number | null;
  target_tolerance_band?: string | null;
  target_horizon: string;
  effective_since: string;
  source_citation: string;
}

export interface PolicyInstrumentDTO {
  instrument_id: string;
  central_bank_id: string;
  code: string;
  name: string;
  category: PolicyInstrumentCategory;
  representation: PolicyRateRepresentationKind;
  current_rate?: number | null;
  current_lower_bound?: number | null;
  current_upper_bound?: number | null;
  effective_date: string;
  canonical_series_id?: string | null;
  operational_description: string;
}

export interface RateChangeMetricDTO {
  instrument_code: string;
  previous_rate?: number | null;
  new_rate?: number | null;
  previous_lower_bound?: number | null;
  previous_upper_bound?: number | null;
  new_lower_bound?: number | null;
  new_upper_bound?: number | null;
  change_bps?: number | null;
  change_lower_bps?: number | null;
  change_upper_bps?: number | null;
}

export interface MonetaryPolicyDecisionDTO {
  decision_id: string;
  official_identifier: string;
  central_bank_id: string;
  decision_kind: PolicyDecisionKind;
  announced_at: string;
  effective_at: string;
  meeting_id?: string | null;
  statement_document_id?: string | null;
  affected_instruments: string[];
  rate_changes: RateChangeMetricDTO[];
  policy_rationale: string;
  source_revision: string;
  publication_status: string;
}

export interface MonetaryPolicyMeetingDTO {
  meeting_id: string;
  official_identifier: string;
  central_bank_id: string;
  meeting_kind: MeetingKind;
  start_date: string;
  end_date: string;
  decision_ids: string[];
  statement_document_id?: string | null;
  minutes_document_id?: string | null;
  minutes_published_at?: string | null;
  voting_record_id?: string | null;
}

export interface IndividualVoteDTO {
  member_name: string;
  role_title: string;
  vote: VotingOutcomeKind;
  dissent_rationale?: string | null;
}

export interface CommitteeVotingRecordDTO {
  record_id: string;
  meeting_id: string;
  decision_id: string;
  votes_for: number;
  votes_against: number;
  votes_abstain: number;
  individual_votes: IndividualVoteDTO[];
  is_publicly_disclosed: boolean;
  source_reference: string;
}

export interface OfficialPublicationDTO {
  document_id: string;
  central_bank_id: string;
  title: string;
  publication_kind: PublicationKind;
  published_at: string;
  source_url: string;
  media_type: string;
  content_hash: string;
  sanitized_excerpt: string;
  source_revision: string;
}

export interface OfficialSpeechDTO {
  speech_id: string;
  central_bank_id: string;
  speaker_name: string;
  speaker_role: string;
  title: string;
  delivered_at: string;
  published_at: string;
  location: string;
  source_url: string;
  key_takeaway: string;
}

export interface OfficialForwardGuidanceDTO {
  guidance_id: string;
  central_bank_id: string;
  source_document_id: string;
  guidance_kind: ForwardGuidanceKind;
  verbatim_excerpt: string;
  explicit_conditions: string;
  published_at: string;
  status: string;
}

export interface BalanceSheetItemDTO {
  item_id: string;
  name: string;
  category: string;
  account_side: string;
  value_billions: number;
  currency: string;
}

export interface CentralBankBalanceSheetSummaryDTO {
  central_bank_id: string;
  reference_date: string;
  reporting_frequency: string;
  currency: string;
  total_assets_billions: number;
  total_liabilities_billions: number;
  securities_holdings_billions: number;
  reserve_balances_billions: number;
  items: BalanceSheetItemDTO[];
  accounting_notes: string;
}

export interface CentralBankPolicyProgramDTO {
  program_id: string;
  central_bank_id: string;
  name: string;
  program_kind: PolicyProgramKind;
  announced_date: string;
  effective_start: string;
  effective_end?: string | null;
  authorized_envelope_billions?: number | null;
  current_holdings_billions?: number | null;
  status: string;
  description: string;
}

export interface PolicyTimelineEventDTO {
  event_id: string;
  central_bank_id: string;
  timestamp: string;
  event_kind: string;
  title: string;
  summary: string;
  instrument_code?: string | null;
  rate_change_bps?: number | null;
  document_id?: string | null;
}

export interface CentralBankOverviewDTO {
  institution: CentralBankInstitutionDTO;
  framework: MonetaryPolicyFrameworkDTO;
  instruments: PolicyInstrumentDTO[];
  latest_decision?: MonetaryPolicyDecisionDTO | null;
  latest_meeting?: MonetaryPolicyMeetingDTO | null;
  latest_balance_sheet?: CentralBankBalanceSheetSummaryDTO | null;
  active_programs_count: number;
  active_forward_guidance?: OfficialForwardGuidanceDTO | null;
  current_policy_cycle: PolicyCycleKind;
  data_freshness_status: string;
}

export interface CentralBankCoverageResponseDTO {
  central_bank_id: string;
  institution: CentralBankInstitutionDTO;
  has_policy_rate_series: boolean;
  has_target_range: boolean;
  has_decision_history: boolean;
  has_meeting_minutes: boolean;
  has_voting_records: boolean;
  has_official_statements: boolean;
  has_official_speeches: boolean;
  has_forward_guidance: boolean;
  has_balance_sheet: boolean;
  has_policy_programs: boolean;
}
