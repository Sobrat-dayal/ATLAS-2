"""Domain models for Company Earnings Intelligence (Stage 84).

Models verified corporate earnings announcements, reported results, analyst consensus
estimates, pre-release cutoffs, management guidance, and earnings call references.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

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


@dataclass
class EarningsEvent:
    """Represents a scheduled, completed, or revised corporate earnings event."""
    event_id: str
    company_id: uuid.UUID
    fiscal_period: str
    fiscal_year: int
    fiscal_quarter: Optional[str]
    event_type: EarningsEventType = EarningsEventType.EARNINGS_RELEASE
    status: EarningsEventStatus = EarningsEventStatus.CONFIRMED
    period_start: Optional[datetime.date] = None
    period_end: Optional[datetime.date] = None
    announced_date: Optional[datetime.date] = None
    announced_time: Optional[datetime.time] = None
    timezone: str = "America/New_York"
    market_session: MarketSession = MarketSession.UNSPECIFIED
    is_confirmed: bool = True
    source: str = "CANONICAL"
    conference_call_time: Optional[datetime.datetime] = None
    webcast_url: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class EarningsActual:
    """Represents reported financial facts from an official corporate earnings release."""
    actual_id: str
    company_id: uuid.UUID
    fiscal_period: str
    period_type: EarningsPeriodType
    diluted_eps: Optional[Decimal] = None
    basic_eps: Optional[Decimal] = None
    adjusted_eps: Optional[Decimal] = None
    revenue: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    reporting_currency: str = "USD"
    accounting_basis: AccountingBasis = AccountingBasis.GAAP
    is_restated: bool = False
    announcement_date: Optional[datetime.date] = None
    reported_at: Optional[datetime.datetime] = None
    source_statement_id: Optional[str] = None
    source_revision: str = "v1"


@dataclass
class ConsensusSnapshot:
    """Represents a qualified analyst consensus estimate snapshot."""
    consensus_id: str
    company_id: uuid.UUID
    fiscal_period: str
    period_type: EarningsPeriodType
    consensus_eps: Optional[Decimal] = None
    consensus_revenue: Optional[Decimal] = None
    eps_high: Optional[Decimal] = None
    eps_low: Optional[Decimal] = None
    revenue_high: Optional[Decimal] = None
    revenue_low: Optional[Decimal] = None
    analyst_count: int = 0
    methodology: str = "MEAN"
    snapshot_timestamp: Optional[datetime.datetime] = None
    pre_release_cutoff: bool = True
    source_provider: str = "CANONICAL_CONSENSUS"


@dataclass
class EarningsSurprise:
    """Represents the computed surprise metrics between actual and pre-release consensus."""
    fiscal_period: str
    actual_eps: Optional[Decimal]
    estimate_eps: Optional[Decimal]
    eps_surprise_abs: Optional[Decimal]
    eps_surprise_pct: Optional[Decimal]
    eps_classification: SurpriseClassification
    actual_revenue: Optional[Decimal]
    estimate_revenue: Optional[Decimal]
    revenue_surprise_abs: Optional[Decimal]
    revenue_surprise_pct: Optional[Decimal]
    revenue_classification: SurpriseClassification
    calculation_version: str = "v1.0"


@dataclass
class ManagementGuidance:
    """Represents company-issued management forward financial guidance."""
    guidance_id: str
    company_id: uuid.UUID
    fiscal_period: str
    metric: GuidanceMetricType
    low_value: Optional[Decimal] = None
    high_value: Optional[Decimal] = None
    point_value: Optional[Decimal] = None
    currency: str = "USD"
    accounting_basis: AccountingBasis = AccountingBasis.GAAP
    issued_at: datetime.date = field(default_factory=datetime.date.today)
    status: GuidanceStatus = GuidanceStatus.ACTIVE
    notes: Optional[str] = None
    source_document: Optional[str] = None


@dataclass
class EarningsCall:
    """Represents an earnings conference call and associated transcript references."""
    call_id: str
    company_id: uuid.UUID
    fiscal_period: str
    call_datetime: Optional[datetime.datetime] = None
    timezone: str = "America/New_York"
    webcast_url: Optional[str] = None
    transcript_document_id: Optional[str] = None
    transcript_status: TranscriptStatus = TranscriptStatus.AVAILABLE
    audio_available: bool = False
    key_topics: List[str] = field(default_factory=list)
