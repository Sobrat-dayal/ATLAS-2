/**
 * ATLAS Stage 132: Corporate Geography and Facility Mapping Types.
 */

export type CorporateFacilityType =
  | "CORPORATE_HEADQUARTERS"
  | "REGISTERED_OFFICE"
  | "REGIONAL_HEADQUARTERS"
  | "CORPORATE_OFFICE"
  | "MANUFACTURING_FACILITY"
  | "ASSEMBLY_FACILITY"
  | "RESEARCH_AND_DEVELOPMENT"
  | "DISTRIBUTION_CENTER"
  | "WAREHOUSE"
  | "CORPORATE_CAMPUS"
  | "CUSTOMER_SUPPORT_CENTER"
  | "SERVICE_CENTER"
  | "OTHER_VERIFIED_FACILITY";

export type CorporateFacilityStatus =
  | "ANNOUNCED"
  | "PLANNED"
  | "UNDER_CONSTRUCTION"
  | "OPERATIONAL"
  | "TEMPORARILY_CLOSED"
  | "PERMANENTLY_CLOSED"
  | "SOLD"
  | "RELOCATED"
  | "HISTORICAL"
  | "STATUS_UNKNOWN";

export type GeographicPrecisionClass =
  | "VERIFIED_SITE_POINT"
  | "VERIFIED_SITE_POLYGON"
  | "VERIFIED_STREET_ADDRESS"
  | "GEOCODED_ADDRESS_APPROXIMATE"
  | "LOCALITY_CENTROID"
  | "ADMINISTRATIVE_REGION_ONLY"
  | "COUNTRY_ONLY"
  | "LOCATION_UNRESOLVED";

export type FacilityRelationshipType =
  | "OWNED_BY"
  | "OPERATED_BY"
  | "LEASED_BY"
  | "OCCUPIED_BY"
  | "MANAGED_BY"
  | "HEADQUARTERS_OF"
  | "REGISTERED_ADDRESS_OF"
  | "ANNOUNCED_BY"
  | "FORMERLY_OPERATED_BY";

export type VerificationStatus =
  | "VERIFIED"
  | "CORROBORATED"
  | "SOURCE_REPORTED"
  | "UNVERIFIED"
  | "CONFLICTED"
  | "REJECTED";

export interface FacilityEntityLink {
  link_id: string;
  facility_id: string;
  legal_entity_id: string;
  company_id: string;
  relationship_type: FacilityRelationshipType;
  role_description?: string;
  ownership_percentage?: number | null;
  valid_from?: string | null;
  valid_to?: string | null;
  source_manifest_id?: string;
  verification_status: VerificationStatus;
}

export interface FacilityEvidenceClaim {
  claim_id: string;
  facility_id: string;
  subject_entity_id: string;
  predicate: string;
  source_title: string;
  source_document_id: string;
  publisher: string;
  publication_date: string;
  exact_evidence_span: string;
  document_url?: string | null;
  licensing_policy: string;
  verification_status: VerificationStatus;
}

export interface FacilityStatusHistory {
  history_id: string;
  facility_id: string;
  status: CorporateFacilityStatus;
  valid_from?: string | null;
  valid_to?: string | null;
  source_manifest_id?: string;
  verification_status: VerificationStatus;
  recorded_at: string;
}

export interface CorporateFacility {
  facility_id: string;
  canonical_name: string;
  facility_type: CorporateFacilityType;
  facility_status: CorporateFacilityStatus;
  precision_class: GeographicPrecisionClass;
  country_code: string;
  administrative_region?: string;
  locality?: string;
  address_text?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  geometry_type: string;
  coordinates?: any;
  primary_entity_id: string;
  operating_start_date?: string | null;
  operating_end_date?: string | null;
  source_manifest_id: string;
  verification_status: VerificationStatus;
  is_public: boolean;
  links: FacilityEntityLink[];
  evidence_claims: FacilityEvidenceClaim[];
  status_history: FacilityStatusHistory[];
}

export interface CompanyFootprintSummary {
  company_id: string;
  canonical_name: string;
  ticker?: string | null;
  total_facilities: number;
  distinct_facilities: number;
  countries_count: number;
  facility_type_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
  direct_facilities_count: number;
  subsidiary_facilities_count: number;
  unresolved_locations_count: number;
  source_coverage: {
    sources_count?: number;
    sources_list?: string[];
    coverage_disclaimer?: string;
    countries?: Array<{ country_code: string; count: number }>;
  };
}

export interface CompanyFootprintResponse {
  company_id: string;
  canonical_entity_reference: {
    entity_id: string;
    canonical_name: string;
    legal_name?: string | null;
    ticker?: string | null;
    lei?: string | null;
    cik?: string | null;
    country_code?: string | null;
  };
  scope: "direct" | "subsidiary_inclusive";
  facilities: CorporateFacility[];
  summary: CompanyFootprintSummary;
  historical_as_of?: string | null;
  generated_at: string;
}

export interface CompanyComparisonResult {
  company_a: CompanyFootprintSummary;
  company_b: CompanyFootprintSummary;
  shared_countries: string[];
  unique_countries_a: string[];
  unique_countries_b: string[];
  type_comparison: Record<string, Record<string, number>>;
  as_of?: string | null;
}

export interface MappedCompanySearchResult {
  entity_id: string;
  company_id: string;
  canonical_name: string;
  legal_name?: string | null;
  tickers?: string[];
  lei?: string | null;
  cik?: string | null;
  primary_country_code?: string;
  organization_type?: string;
  status?: string;
}

