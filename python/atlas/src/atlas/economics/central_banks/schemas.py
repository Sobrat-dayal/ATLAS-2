"""Pydantic V2 Schemas and DTOs for Central Bank Intelligence (Stage 91)."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

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


class CentralBankInstitutionDTO(BaseModel):
    """Institutional central banking authority metadata."""
    model_config = ConfigDict(from_attributes=True)

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
    is_active: bool
    supported_instruments_count: int
    notes: Optional[str] = None


class MonetaryPolicyFrameworkDTO(BaseModel):
    """Monetary policy mandate and inflation target framework."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    mandate_title: str
    mandate_summary: str
    operating_strategy: str
    inflation_target_metric: str
    inflation_target_pct: Optional[float] = None
    target_lower_bound_pct: Optional[float] = None
    target_upper_bound_pct: Optional[float] = None
    target_tolerance_band: Optional[str] = None
    target_horizon: str
    effective_since: str
    source_citation: str


class PolicyInstrumentDTO(BaseModel):
    """Administered policy interest rate instrument."""
    model_config = ConfigDict(from_attributes=True)

    instrument_id: str
    central_bank_id: str
    code: str
    name: str
    category: PolicyInstrumentCategory
    representation: PolicyRateRepresentationKind
    current_rate: Optional[float] = None
    current_lower_bound: Optional[float] = None
    current_upper_bound: Optional[float] = None
    effective_date: str
    canonical_series_id: Optional[str] = None
    operational_description: str


class RateChangeMetricDTO(BaseModel):
    """Rate change calculations in basis points."""
    model_config = ConfigDict(from_attributes=True)

    instrument_code: str
    previous_rate: Optional[float] = None
    new_rate: Optional[float] = None
    previous_lower_bound: Optional[float] = None
    previous_upper_bound: Optional[float] = None
    new_lower_bound: Optional[float] = None
    new_upper_bound: Optional[float] = None
    change_bps: Optional[float] = None
    change_lower_bps: Optional[float] = None
    change_upper_bps: Optional[float] = None


class MonetaryPolicyDecisionDTO(BaseModel):
    """Official policy decision announcement."""
    model_config = ConfigDict(from_attributes=True)

    decision_id: str
    official_identifier: str
    central_bank_id: str
    decision_kind: PolicyDecisionKind
    announced_at: datetime
    effective_at: date
    meeting_id: Optional[str] = None
    statement_document_id: Optional[str] = None
    affected_instruments: List[str]
    rate_changes: List[RateChangeMetricDTO]
    policy_rationale: str
    source_revision: str
    publication_status: str


class MonetaryPolicyMeetingDTO(BaseModel):
    """Policy committee deliberation meeting record."""
    model_config = ConfigDict(from_attributes=True)

    meeting_id: str
    official_identifier: str
    central_bank_id: str
    meeting_kind: MeetingKind
    start_date: date
    end_date: date
    decision_ids: List[str]
    statement_document_id: Optional[str] = None
    minutes_document_id: Optional[str] = None
    minutes_published_at: Optional[datetime] = None
    voting_record_id: Optional[str] = None


class IndividualVoteDTO(BaseModel):
    """Individual committee member vote."""
    model_config = ConfigDict(from_attributes=True)

    member_name: str
    role_title: str
    vote: VotingOutcomeKind
    dissent_rationale: Optional[str] = None


class CommitteeVotingRecordDTO(BaseModel):
    """Official voting split and dissenting records."""
    model_config = ConfigDict(from_attributes=True)

    record_id: str
    meeting_id: str
    decision_id: str
    votes_for: int
    votes_against: int
    votes_abstain: int
    individual_votes: List[IndividualVoteDTO]
    is_publicly_disclosed: bool
    source_reference: str


class OfficialPublicationDTO(BaseModel):
    """Official publication or decision statement."""
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    central_bank_id: str
    title: str
    publication_kind: PublicationKind
    published_at: datetime
    source_url: str
    media_type: str
    content_hash: str
    sanitized_excerpt: str
    source_revision: str


class OfficialSpeechDTO(BaseModel):
    """Policymaker speech and transcript record."""
    model_config = ConfigDict(from_attributes=True)

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


class OfficialForwardGuidanceDTO(BaseModel):
    """Official forward guidance statement excerpt."""
    model_config = ConfigDict(from_attributes=True)

    guidance_id: str
    central_bank_id: str
    source_document_id: str
    guidance_kind: ForwardGuidanceKind
    verbatim_excerpt: str
    explicit_conditions: str
    published_at: datetime
    status: str


class BalanceSheetItemDTO(BaseModel):
    """Single balance sheet position item."""
    model_config = ConfigDict(from_attributes=True)

    item_id: str
    name: str
    category: str
    account_side: str
    value_billions: float
    currency: str


class CentralBankBalanceSheetSummaryDTO(BaseModel):
    """Balance sheet assets, liabilities, and reserve positions."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    reference_date: str
    reporting_frequency: str
    currency: str
    total_assets_billions: float
    total_liabilities_billions: float
    securities_holdings_billions: float
    reserve_balances_billions: float
    items: List[BalanceSheetItemDTO]
    accounting_notes: str


class CentralBankPolicyProgramDTO(BaseModel):
    """Asset purchase or balance sheet reduction policy program."""
    model_config = ConfigDict(from_attributes=True)

    program_id: str
    central_bank_id: str
    name: str
    program_kind: PolicyProgramKind
    announced_date: str
    effective_start: str
    effective_end: Optional[str] = None
    authorized_envelope_billions: Optional[float] = None
    current_holdings_billions: Optional[float] = None
    status: str
    description: str


class PolicyTimelineEventDTO(BaseModel):
    """Historical timeline event."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    central_bank_id: str
    timestamp: datetime
    event_kind: str
    title: str
    summary: str
    instrument_code: Optional[str] = None
    rate_change_bps: Optional[float] = None
    document_id: Optional[str] = None


class CentralBankOverviewDTO(BaseModel):
    """Master central bank analytical research snapshot."""
    model_config = ConfigDict(from_attributes=True)

    institution: CentralBankInstitutionDTO
    framework: MonetaryPolicyFrameworkDTO
    instruments: List[PolicyInstrumentDTO]
    latest_decision: Optional[MonetaryPolicyDecisionDTO] = None
    latest_meeting: Optional[MonetaryPolicyMeetingDTO] = None
    latest_balance_sheet: Optional[CentralBankBalanceSheetSummaryDTO] = None
    active_programs_count: int
    active_forward_guidance: Optional[OfficialForwardGuidanceDTO] = None
    current_policy_cycle: PolicyCycleKind
    data_freshness_status: str


class CentralBankCoverageResponseDTO(BaseModel):
    """Central bank indicator and document coverage availability."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    institution: CentralBankInstitutionDTO
    has_policy_rate_series: bool
    has_target_range: bool
    has_decision_history: bool
    has_meeting_minutes: bool
    has_voting_records: bool
    has_official_statements: bool
    has_official_speeches: bool
    has_forward_guidance: bool
    has_balance_sheet: bool
    has_policy_programs: bool


class CommitteeMetadataDTO(BaseModel):
    """Monetary policy committee identity and structure."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    committee_name: str
    mandate: str
    total_members: int
    discloses_individual_votes: bool
    official_charter_url: str


class InflationTargetDTO(BaseModel):
    """Official inflation target parameters."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    inflation_target_metric: str
    inflation_target_pct: Optional[float] = None
    target_lower_bound_pct: Optional[float] = None
    target_upper_bound_pct: Optional[float] = None
    target_tolerance_band: Optional[str] = None
    target_horizon: str
    effective_since: str
    source_citation: str


class SourceProvenanceDTO(BaseModel):
    """Source authority and provenance verification metadata."""
    model_config = ConfigDict(from_attributes=True)

    central_bank_id: str
    official_institution_name: str
    official_website_url: str
    data_authority: str
    source_tier: str
    provenance_id: str
    reporting_currency: str
    is_point_in_time_verified: bool


class HistoricalRatePointDTO(BaseModel):
    """Historical official policy rate observation."""
    model_config = ConfigDict(from_attributes=True)

    observation_date: str
    instrument_code: str
    rate: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    effective_date: str
    source_decision_id: Optional[str] = None
