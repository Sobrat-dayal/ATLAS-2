/**
 * Canonical Types for ATLAS Stage 81: Companies V1
 */

export interface CompanyIdentity {
  company_entity_id: string;
  entity_type: "company";
  canonical_name: string;
  display_name: string;
  legal_name: string | null;
  short_name: string | null;
  organization_type: string | null;
  status: string | null;
  founded_date: string | null;
  website_url: string | null;
  aliases: string[];
}

export interface CompanyIdentifierItem {
  identifier_id?: string | null;
  scheme_key: string;
  scheme_name: string;
  value: string;
  normalized_value: string;
  namespace?: string | null;
  is_current: boolean;
  valid_from?: string | null;
  valid_to?: string | null;
  source: string;
  verification_status: string;
}

export interface CompanyClassification {
  taxonomy: string;
  taxonomy_version?: string | null;
  sector_code?: string | null;
  sector_name?: string | null;
  industry_code?: string | null;
  industry_name?: string | null;
  source: string;
  as_of?: string | null;
  status: "AVAILABLE" | "UNAVAILABLE" | "PARTIAL";
}

export interface CompanyGeography {
  headquarters_city?: string | null;
  headquarters_country?: string | null;
  country_code?: string | null;
  country_entity_id?: string | null;
  incorporation_jurisdiction?: string | null;
  domicile_country?: string | null;
  address_text?: string | null;
  source: string;
  status: "AVAILABLE" | "UNAVAILABLE" | "PARTIAL";
}

export interface RelatedSecurityItem {
  instrument_entity_id: string;
  canonical_name: string;
  display_name: string;
  symbol?: string | null;
  asset_class: string;
  security_type: string;
  share_class_name?: string | null;
  exchange_or_venue?: string | null;
  currency: string;
  relationship_type: string;
  is_current: boolean;
  is_primary_listing: boolean;

  // Latest Quote Snapshot
  is_quote_available: boolean;
  quote_measure?: string | null;
  latest_price?: string | null;
  bid_price?: string | null;
  ask_price?: string | null;
  absolute_change?: string | null;
  percentage_change?: string | null;
  change_direction: "up" | "down" | "flat";
  source_timestamp?: string | null;
  provider?: string | null;
  freshness_status: string;
  delay_status: string;
  delay_seconds?: number | null;
}

export interface CompanyMarketSummary {
  reference_security_id?: string | null;
  reference_symbol?: string | null;
  reference_venue?: string | null;
  reference_price?: string | null;
  market_cap?: string | null;
  market_cap_currency?: string | null;
  market_cap_as_of?: string | null;
  market_cap_source?: string | null;
  market_cap_methodology?: string | null;
  total_securities_count: number;
  listed_equity_count: number;
  bond_count: number;
  status: "AVAILABLE" | "UNAVAILABLE" | "PARTIAL";
}

export interface FinancialSummaryMetric {
  metric_key: string;
  metric_name: string;
  value?: string | null;
  raw_value?: number | null;
  unit?: string | null;
  scale?: string | null;
  fiscal_period?: string | null;
  period_end_date?: string | null;
  publication_date?: string | null;
  consolidation_scope: string;
  restatement_status: string;
  source: string;
  status: "AVAILABLE" | "UNAVAILABLE" | "PARTIAL";
}

export interface CompanyFinancialSummary {
  reporting_currency: string;
  fiscal_period?: string | null;
  period_end_date?: string | null;
  publication_date?: string | null;
  consolidation_scope: string;
  metrics: FinancialSummaryMetric[];
  status: "AVAILABLE" | "UNAVAILABLE" | "PARTIAL" | "NOT_ENTITLED";
}

export interface CompanyNewsReference {
  title: string;
  publisher: string;
  published_at: string;
  url?: string | null;
  summary?: string | null;
  authors: string[];
  source: string;
}

export interface CompanyDocumentReference {
  document_id?: string | null;
  title: string;
  document_kind?: string | null;
  publication_date?: string | null;
  url?: string | null;
  language_code?: string | null;
  authors: string[];
  source: string;
}

export interface SectionAvailability {
  identity: string;
  profile: string;
  classification: string;
  geography: string;
  identifiers: string;
  securities: string;
  market_summary: string;
  financial_summary: string;
  news: string;
  documents: string;
}

export interface CompanyOverviewResponse {
  company_entity_id: string;
  identity: CompanyIdentity;
  description?: string | null;
  classification: CompanyClassification;
  geography: CompanyGeography;
  identifiers: CompanyIdentifierItem[];
  related_securities: RelatedSecurityItem[];
  market_summary: CompanyMarketSummary;
  financial_summary: CompanyFinancialSummary;
  recent_news: CompanyNewsReference[];
  documents: CompanyDocumentReference[];
  section_availability: SectionAvailability;
  created_at: string;
  updated_at: string;
}

export interface CompanySearchResult {
  company_entity_id: string;
  canonical_name: string;
  display_name: string;
  legal_name?: string | null;
  primary_ticker?: string | null;
  country?: string | null;
  country_code?: string | null;
  sector?: string | null;
  industry?: string | null;
  organization_type?: string | null;
  status?: string | null;
  has_public_securities: boolean;
}

export interface CompanySearchResponse {
  results: CompanySearchResult[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaginatedSecuritiesResponse {
  results: RelatedSecurityItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaginatedNewsResponse {
  results: CompanyNewsReference[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaginatedDocumentsResponse {
  results: CompanyDocumentReference[];
  total: number;
  page: number;
  page_size: number;
}
