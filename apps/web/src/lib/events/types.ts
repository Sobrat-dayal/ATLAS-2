/**
 * Universal Event Model TypeScript Domain Types (Stage 135)
 */

export type EventCategory =
  | 'FINANCIAL'
  | 'CORPORATE'
  | 'ECONOMIC'
  | 'MONETARY_POLICY'
  | 'REGULATORY'
  | 'SANCTIONS'
  | 'GEOPOLITICAL'
  | 'NEWS_REPORTED'
  | 'NATURAL_DISASTER'
  | 'PHYSICAL_WORLD'
  | 'INFRASTRUCTURE'
  | 'OTHER_VERIFIED_EVENT';

export type EventLifecycleStatus =
  | 'SCHEDULED'
  | 'PROPOSED'
  | 'ANNOUNCED'
  | 'REPORTED'
  | 'OCCURRED'
  | 'CONFIRMED'
  | 'POSTPONED'
  | 'CANCELLED'
  | 'SUPERSEDED'
  | 'RETRACTED'
  | 'DISPUTED'
  | 'STATUS_UNKNOWN';

export type EventVerificationStatus =
  | 'OFFICIALLY_CONFIRMED'
  | 'INDEPENDENTLY_CORROBORATED'
  | 'SOURCE_REPORTED'
  | 'UNVERIFIED'
  | 'CONFLICTED'
  | 'REJECTED';

export type DatePrecision =
  | 'EXACT_TIMESTAMP'
  | 'DATE_ONLY'
  | 'MONTH_ONLY'
  | 'YEAR_ONLY'
  | 'TIME_UNKNOWN';

export type EvidenceRole =
  | 'PRIMARY_SOURCE'
  | 'OFFICIAL_CONFIRMATION'
  | 'CORROBORATING_SOURCE'
  | 'CONTRADICTING_SOURCE'
  | 'CORRECTION_SOURCE'
  | 'RETRACTION_SOURCE'
  | 'CONTEXTUAL_SOURCE';

export type ClaimConflictStatus =
  | 'NO_CONFLICT'
  | 'MINOR_DISCREPANCY'
  | 'CONFLICTED'
  | 'CONFLICT_DETECTED'
  | 'RESOLVED';

export type GeographicScopeType =
  | 'POINT'
  | 'COORDINATES'
  | 'POLYGON'
  | 'MULTIPOLYGON'
  | 'ADMINISTRATIVE_AREA'
  | 'REGION'
  | 'CONTINENT'
  | 'COUNTRY'
  | 'GLOBAL'
  | 'GLOBAL_SCOPE'
  | 'UNKNOWN';

export interface EventGeographicScope {
  scope_type: GeographicScopeType;
  country_code?: string | null;
  jurisdiction?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  location_name?: string | null;
  coordinates?: number[] | null;
  geometry?: Record<string, unknown> | null;
  area_name?: string | null;
}

export interface EventSourceRecord {
  source_record_id: string;
  source_id: string;
  publisher: string;
  title: string;
  original_url?: string | null;
  published_at?: string | null;
  retrieved_at: string;
  source_version?: number;
  license_name?: string;
  retention_policy?: string;
  access_policy?: string;
  attribution?: string;
}

export interface EventEvidence {
  evidence_id: string;
  event_id: string;
  source_record_id: string;
  evidence_role: EvidenceRole;
  source_version?: number;
  verification_status: EventVerificationStatus;
  snippet?: string | null;
  locator?: string | null;
  recorded_at: string;
}

export interface EventClaim {
  claim_id: string;
  event_id: string;
  source_record_id: string;
  predicate: string;
  claim_value: unknown;
  value_type: string;
  units?: string | null;
  qualifiers?: Record<string, unknown>;
  published_at?: string | null;
  extracted_at: string;
  verification_status: EventVerificationStatus;
}

export interface EventRevision {
  event_revision_id: string;
  event_id: string;
  revision_number: number;
  changed_fields: Record<string, unknown>;
  previous_revision_id?: string | null;
  reason: string;
  recorded_at: string;
  published_at?: string | null;
}

export interface AtlasUniversalEvent {
  event_id: string;
  canonical_event_key: string;
  event_type: string;
  event_subtype: string;
  event_category: EventCategory;
  title: string;
  factual_summary: string;
  lifecycle_status: EventLifecycleStatus;
  verification_status: EventVerificationStatus;
  occurred_at?: string | null;
  date_precision: DatePrecision;
  announced_at?: string | null;
  scheduled_for?: string | null;
  effective_at?: string | null;
  source_published_at?: string | null;
  first_public_at?: string | null;
  first_observed_at?: string | null;
  first_ingested_at: string;
  updated_at: string;
  geographic_scope: EventGeographicScope;
  primary_source_id: string;
  event_payload: Record<string, unknown>;
  source_count: number;
  claim_conflict_status: ClaimConflictStatus;
  current_revision_number: number;
  schema_version: string;
  tenant_id?: string | null;
  aliases: string[];
  tags: string[];
  is_retracted: boolean;
  retraction_reason?: string | null;
}

export interface EventSearchParams {
  query?: string;
  categories?: EventCategory[];
  event_types?: string[];
  lifecycle_statuses?: EventLifecycleStatus[];
  verification_statuses?: EventVerificationStatus[];
  jurisdictions?: string[];
  entities?: string[];
  time_clock?: string;
  start_date?: string;
  end_date?: string;
  include_retracted?: boolean;
  tenant_id?: string;
  limit?: number;
  offset?: number;
}

export interface EventSearchResult {
  total_count: number;
  returned_count: number;
  offset: number;
  limit: number;
  events: AtlasUniversalEvent[];
}

export interface TimelineBucket {
  bucket_date: string;
  event_count: number;
  events: AtlasUniversalEvent[];
}

export interface TimelineResponse {
  clock_used: string;
  total_events: number;
  buckets: TimelineBucket[];
  events: AtlasUniversalEvent[];
}

export interface ReviewItem {
  review_id: string;
  event_a_id: string;
  event_b_id: string;
  reason: string;
  status: 'PENDING' | 'RESOLVED' | 'DISMISSED';
  context: Record<string, unknown>;
  created_at: string;
  resolved_at?: string | null;
  resolved_by?: string | null;
  resolution?: string | null;
}
