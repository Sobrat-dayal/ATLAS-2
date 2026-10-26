/**
 * Canonical TypeScript Types and DTOs for Institutional News Platform (Stage 99).
 */

export type NewsArticleType =
  | "NEWS_REPORT"
  | "WIRE_REPORT"
  | "PRESS_RELEASE"
  | "OFFICIAL_ANNOUNCEMENT"
  | "MARKET_COMMENTARY"
  | "OPINION"
  | "ANALYSIS";

export type NewsAvailabilityStatus =
  | "AVAILABLE"
  | "METADATA_ONLY"
  | "SOURCE_RESTRICTED"
  | "WITHDRAWN"
  | "REMOVED"
  | "SOURCE_UNAVAILABLE";

export type NewsLicensingStatus =
  | "FULL_DISPLAY"
  | "EXCERPT_ONLY"
  | "HEADLINE_ONLY"
  | "SUBSCRIPTION_REQUIRED"
  | "RESTRICTED";

export type NewsCategoryKey =
  | "GENERAL_FINANCIAL"
  | "COMPANY"
  | "EQUITIES"
  | "FIXED_INCOME"
  | "FOREIGN_EXCHANGE"
  | "COMMODITIES"
  | "ECONOMICS"
  | "CENTRAL_BANKS"
  | "REGULATION"
  | "CORPORATE_ACTIONS"
  | "TECHNOLOGY";

export interface NewsEntityMentionDTO {
  entity_id: string;
  entity_type: "COMPANY" | "INSTRUMENT" | "GEOGRAPHY" | "CENTRAL_BANK";
  canonical_name: string;
  ticker?: string | null;
  exchange?: string | null;
  country_code?: string | null;
  mention_type: string;
  resolution_method: string;
  verification_status: string;
}

export interface NewsArticleDTO {
  article_id: string;
  source_provider_id: string;
  publisher_id: string;
  publisher_name: string;
  publisher_article_id?: string | null;
  headline: string;
  permitted_excerpt?: string | null;
  original_url: string;
  canonical_url: string;
  language: string;
  article_type: NewsArticleType;
  published_at: string;
  source_updated_at?: string | null;
  first_seen_at: string;
  ingested_at: string;
  availability_status: NewsAvailabilityStatus;
  licensing_status: NewsLicensingStatus;
  categories: string[];
  linked_entities: NewsEntityMentionDTO[];
  geographies: string[];
  authors: string[];
  tags: string[];
  revision: number;
  is_duplicate: boolean;
  is_corrected: boolean;
  syndicated_from_id?: string | null;
  correction_details?: string | null;
  topic_ids?: string[];
  industries?: string[];
}

export interface NewsFeedResponseDTO {
  articles: NewsArticleDTO[];
  total_count: number;
  next_cursor?: string | null;
  has_more: boolean;
  as_of: string;
  active_filters: Record<string, unknown>;
}

export interface NewsPublisherDTO {
  publisher_id: string;
  canonical_name: string;
  verified_domain: string;
  publisher_type: string;
  country_code?: string | null;
  official_website: string;
  attribution_required: boolean;
  status: string;
}

export interface NewsSourceDTO {
  source_id: string;
  provider_name: string;
  provider_type: string;
  supported_content_types: string[];
  geographic_coverage: string[];
  update_cadence_seconds: number;
  latency_class: string;
  attribution_policy: string;
  excerpt_policy: string;
  health_status: string;
  last_successful_ingestion?: string | null;
}

export interface NewsCoverageResponseDTO {
  total_articles: number;
  active_sources: number;
  verified_publishers: number;
  supported_categories: string[];
  geographic_coverage: string[];
  latest_publication_time?: string | null;
  latest_ingestion_time?: string | null;
}

export interface NewsFreshnessResponseDTO {
  status: string;
  latency_class: string;
  last_successful_fetch?: string | null;
  latest_article_published?: string | null;
  latest_article_ingested?: string | null;
  staleness_seconds: number;
  active_source_count: number;
}

export interface NewsFeedQueryParams {
  category?: string;
  source_id?: string;
  publisher_id?: string;
  entity_id?: string;
  geography?: string;
  q?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  cursor?: string;
}

export type NewsTabKey =
  | "ALL"
  | "MARKETS"
  | "COMPANIES"
  | "ECONOMICS"
  | "CENTRAL_BANKS"
  | "REGULATION"
  | "TECHNOLOGY";

// ---------------------------------------------------------------------------
// Stage 100 Discovery, Facets, and Timeline Types
// ---------------------------------------------------------------------------

export type NewsDiscoveryMode =
  | "ALL"
  | "MARKETS"
  | "COMPANIES"
  | "SECURITIES"
  | "TOPICS"
  | "INDUSTRIES"
  | "WATCHLIST";

export type NewsTimelineInterval = "DAY" | "WEEK" | "MONTH";

export type NewsSortOrder =
  | "PUBLISHED_DESC"
  | "PUBLISHED_ASC"
  | "RELEVANCE_DESC";

export type NewsDatePreset =
  | "ALL_TIME"
  | "TODAY"
  | "PAST_24H"
  | "PAST_7D"
  | "PAST_30D"
  | "CUSTOM";

export interface NewsTopicDTO {
  topic_id: string;
  name: string;
  category: string;
  description: string;
  keywords: string[];
  importance: string;
  status: string;
}

export interface NewsFacetItemDTO {
  key: string;
  label: string;
  count: number;
}

export interface NewsFacetsResponseDTO {
  sources: NewsFacetItemDTO[];
  publishers: NewsFacetItemDTO[];
  categories: NewsFacetItemDTO[];
  topics: NewsFacetItemDTO[];
  countries: NewsFacetItemDTO[];
  article_types: NewsFacetItemDTO[];
  as_of: string;
}

export interface NewsTimelineBucketDTO {
  bucket_id: string;
  start_time: string;
  end_time: string;
  label: string;
  article_count: number;
  articles: NewsArticleDTO[];
}

export interface NewsTimelineRequestDTO {
  query?: NewsDiscoveryQueryDTO;
  interval?: NewsTimelineInterval;
  timezone?: string;
}

export interface NewsTimelineResponseDTO {
  interval: string;
  timezone: string;
  total_articles: number;
  total_buckets: number;
  buckets: NewsTimelineBucketDTO[];
  as_of: string;
}

export interface NewsSearchSuggestionDTO {
  suggestion_type: "COMPANY" | "TICKER" | "TOPIC" | "PUBLISHER" | "CATEGORY";
  key: string;
  label: string;
  secondary_label?: string | null;
  category?: string | null;
}

export interface NewsDiscoveryQueryDTO {
  mode?: NewsDiscoveryMode;
  entity_ids?: string[];
  tickers?: string[];
  topic_ids?: string[];
  industries?: string[];
  source_ids?: string[];
  publisher_ids?: string[];
  categories?: string[];
  countries?: string[];
  languages?: string[];
  article_types?: string[];
  query?: string;
  date_preset?: NewsDatePreset;
  start_date?: string;
  end_date?: string;
  sort_order?: NewsSortOrder;
  limit?: number;
  cursor?: string;
}

export interface NewsDiscoveryResponseDTO {
  articles: NewsArticleDTO[];
  total_count: number;
  next_cursor?: string | null;
  has_more: boolean;
  as_of: string;
  facets?: NewsFacetsResponseDTO | null;
  active_filters?: Record<string, unknown> | null;
}

// ---------------------------------------------------------------------------
// Stage 101 Story Intelligence & Financial Event Types
// ---------------------------------------------------------------------------

export type NewsStoryStatus =
  | "ACTIVE"
  | "DEVELOPING"
  | "QUIET"
  | "ARCHIVED"
  | "MERGED"
  | "WITHDRAWN_FROM_DISPLAY";

export type NewsStoryMembershipReason =
  | "EXACT_CANONICAL_DUPLICATE"
  | "SYNDICATED_WIRE_REPUBLICATION"
  | "SHARED_TRANSACTION_IDENTIFIER"
  | "SHARED_EVENT_IDENTITY"
  | "TOPIC_ENTITY_TEMPORAL_CLUSTER"
  | "MANUAL_CURATION_LINK";

export type NewsStoryMembershipStatus =
  | "CONFIRMED"
  | "PROVISIONAL"
  | "DISPUTED"
  | "SUPERSEDED";

export type FinancialEventType =
  | "EARNINGS_RELEASE"
  | "EARNINGS_GUIDANCE"
  | "DIVIDEND_DECLARATION"
  | "SHARE_REPURCHASE"
  | "MERGER_ACQUISITION_AGREEMENT"
  | "MERGER_ACQUISITION_PROPOSAL"
  | "MERGER_ACQUISITION_COMPLETION"
  | "MERGER_ACQUISITION_CANCELLATION"
  | "EQUITY_FINANCING"
  | "DEBT_FINANCING"
  | "EXECUTIVE_APPOINTMENT"
  | "EXECUTIVE_RESIGNATION"
  | "REGULATORY_ACTION"
  | "LITIGATION_FILING"
  | "BANKRUPTCY_RESTRUCTURING"
  | "PRODUCT_LAUNCH"
  | "FACILITY_EXPANSION"
  | "CENTRAL_BANK_POLICY_DECISION"
  | "ECONOMIC_RELEASE"
  | "GOVERNMENT_POLICY";

export type NewsEventLifecycleStatus =
  | "PROPOSED"
  | "ANNOUNCED"
  | "PENDING"
  | "APPROVED"
  | "COMPLETED"
  | "CANCELLED"
  | "WITHDRAWN"
  | "UNKNOWN";

export type NewsEventAssertionStatus =
  | "OFFICIALLY_REPORTED"
  | "THIRD_PARTY_REPORTED"
  | "ALLEGED"
  | "RUMORED"
  | "DENIED"
  | "DISPUTED"
  | "CORRECTED"
  | "UNRESOLVED";

export type EventParticipantRole =
  | "PRIMARY_SUBJECT"
  | "ACQUIRER"
  | "TARGET"
  | "SELLER"
  | "BUYER"
  | "ISSUER"
  | "LENDER"
  | "INVESTOR"
  | "UNDERWRITER"
  | "REGULATOR"
  | "SUBJECT"
  | "RESPONDENT"
  | "OFFICER";

export type EventAmountType =
  | "TRANSACTION_VALUE"
  | "DIVIDEND_PER_SHARE"
  | "BUYBACK_AUTHORIZATION"
  | "FINANCING_AMOUNT"
  | "INTEREST_RATE_TARGET"
  | "QUARTERLY_REVENUE"
  | "NET_INCOME"
  | "FINE_PENALTY_AMOUNT";

export type EventAmountApproximation =
  | "EXACT"
  | "APPROXIMATE"
  | "RANGE_MIN"
  | "RANGE_MAX"
  | "UNDISCLOSED";

export type EventTimePrecision =
  | "EXACT_INSTANT"
  | "CALENDAR_DAY"
  | "MONTH"
  | "YEAR"
  | "UNKNOWN";

export type NewsEvidenceType =
  | "OFFICIAL_PRESS_RELEASE"
  | "REGULATORY_FILING"
  | "CENTRAL_BANK_RELEASE"
  | "PUBLISHER_REPORT"
  | "WIRE_REPORT"
  | "THIRD_PARTY_STATEMENT";

export interface NewsStoryArticleLinkDTO {
  story_id: string;
  article_id: string;
  publisher_id: string;
  published_at: string;
  headline: string;
  membership_reason: NewsStoryMembershipReason;
  membership_status: NewsStoryMembershipStatus;
  is_primary_anchor: boolean;
  linked_at: string;
}

export interface NewsStoryThreadDTO {
  story_id: string;
  display_title: string;
  canonical_topic_label?: string | null;
  topic_ids: string[];
  primary_entity_id?: string | null;
  primary_entity_name?: string | null;
  related_entities: NewsEntityMentionDTO[];
  first_source_published_at: string;
  latest_source_published_at: string;
  first_seen_at: string;
  latest_activity_at: string;
  story_status: NewsStoryStatus;
  article_count: number;
  independent_publisher_count: number;
  publishers: string[];
  article_ids: string[];
  representative_article_id: string;
  clustering_method: string;
  clustering_version: string;
  linked_event_ids: string[];
}

export interface NewsStoryFeedResponseDTO {
  stories: NewsStoryThreadDTO[];
  total_count: number;
  next_cursor?: string | null;
  has_more: boolean;
  as_of: string;
}

export interface EventParticipantDTO {
  entity_id: string;
  canonical_name: string;
  role: EventParticipantRole;
  resolution_status: string;
}

export interface EventAmountDTO {
  amount_type: EventAmountType;
  amount_value: number;
  currency: string;
  period?: string | null;
  approximation_status: EventAmountApproximation;
  source_text?: string | null;
}

export interface NewsEventEvidenceDTO {
  evidence_id: string;
  event_id: string;
  article_id: string;
  publisher_id: string;
  publisher_name: string;
  source_provider_id: string;
  evidence_type: NewsEvidenceType;
  headline: string;
  permitted_excerpt?: string | null;
  source_published_at: string;
  first_observed_at: string;
  is_verified_by_filing: boolean;
  filing_id?: string | null;
}

export interface NewsEventRevisionDTO {
  revision_id: string;
  event_id: string;
  timestamp: string;
  previous_lifecycle_status?: NewsEventLifecycleStatus | null;
  new_lifecycle_status: NewsEventLifecycleStatus;
  previous_assertion_status?: NewsEventAssertionStatus | null;
  new_assertion_status: NewsEventAssertionStatus;
  change_reason: string;
  evidence_id?: string | null;
}

export interface NewsFinancialEventDTO {
  event_id: string;
  event_type: FinancialEventType;
  event_title: string;
  primary_entity_id: string;
  primary_entity_name: string;
  lifecycle_status: NewsEventLifecycleStatus;
  assertion_status: NewsEventAssertionStatus;
  event_date?: string | null;
  event_time_precision: EventTimePrecision;
  announcement_time?: string | null;
  first_seen_at: string;
  last_evidence_updated_at: string;
  participants: EventParticipantDTO[];
  amounts: EventAmountDTO[];
  supporting_article_ids: string[];
  evidence_records: NewsEventEvidenceDTO[];
  linked_story_ids: string[];
  revisions: NewsEventRevisionDTO[];
  is_disputed: boolean;
  is_corrected: boolean;
}

export interface NewsEventFeedResponseDTO {
  events: NewsFinancialEventDTO[];
  total_count: number;
  next_cursor?: string | null;
  has_more: boolean;
  as_of: string;
}

export interface FinancialEventTypeDefinitionDTO {
  event_type_id: FinancialEventType;
  canonical_label: string;
  event_family: string;
  description: string;
  supported_roles: EventParticipantRole[];
  supported_amount_types: EventAmountType[];
}

// =========================================================================
// STAGE 102: Financial Sentiment, Relevance & Market Reaction Analytics
// =========================================================================

export type NewsSentimentLabel =
  | "POSITIVE"
  | "NEGATIVE"
  | "NEUTRAL"
  | "MIXED"
  | "INSUFFICIENT_EVIDENCE"
  | "NOT_APPLICABLE";

export type NewsFinancialAspect =
  | "EARNINGS_PERFORMANCE"
  | "EARNINGS_GUIDANCE"
  | "REVENUE_GROWTH"
  | "PROFITABILITY"
  | "CASH_FLOW"
  | "BALANCE_SHEET"
  | "DEBT_FINANCING"
  | "CORPORATE_GOVERNANCE"
  | "REGULATORY_EXPOSURE"
  | "PRODUCT_DEVELOPMENT"
  | "OPERATIONAL_PERFORMANCE"
  | "MANAGEMENT"
  | "CORPORATE_TRANSACTION"
  | "GENERAL";

export type NewsEntityRelevanceClass =
  | "PRIMARY_SUBJECT"
  | "DIRECT_PARTICIPANT"
  | "VERIFIED_MENTION"
  | "VERIFIED_RELATED_ENTITY"
  | "CONTEXTUAL_MARKET_REFERENCE"
  | "INSUFFICIENT_EVIDENCE";

export type NewsEvidenceScope =
  | "HEADLINE"
  | "LICENSED_EXCERPT"
  | "LICENSED_BODY"
  | "STRUCTURED_FILING";

export type NewsClassificationMethod =
  | "DETERMINISTIC_RULES"
  | "APPROVED_FINANCIAL_LLM"
  | "HYBRID"
  | "FALLBACK_ABSTAIN";

export type NewsMarketReactionWindow =
  | "PREV_CLOSE_TO_NEXT_CLOSE"
  | "PUB_BAR_TO_NEXT_BAR"
  | "PREV_SESSION_TO_SUBSEQUENT_SESSION"
  | "INTRADAY_ONE_HOUR"
  | "INTRADAY_FOUR_HOURS";

export interface SentimentEvidenceReferenceDTO {
  evidence_id: string;
  article_id: string;
  revision_id: string;
  evidence_scope: NewsEvidenceScope;
  text_span: string;
  aspect: NewsFinancialAspect;
  rationale_code: string;
}

export interface NewsSentimentAnnotationDTO {
  annotation_id: string;
  article_id: string;
  article_revision_id: string;
  target_entity_id: string;
  target_entity_type: string;
  target_canonical_name?: string | null;
  target_ticker?: string | null;
  sentiment_label: NewsSentimentLabel;
  sentiment_score: number;
  confidence_score: number;
  sentiment_aspect: NewsFinancialAspect;
  classification_status: string;
  analysis_method: NewsClassificationMethod;
  model_or_rule_version: string;
  source_published_at: string;
  analysis_created_at: string;
  evidence: SentimentEvidenceReferenceDTO[];
  explanation: string;
}

export interface NewsEntityRelevanceDTO {
  relevance_id: string;
  article_id: string;
  entity_id: string;
  entity_type: string;
  canonical_name?: string | null;
  ticker?: string | null;
  relevance_class: NewsEntityRelevanceClass;
  relevance_score: number;
  evidence_source: string;
  relationship_type: string;
  resolution_method: string;
  source_published_at: string;
}

export interface EntitySentimentAggregateDTO {
  target_entity_id: string;
  target_canonical_name?: string | null;
  target_ticker?: string | null;
  evaluation_window_days: number;
  eligible_count: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  mixed_count: number;
  insufficient_evidence_count: number;
  net_sentiment: number;
  unique_story_count: number;
  independent_publisher_count: number;
  top_aspects: Array<{ aspect: string; count: number }>;
  coverage_completeness: string;
  methodology_version: string;
  evaluation_time: string;
}

export interface SentimentTimelineBucketDTO {
  bucket_start: string;
  bucket_end: string;
  label: string;
  eligible_count: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  mixed_count: number;
  net_sentiment: number;
}

export interface SentimentTimelineResponseDTO {
  target_entity_id: string;
  interval: string;
  days: number;
  total_eligible: number;
  buckets: SentimentTimelineBucketDTO[];
}

export interface StorySentimentProfileDTO {
  story_id: string;
  target_entity_id: string;
  distribution: Record<string, number>;
  net_sentiment: number;
  eligible_article_count: number;
  independent_source_count: number;
  evaluation_time: string;
}

export interface EventSentimentProfileDTO {
  event_id: string;
  target_entity_id: string;
  distribution: Record<string, number>;
  net_sentiment: number;
  eligible_evidence_count: number;
  assertion_status: string;
  evaluation_time: string;
}

export interface ObservedNewsMarketContextDTO {
  context_id: string;
  article_id_or_event_id: string;
  instrument_id: string;
  ticker: string;
  market_id: string;
  window_type: NewsMarketReactionWindow;
  publication_time: string;
  window_start_time: string;
  window_end_time: string;
  price_start: number;
  price_end: number;
  observed_return: number;
  observed_return_pct: number;
  benchmark_id?: string | null;
  benchmark_return?: number | null;
  benchmark_relative_return?: number | null;
  currency: string;
  is_descriptive_only: boolean;
  noncausal_disclaimer: string;
  limitations: string[];
  data_source: string;
}

export interface MarketReactionRequestDTO {
  article_id_or_event_id: string;
  instrument_id: string;
  ticker: string;
  publication_time: string;
  window_type?: NewsMarketReactionWindow;
  market_id?: string;
  benchmark_id?: string;
}

export interface SentimentEvaluationResultDTO {
  evaluation_version: string;
  evaluated_at: string;
  total_samples: number;
  per_class_precision: Record<string, number>;
  per_class_recall: Record<string, number>;
  per_class_f1: Record<string, number>;
  macro_f1: number;
  accuracy: number;
  target_resolution_accuracy: number;
  abstention_rate: number;
  confusion_matrix: Record<string, Record<string, number>>;
  methodology: string;
}


