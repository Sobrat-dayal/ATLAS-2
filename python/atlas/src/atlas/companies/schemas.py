import uuid
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .types import CompanyStatus, OrganizationType


# ---------------------------------------------------------------------------
# Section Availability & Status Codes
# ---------------------------------------------------------------------------
class SectionAvailability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    identity: str = Field(default="AVAILABLE", description="Status of identity section")
    profile: str = Field(default="AVAILABLE", description="Status of profile section")
    classification: str = Field(default="AVAILABLE", description="Status of classification section")
    geography: str = Field(default="AVAILABLE", description="Status of geography section")
    identifiers: str = Field(default="AVAILABLE", description="Status of identifiers section")
    securities: str = Field(default="AVAILABLE", description="Status of securities section")
    market_summary: str = Field(default="AVAILABLE", description="Status of market summary section")
    financial_summary: str = Field(default="AVAILABLE", description="Status of financial summary section")
    news: str = Field(default="AVAILABLE", description="Status of news section")
    documents: str = Field(default="AVAILABLE", description="Status of documents section")


# ---------------------------------------------------------------------------
# Company Identity & Aliases
# ---------------------------------------------------------------------------
class CompanyIdentity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_entity_id: uuid.UUID
    entity_type: Literal["company"] = "company"
    canonical_name: str
    display_name: str
    legal_name: Optional[str] = None
    short_name: Optional[str] = None
    organization_type: Optional[str] = None
    status: Optional[str] = None
    founded_date: Optional[date] = None
    website_url: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Corporate Identifiers (LEI, CIK, etc.)
# ---------------------------------------------------------------------------
class CompanyIdentifierItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    identifier_id: Optional[uuid.UUID] = None
    scheme_key: str
    scheme_name: str
    value: str
    normalized_value: str
    namespace: Optional[str] = None
    is_current: bool = True
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    source: str = "canonical"
    verification_status: str = "verified"


# ---------------------------------------------------------------------------
# Sector & Industry Classification
# ---------------------------------------------------------------------------
class CompanyClassification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    taxonomy: str = Field(default="GICS", description="Classification taxonomy (e.g. GICS, ICB, NAICS, SIC)")
    taxonomy_version: Optional[str] = Field(default="2023", description="Taxonomy release version")
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    source: str = "canonical"
    as_of: Optional[datetime] = None
    status: str = "AVAILABLE"


# ---------------------------------------------------------------------------
# Geographic Information
# ---------------------------------------------------------------------------
class CompanyGeography(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    headquarters_city: Optional[str] = None
    headquarters_country: Optional[str] = None
    country_code: Optional[str] = None
    country_entity_id: Optional[uuid.UUID] = None
    incorporation_jurisdiction: Optional[str] = None
    domicile_country: Optional[str] = None
    address_text: Optional[str] = None
    source: str = "canonical"
    status: str = "AVAILABLE"


# ---------------------------------------------------------------------------
# Company-to-Security Relationships (Listed Equities, Share Classes, Bonds)
# ---------------------------------------------------------------------------
class RelatedSecurityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    instrument_entity_id: uuid.UUID
    canonical_name: str
    display_name: str
    symbol: Optional[str] = None
    asset_class: str = "equity"  # equity, bond, etc.
    security_type: str = "common_equity"  # common_equity, preferred_equity, depositary_receipt, corporate_bond
    share_class_name: Optional[str] = None  # Class A, Class B, Common, etc.
    exchange_or_venue: Optional[str] = None
    currency: str = "USD"
    relationship_type: str = "issued"  # issued, issued_by
    is_current: bool = True
    is_primary_listing: bool = False

    # Qualified Latest Quote Snapshot
    is_quote_available: bool = False
    quote_measure: Optional[str] = None  # Last, Bid, Ask, Mid, NAV, Clean Price, Yield
    latest_price: Optional[str] = None
    bid_price: Optional[str] = None
    ask_price: Optional[str] = None
    absolute_change: Optional[str] = None
    percentage_change: Optional[str] = None
    change_direction: str = "flat"  # up, down, flat
    source_timestamp: Optional[datetime] = None
    provider: Optional[str] = None
    freshness_status: str = "unknown"
    delay_status: str = "realtime"
    delay_seconds: Optional[int] = None


# ---------------------------------------------------------------------------
# Market Summary & Context
# ---------------------------------------------------------------------------
class CompanyMarketSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference_security_id: Optional[uuid.UUID] = None
    reference_symbol: Optional[str] = None
    reference_venue: Optional[str] = None
    reference_price: Optional[str] = None
    market_cap: Optional[str] = None
    market_cap_currency: Optional[str] = None
    market_cap_as_of: Optional[datetime] = None
    market_cap_source: Optional[str] = None
    market_cap_methodology: Optional[str] = None
    total_securities_count: int = 0
    listed_equity_count: int = 0
    bond_count: int = 0
    status: str = "AVAILABLE"


# ---------------------------------------------------------------------------
# Financial Summary (Stage 34 Fundamental Data)
# ---------------------------------------------------------------------------
class FinancialSummaryMetric(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_key: str
    metric_name: str
    value: Optional[str] = None
    raw_value: Optional[float] = None
    unit: Optional[str] = None
    scale: Optional[str] = None  # billions, millions, exact
    fiscal_period: Optional[str] = None  # FY2025, Q3 FY2026
    period_end_date: Optional[date] = None
    publication_date: Optional[date] = None
    consolidation_scope: str = "consolidated"
    restatement_status: str = "original"
    source: str = "canonical"
    status: str = "AVAILABLE"


class CompanyFinancialSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reporting_currency: str = "USD"
    fiscal_period: Optional[str] = None
    period_end_date: Optional[date] = None
    publication_date: Optional[date] = None
    consolidation_scope: str = "consolidated"
    metrics: List[FinancialSummaryMetric] = Field(default_factory=list)
    status: str = "AVAILABLE"


# ---------------------------------------------------------------------------
# News & Document References (Stage 36 / 20)
# ---------------------------------------------------------------------------
class CompanyNewsReference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    publisher: str
    published_at: datetime
    url: Optional[str] = None
    summary: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    source: str = "canonical"


class CompanyDocumentReference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: Optional[uuid.UUID] = None
    title: str
    document_kind: Optional[str] = None  # annual_report, 10-k, 10-q, research_report
    publication_date: Optional[date] = None
    url: Optional[str] = None
    language_code: Optional[str] = "en"
    authors: List[str] = Field(default_factory=list)
    source: str = "canonical"


# ---------------------------------------------------------------------------
# Full Canonical Company Overview Response
# ---------------------------------------------------------------------------
class CompanyOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_entity_id: uuid.UUID
    identity: CompanyIdentity
    description: Optional[str] = None
    classification: CompanyClassification
    geography: CompanyGeography
    identifiers: List[CompanyIdentifierItem] = Field(default_factory=list)
    related_securities: List[RelatedSecurityItem] = Field(default_factory=list)
    market_summary: CompanyMarketSummary
    financial_summary: CompanyFinancialSummary
    recent_news: List[CompanyNewsReference] = Field(default_factory=list)
    documents: List[CompanyDocumentReference] = Field(default_factory=list)
    section_availability: SectionAvailability
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Search and Discovery Schemas
# ---------------------------------------------------------------------------
class CompanySearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_entity_id: uuid.UUID
    canonical_name: str
    display_name: str
    legal_name: Optional[str] = None
    primary_ticker: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    organization_type: Optional[str] = None
    status: Optional[str] = None
    has_public_securities: bool = False


class CompanySearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: List[CompanySearchResult]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Paginated Secondary Endpoints Schemas
# ---------------------------------------------------------------------------
class PaginatedSecuritiesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: List[RelatedSecurityItem]
    total: int
    page: int
    page_size: int


class PaginatedNewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: List[CompanyNewsReference]
    total: int
    page: int
    page_size: int


class PaginatedDocumentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: List[CompanyDocumentReference]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Legacy Response for Backwards Compatibility
# ---------------------------------------------------------------------------
class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: Literal["company"] = "company"
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    legal_name: Optional[str] = None
    short_name: Optional[str] = None
    organization_type: Optional[OrganizationType] = None
    status: Optional[CompanyStatus] = None
    founded_date: Optional[date] = None
    website_url: Optional[str] = None
    primary_country_entity_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
