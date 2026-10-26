"""Pydantic schemas and DTOs for Company Earnings Intelligence (Stage 84).

Conforms to standard ATLAS API response formats with strict serialization.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from atlas.companies.earnings.enums import (
    AccountingBasis,
    EarningsEventStatus,
    EarningsEventType,
    EarningsPeriodType,
    GuidanceMetricType,
    GuidanceStatus,
    MarketSession,
    SurpriseClassification,
    TranscriptStatus,
)


class EarningsEventDTO(BaseModel):
    """Event announcement schedule record."""
    event_id: str
    company_id: str
    fiscal_period: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None
    event_type: EarningsEventType
    status: EarningsEventStatus
    announced_date: Optional[str] = None
    announced_time: Optional[str] = None
    timezone: str = "America/New_York"
    market_session: MarketSession = MarketSession.UNSPECIFIED
    is_confirmed: bool = True
    source: str = "CANONICAL"
    webcast_url: Optional[str] = None


class EarningsActualDTO(BaseModel):
    """Reported actual results from earnings release."""
    actual_id: str
    fiscal_period: str
    period_type: EarningsPeriodType
    diluted_eps: Optional[float] = None
    basic_eps: Optional[float] = None
    adjusted_eps: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    formatted_diluted_eps: str = "—"
    formatted_revenue: str = "—"
    reporting_currency: str = "USD"
    accounting_basis: AccountingBasis = AccountingBasis.GAAP
    is_restated: bool = False
    announcement_date: Optional[str] = None


class ConsensusSnapshotDTO(BaseModel):
    """Analyst consensus estimate expectation snapshot."""
    consensus_id: str
    fiscal_period: str
    period_type: EarningsPeriodType
    consensus_eps: Optional[float] = None
    consensus_revenue: Optional[float] = None
    formatted_eps: str = "—"
    formatted_revenue: str = "—"
    eps_high: Optional[float] = None
    eps_low: Optional[float] = None
    revenue_high: Optional[float] = None
    revenue_low: Optional[float] = None
    analyst_count: int = 0
    methodology: str = "MEAN"
    snapshot_timestamp: Optional[str] = None
    pre_release_cutoff: bool = True


class EarningsSurpriseDTO(BaseModel):
    """Derived surprise between actual result and consensus."""
    fiscal_period: str
    eps_surprise_abs: Optional[float] = None
    eps_surprise_pct: Optional[float] = None
    formatted_eps_surprise: str = "—"
    eps_classification: SurpriseClassification = SurpriseClassification.UNAVAILABLE
    revenue_surprise_abs: Optional[float] = None
    revenue_surprise_pct: Optional[float] = None
    formatted_revenue_surprise: str = "—"
    revenue_classification: SurpriseClassification = SurpriseClassification.UNAVAILABLE


class QuarterlyEarningsItemDTO(BaseModel):
    """Integrated row combining period, event, actual, estimate, and surprise."""
    fiscal_period: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None
    announced_date: Optional[str] = None
    market_session: MarketSession = MarketSession.UNSPECIFIED
    status: EarningsEventStatus = EarningsEventStatus.COMPLETED
    # EPS Metrics
    actual_eps: Optional[float] = None
    formatted_actual_eps: str = "—"
    estimate_eps: Optional[float] = None
    formatted_estimate_eps: str = "—"
    eps_surprise_abs: Optional[float] = None
    eps_surprise_pct: Optional[float] = None
    formatted_eps_surprise_pct: str = "—"
    eps_classification: SurpriseClassification = SurpriseClassification.UNAVAILABLE
    # Revenue Metrics
    actual_revenue: Optional[float] = None
    formatted_actual_revenue: str = "—"
    estimate_revenue: Optional[float] = None
    formatted_estimate_revenue: str = "—"
    revenue_surprise_abs: Optional[float] = None
    revenue_surprise_pct: Optional[float] = None
    formatted_revenue_surprise_pct: str = "—"
    revenue_classification: SurpriseClassification = SurpriseClassification.UNAVAILABLE
    # Metadata
    currency: str = "USD"
    is_restated: bool = False
    source: str = "CANONICAL"


class ManagementGuidanceDTO(BaseModel):
    """Company-issued management forward financial guidance."""
    guidance_id: str
    fiscal_period: str
    metric: GuidanceMetricType
    low_value: Optional[float] = None
    high_value: Optional[float] = None
    point_value: Optional[float] = None
    formatted_range: str = "—"
    currency: str = "USD"
    accounting_basis: AccountingBasis = AccountingBasis.GAAP
    issued_at: str
    status: GuidanceStatus = GuidanceStatus.ACTIVE
    notes: Optional[str] = None
    source_document: Optional[str] = None


class EarningsCallDTO(BaseModel):
    """Earnings conference call and transcript metadata."""
    call_id: str
    fiscal_period: str
    call_datetime: Optional[str] = None
    timezone: str = "America/New_York"
    webcast_url: Optional[str] = None
    transcript_document_id: Optional[str] = None
    transcript_status: TranscriptStatus = TranscriptStatus.AVAILABLE
    audio_available: bool = False
    key_topics: List[str] = Field(default_factory=list)


class CompanyEarningsOverviewDTO(BaseModel):
    """High-level summary of latest reported and next upcoming earnings."""
    company_id: str
    company_name: str
    latest_completed: Optional[QuarterlyEarningsItemDTO] = None
    next_scheduled: Optional[EarningsEventDTO] = None
    next_consensus: Optional[ConsensusSnapshotDTO] = None
    active_guidance: List[ManagementGuidanceDTO] = Field(default_factory=list)
    latest_call: Optional[EarningsCallDTO] = None
    recent_history: List[QuarterlyEarningsItemDTO] = Field(default_factory=list)


class EarningsHistoryResponseDTO(BaseModel):
    """Response containing chronological multi-period earnings history."""
    company_id: str
    company_name: str
    period_type: EarningsPeriodType
    total_count: int
    items: List[QuarterlyEarningsItemDTO]


class EarningsEventsResponseDTO(BaseModel):
    """Response containing scheduled and completed earnings events."""
    company_id: str
    company_name: str
    total_count: int
    events: List[EarningsEventDTO]


class GuidanceResponseDTO(BaseModel):
    """Response containing company management guidance items."""
    company_id: str
    company_name: str
    total_count: int
    guidance_items: List[ManagementGuidanceDTO]


class EarningsCallsResponseDTO(BaseModel):
    """Response containing earnings call records and transcript links."""
    company_id: str
    company_name: str
    total_count: int
    calls: List[EarningsCallDTO]
