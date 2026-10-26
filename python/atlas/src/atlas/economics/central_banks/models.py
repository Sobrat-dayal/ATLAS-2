"""Domain Models for Central Bank Intelligence (Stage 91).

Defines institutional representations for central banks, monetary policy frameworks,
policy instruments, official rate decisions, meetings, voting records, official
publications, forward guidance, balance sheets, and policy programs.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from .enums import (
    CentralBankInstitutionKind,
    ForwardGuidanceKind,
    MeetingKind,
    PolicyCycleKind,
    PolicyDecisionKind,
    PolicyInstrumentCategory,
    PolicyProgramKind,
    PolicyRateRepresentationKind,
    PublicationKind,
    VotingOutcomeKind,
)


@dataclass
class CentralBankInstitution:
    """Canonical central banking institution authority."""
    central_bank_id: str
    canonical_name: str
    acronym: str
    institution_kind: CentralBankInstitutionKind
    primary_geography_id: str
    monetary_area_id: str
    currency_code: str
    official_website_url: str
    established_year: int
    headquarters_city: str
    primary_policy_committee: str
    is_active: bool = True
    supported_instruments_count: int = 1
    notes: Optional[str] = None


@dataclass
class MonetaryPolicyFramework:
    """Official mandate, operational strategy, and inflation target definition."""
    central_bank_id: str
    mandate_title: str
    mandate_summary: str
    operating_strategy: str
    inflation_target_metric: str
    inflation_target_pct: Optional[Decimal] = None
    target_lower_bound_pct: Optional[Decimal] = None
    target_upper_bound_pct: Optional[Decimal] = None
    target_tolerance_band: Optional[str] = None
    target_horizon: str = "Medium Term"
    effective_since: str = "2012"
    source_citation: str = "Official Central Bank Charter / Statutory Mandate"


@dataclass
class PolicyInstrument:
    """Administered monetary policy instrument."""
    instrument_id: str
    central_bank_id: str
    code: str
    name: str
    category: PolicyInstrumentCategory
    representation: PolicyRateRepresentationKind
    current_rate: Optional[Decimal] = None
    current_lower_bound: Optional[Decimal] = None
    current_upper_bound: Optional[Decimal] = None
    effective_date: str = "2024-11-08"
    canonical_series_id: Optional[str] = None
    operational_description: str = ""


@dataclass
class RateChangeMetric:
    """Rate change metrics in basis points for single rates and target ranges."""
    instrument_code: str
    previous_rate: Optional[Decimal] = None
    new_rate: Optional[Decimal] = None
    previous_lower_bound: Optional[Decimal] = None
    previous_upper_bound: Optional[Decimal] = None
    new_lower_bound: Optional[Decimal] = None
    new_upper_bound: Optional[Decimal] = None
    change_bps: Optional[Decimal] = None
    change_lower_bps: Optional[Decimal] = None
    change_upper_bps: Optional[Decimal] = None


@dataclass
class MonetaryPolicyDecision:
    """Official policy decision announcement and affected instruments."""
    decision_id: str
    official_identifier: str
    central_bank_id: str
    decision_kind: PolicyDecisionKind
    announced_at: datetime
    effective_at: date
    meeting_id: Optional[str]
    statement_document_id: Optional[str]
    affected_instruments: List[str]
    rate_changes: List[RateChangeMetric]
    policy_rationale: str
    source_revision: str = "REV-FINAL"
    publication_status: str = "OFFICIALLY_CONFIRMED"


@dataclass
class MonetaryPolicyMeeting:
    """Policy committee deliberation meeting."""
    meeting_id: str
    official_identifier: str
    central_bank_id: str
    meeting_kind: MeetingKind
    start_date: date
    end_date: date
    decision_ids: List[str] = field(default_factory=list)
    statement_document_id: Optional[str] = None
    minutes_document_id: Optional[str] = None
    minutes_published_at: Optional[datetime] = None
    voting_record_id: Optional[str] = None


@dataclass
class IndividualVote:
    """Single committee member vote on a policy decision."""
    member_name: str
    role_title: str
    vote: VotingOutcomeKind
    dissent_rationale: Optional[str] = None


@dataclass
class CommitteeVotingRecord:
    """Official recorded voting outcome of the policy committee."""
    record_id: str
    meeting_id: str
    decision_id: str
    votes_for: int
    votes_against: int
    votes_abstain: int
    individual_votes: List[IndividualVote] = field(default_factory=list)
    is_publicly_disclosed: bool = True
    source_reference: str = "Official Minutes of the Monetary Policy Meeting"


@dataclass
class OfficialPublication:
    """Authoritative central bank publication or decision statement."""
    document_id: str
    central_bank_id: str
    title: str
    publication_kind: PublicationKind
    published_at: datetime
    source_url: str
    media_type: str = "HTML"
    content_hash: str = ""
    sanitized_excerpt: str = ""
    source_revision: str = "v1.0"


@dataclass
class OfficialSpeech:
    """Official speech transcript delivered by a central bank policymaker."""
    speech_id: str
    central_bank_id: str
    speaker_name: str
    speaker_role: str
    title: str
    delivered_at: datetime
    published_at: datetime
    location: str
    source_url: str
    key_takeaway: str


@dataclass
class OfficialForwardGuidance:
    """Explicit source-grounded forward guidance extracted from official statements."""
    guidance_id: str
    central_bank_id: str
    source_document_id: str
    guidance_kind: ForwardGuidanceKind
    verbatim_excerpt: str
    explicit_conditions: str
    published_at: datetime
    status: str = "ACTIVE"


@dataclass
class BalanceSheetItem:
    """Balance sheet asset or liability position item."""
    item_id: str
    name: str
    category: str
    account_side: str
    value_billions: Decimal
    currency: str


@dataclass
class CentralBankBalanceSheetSummary:
    """Consolidated balance sheet assets, liabilities, and reserve balances."""
    central_bank_id: str
    reference_date: str
    reporting_frequency: str
    currency: str
    total_assets_billions: Decimal
    total_liabilities_billions: Decimal
    securities_holdings_billions: Decimal
    reserve_balances_billions: Decimal
    items: List[BalanceSheetItem] = field(default_factory=list)
    accounting_notes: str = ""


@dataclass
class CentralBankPolicyProgram:
    """Asset purchase (QE) or quantitative tightening (QT) balance sheet program."""
    program_id: str
    central_bank_id: str
    name: str
    program_kind: PolicyProgramKind
    announced_date: str
    effective_start: str
    effective_end: Optional[str] = None
    authorized_envelope_billions: Optional[Decimal] = None
    current_holdings_billions: Optional[Decimal] = None
    status: str = "ACTIVE"
    description: str = ""


@dataclass
class PolicyTimelineEvent:
    """Consolidated historical timeline event across decisions, meetings, and speeches."""
    event_id: str
    central_bank_id: str
    timestamp: datetime
    event_kind: str
    title: str
    summary: str
    instrument_code: Optional[str] = None
    rate_change_bps: Optional[Decimal] = None
    document_id: Optional[str] = None


@dataclass
class CentralBankOverview:
    """Unified master analytical overview for a selected central bank."""
    institution: CentralBankInstitution
    framework: MonetaryPolicyFramework
    instruments: List[PolicyInstrument]
    latest_decision: Optional[MonetaryPolicyDecision] = None
    latest_meeting: Optional[MonetaryPolicyMeeting] = None
    latest_balance_sheet: Optional[CentralBankBalanceSheetSummary] = None
    active_programs_count: int = 0
    active_forward_guidance: Optional[OfficialForwardGuidance] = None
    current_policy_cycle: PolicyCycleKind = PolicyCycleKind.HOLDING
    data_freshness_status: str = "VERIFIED_CURRENT"
