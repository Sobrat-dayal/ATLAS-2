"""Pydantic V2 API Schemas for Corporate Geography and Facility Intelligence (Stage 132)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class FacilityEntityLinkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    link_id: str
    facility_id: str
    legal_entity_id: str
    company_id: str
    relationship_type: str
    role_description: str = ""
    ownership_percentage: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    source_manifest_id: str = ""
    verification_status: str


class FacilityEvidenceClaimSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    claim_id: str
    facility_id: str
    subject_entity_id: str
    predicate: str
    source_title: str
    source_document_id: str
    publisher: str
    publication_date: str
    exact_evidence_span: str
    document_url: Optional[str] = None
    licensing_policy: str = "authorized_disclosure"
    verification_status: str


class FacilityStatusHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    history_id: str
    facility_id: str
    status: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    source_manifest_id: str = ""
    verification_status: str
    recorded_at: str


class CorporateFacilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    facility_id: str
    canonical_name: str
    facility_type: str
    facility_status: str
    precision_class: str
    country_code: str
    administrative_region: str = ""
    locality: str = ""
    address_text: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    geometry_type: str = "POINT"
    coordinates: Optional[Any] = None
    primary_entity_id: str = ""
    operating_start_date: Optional[str] = None
    operating_end_date: Optional[str] = None
    source_manifest_id: str = ""
    verification_status: str
    is_public: bool = True
    links: list[FacilityEntityLinkSchema] = Field(default_factory=list)
    evidence_claims: list[FacilityEvidenceClaimSchema] = Field(default_factory=list)
    status_history: list[FacilityStatusHistorySchema] = Field(default_factory=list)


class CompanyFootprintSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: str
    canonical_name: str
    ticker: Optional[str] = None
    total_facilities: int
    distinct_facilities: int
    countries_count: int
    facility_type_breakdown: dict[str, int]
    status_breakdown: dict[str, int]
    direct_facilities_count: int
    subsidiary_facilities_count: int
    unresolved_locations_count: int
    source_coverage: dict[str, Any]


class CompanyFootprintResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: str
    canonical_entity_reference: dict[str, Any]
    scope: str
    facilities: list[CorporateFacilitySchema]
    summary: CompanyFootprintSummarySchema
    historical_as_of: Optional[str] = None
    generated_at: str


class CompanyComparisonRequestSchema(BaseModel):
    company_a_id: str
    company_b_id: str
    include_subsidiaries: bool = True
    as_of: Optional[str] = None


class CompanyComparisonResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_a: CompanyFootprintSummarySchema
    company_b: CompanyFootprintSummarySchema
    shared_countries: list[str]
    unique_countries_a: list[str]
    unique_countries_b: list[str]
    type_comparison: dict[str, dict[str, int]]
    as_of: Optional[str] = None


class FacilitySpatialQueryRequestSchema(BaseModel):
    query: Optional[str] = None
    company_id: Optional[str] = None
    include_subsidiaries: bool = True
    facility_types: Optional[list[str]] = None
    statuses: Optional[list[str]] = None
    country_code: Optional[str] = None
    bbox: Optional[list[float]] = None  # [min_lon, min_lat, max_lon, max_lat]
    as_of: Optional[str] = None
    limit: int = 500


class FacilityAggregateRequestSchema(BaseModel):
    company_id: Optional[str] = None
    include_subsidiaries: bool = True
    resolution: int = 4
    facility_types: Optional[list[str]] = None
    as_of: Optional[str] = None


class FacilityCorrectionRequestSchema(BaseModel):
    facility_id: str
    correction_type: str
    details: str


class FacilityCorrectionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    correction_id: str
    facility_id: str
    user_id: str
    correction_type: str
    details: str
    status: str
    submitted_at: str

