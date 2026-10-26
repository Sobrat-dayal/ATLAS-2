"""Pydantic request and response schemas for Company Ownership Intelligence (Stage 85).

Defines strongly-typed DTOs for ownership overviews, security share classes,
institutional holders, corporate insiders, beneficial owners, shareholding patterns,
historical snapshots, position changes, and disclosure provenance.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import (
    DisclosureType,
    HolderCategory,
    Jurisdiction,
    OwnershipForm,
    PositionChangeStatus,
    PositionType,
)


class HolderSummaryDTO(BaseModel):
    """Canonical shareholder summary."""
    holder_entity_id: str
    name: str
    category: HolderCategory
    reporting_party: Optional[str] = None
    country: Optional[str] = None
    is_institution: bool = False
    is_insider: bool = False
    is_promoter: bool = False


class SecuritySummaryDTO(BaseModel):
    """Issuing company security and share-class definition."""
    security_id: str
    security_name: str
    ticker: Optional[str] = None
    share_class: str = "Common Stock"
    is_primary: bool = True
    shares_outstanding: float = 0.0
    formatted_shares_outstanding: str = "—"


class OwnershipPositionDTO(BaseModel):
    """Disclosed security holding record."""
    position_id: str
    company_id: str
    security_id: str
    security_name: str
    share_class: str
    holder: HolderSummaryDTO
    shares_held: float
    formatted_shares: str = "—"
    position_type: PositionType = PositionType.COMMON_SHARES
    ownership_form: OwnershipForm = OwnershipForm.DIRECT
    source_reported_percentage: Optional[float] = None
    calculated_percentage: Optional[float] = None
    formatted_percentage: str = "—"
    voting_percentage: Optional[float] = None
    reporting_date: str = ""
    filing_date: str = ""
    filing_delay_days: int = 0
    disclosure_type: DisclosureType = DisclosureType.FORM_13F
    jurisdiction: Jurisdiction = Jurisdiction.US_SEC
    source_document_id: Optional[str] = None
    is_amendment: bool = False
    notes: Optional[str] = None


class InstitutionalHoldingDTO(BaseModel):
    """13F or institutional manager reported position."""
    position_id: str
    holder: HolderSummaryDTO
    shares_held: float
    formatted_shares: str = "—"
    calculated_percentage: Optional[float] = None
    formatted_percentage: str = "—"
    shares_change: float = 0.0
    formatted_shares_change: str = "—"
    change_status: PositionChangeStatus = PositionChangeStatus.UNCHANGED
    indicative_value_formatted: str = "—"
    reporting_date: str = ""
    filing_date: str = ""
    source_document_id: Optional[str] = None


class InsiderHoldingDTO(BaseModel):
    """Form 3/4/5 officer, director, or 10% insider reported position."""
    position_id: str
    holder: HolderSummaryDTO
    insider_role: str = "Corporate Insider"
    is_officer: bool = False
    is_director: bool = False
    is_ten_percent_owner: bool = False
    ownership_form: OwnershipForm = OwnershipForm.DIRECT
    shares_held: float
    formatted_shares: str = "—"
    calculated_percentage: Optional[float] = None
    formatted_percentage: str = "—"
    reporting_date: str = ""
    filing_date: str = ""
    source_document_id: Optional[str] = None
    notes: Optional[str] = None


class BeneficialOwnerDTO(BaseModel):
    """Schedule 13D/13G beneficial owner holding >=5% voting/economic interest."""
    position_id: str
    holder: HolderSummaryDTO
    shares_held: float
    formatted_shares: str = "—"
    calculated_percentage: Optional[float] = None
    formatted_percentage: str = "—"
    sole_voting_power: Optional[float] = None
    shared_voting_power: Optional[float] = None
    sole_dispositive_power: Optional[float] = None
    shared_dispositive_power: Optional[float] = None
    reporting_date: str = ""
    filing_date: str = ""
    disclosure_type: DisclosureType = DisclosureType.SCHEDULE_13G
    source_document_id: Optional[str] = None


class PatternCategoryDTO(BaseModel):
    """Category in a standardized shareholding pattern."""
    category_name: str
    shares_held: float
    formatted_shares: str = "—"
    percentage_of_total: float
    formatted_percentage: str = "—"
    pledged_percentage: Optional[float] = None
    shareholder_count: Optional[int] = None


class ShareholdingPatternDTO(BaseModel):
    """Jurisdiction-specific shareholding pattern breakdown."""
    company_id: str
    reporting_period: str
    reporting_date: str
    jurisdiction: Jurisdiction = Jurisdiction.GLOBAL_OTHER
    categories: List[PatternCategoryDTO] = Field(default_factory=list)


class OwnershipConcentrationDTO(BaseModel):
    """Ownership concentration analytics."""
    top_1_shares: float = 0.0
    top_1_formatted: str = "—"
    top_1_pct: Optional[float] = None
    top_5_shares: float = 0.0
    top_5_formatted: str = "—"
    top_5_pct: Optional[float] = None
    top_10_shares: float = 0.0
    top_10_formatted: str = "—"
    top_10_pct: Optional[float] = None
    total_disclosed_shares: float = 0.0
    total_disclosed_formatted: str = "—"
    total_disclosed_pct: Optional[float] = None
    shares_outstanding: float = 0.0
    shares_outstanding_formatted: str = "—"


class OwnershipChangeDTO(BaseModel):
    """Historical position change between two reporting snapshots."""
    holder: HolderSummaryDTO
    prior_shares: float
    current_shares: float
    shares_change: float
    formatted_shares_change: str = "—"
    percentage_change: Optional[float] = None
    formatted_percentage_change: str = "—"
    prior_ownership_pct: Optional[float] = None
    current_ownership_pct: Optional[float] = None
    pp_change: Optional[float] = None
    status: PositionChangeStatus = PositionChangeStatus.UNCHANGED


class HistoricalOwnershipSnapshotDTO(BaseModel):
    """Point-in-time snapshot summary for a historical period."""
    snapshot_id: str
    reporting_period: str
    reporting_date: str
    filing_date: str
    shares_outstanding: float
    formatted_shares_outstanding: str = "—"
    institutional_shares: float = 0.0
    institutional_pct: Optional[float] = None
    insider_shares: float = 0.0
    insider_pct: Optional[float] = None
    holder_count: int = 0


class CompanyOwnershipOverviewDTO(BaseModel):
    """Executive ownership intelligence overview."""
    company_id: str
    company_name: str
    selected_security: SecuritySummaryDTO
    available_securities: List[SecuritySummaryDTO] = Field(default_factory=list)
    reporting_period: str
    reporting_date: str
    filing_date: str
    source_coverage: str = "SEC Form 13F & 13D/13G Disclosures"
    concentration: OwnershipConcentrationDTO
    top_holders: List[OwnershipPositionDTO] = Field(default_factory=list)
    institutional_summary: Dict[str, Any] = Field(default_factory=dict)
    insider_summary: Dict[str, Any] = Field(default_factory=dict)
    beneficial_summary: Dict[str, Any] = Field(default_factory=dict)
    patterns: Optional[ShareholdingPatternDTO] = None


class OwnershipHoldersResponseDTO(BaseModel):
    """Paginated collection of disclosed positions."""
    company_id: str
    total_count: int
    items: List[OwnershipPositionDTO] = Field(default_factory=list)


class InstitutionalHoldingsResponseDTO(BaseModel):
    """Collection of institutional holdings."""
    company_id: str
    total_count: int
    reporting_period: str
    reporting_date: str
    items: List[InstitutionalHoldingDTO] = Field(default_factory=list)


class InsiderHoldingsResponseDTO(BaseModel):
    """Collection of corporate insider holdings."""
    company_id: str
    total_count: int
    reporting_date: str
    items: List[InsiderHoldingDTO] = Field(default_factory=list)


class BeneficialOwnersResponseDTO(BaseModel):
    """Collection of >=5% beneficial owners."""
    company_id: str
    total_count: int
    reporting_date: str
    items: List[BeneficialOwnerDTO] = Field(default_factory=list)


class OwnershipHistoryResponseDTO(BaseModel):
    """Historical ownership snapshots sequence."""
    company_id: str
    total_count: int
    snapshots: List[HistoricalOwnershipSnapshotDTO] = Field(default_factory=list)


class OwnershipChangesResponseDTO(BaseModel):
    """Comparative position changes between two quarters."""
    company_id: str
    prior_period: str
    current_period: str
    total_count: int
    changes: List[OwnershipChangeDTO] = Field(default_factory=list)


class OwnershipSecuritiesResponseDTO(BaseModel):
    """List of securities and share classes for the company."""
    company_id: str
    securities: List[SecuritySummaryDTO] = Field(default_factory=list)
