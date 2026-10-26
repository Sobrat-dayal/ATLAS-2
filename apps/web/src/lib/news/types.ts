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
