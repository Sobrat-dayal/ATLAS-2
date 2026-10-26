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
