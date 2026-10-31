"""Typed Event Payloads for the Universal Event Model (Stage 135).

Defines strongly-typed discriminated payloads for earnings releases, economic releases,
central bank policy rate decisions, sanctions designations, corporate actions, regulatory
orders, geopolitical developments, and physical-world disasters.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EarningsEventPayload(BaseModel):
    """Structured payload for corporate earnings announcements and guidance."""
    issuer_reference: str
    fiscal_period: str
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    period_end: str
    release_datetime: Optional[datetime] = None
    reporting_currency: str = "USD"
    reported_metrics: Dict[str, float] = Field(default_factory=dict)
    consensus_metrics: Optional[Dict[str, float]] = None
    surprise_metrics: Optional[Dict[str, float]] = None
    audit_status: str = "UNAUDITED"
    conference_call_time: Optional[datetime] = None


class EconomicReleasePayload(BaseModel):
    """Structured payload for macroeconomic indicators and data releases."""
    indicator_id: str
    indicator_name: str
    country_region: str
    reporting_period: str
    reference_period: str
    release_time: datetime
    reported_value: float
    units: str
    seasonal_adjustment: str = "SA"
    revision_vintage: str = "INITIAL"
    previous_value: Optional[float] = None
    consensus_expectation: Optional[float] = None


class CentralBankEventPayload(BaseModel):
    """Structured payload for central bank monetary policy and interest rate decisions."""
    central_bank_reference: str
    jurisdiction: str
    policy_instrument: str
    decision_time: datetime
    effective_time: Optional[datetime] = None
    previous_rate: Optional[float] = None
    new_rate: Optional[float] = None
    change_bps: Optional[float] = None
    target_range_lower: Optional[float] = None
    target_range_upper: Optional[float] = None
    rate_unit: str = "PERCENT"
    statement_url: Optional[str] = None

    def compute_change_bps(self) -> Optional[float]:
        """Compute basis point change between new and previous rate."""
        if self.new_rate is not None and self.previous_rate is not None:
            self.change_bps = round((self.new_rate - self.previous_rate) * 100.0, 2)
            return self.change_bps
        return None


class SanctionsEventPayload(BaseModel):
    """Structured payload for official government and multilateral sanctions."""
    authority_id: str
    jurisdiction: str
    program_id: str
    official_action_id: str
    action_type: str  # DESIGNATION, AMENDMENT, DELISTING
    designated_subject_reference: str
    subject_kind: str  # INDIVIDUAL, ENTITY, VESSEL, AIRCRAFT
    publication_date: str
    effective_date: str
    legal_instrument_reference: Optional[str] = None
    list_version: Optional[str] = None


class RegulatoryEventPayload(BaseModel):
    """Structured payload for official regulatory rulemakings and enforcement actions."""
    agency: str
    jurisdiction: str
    action_type: str  # RULE_PROPOSAL, RULE_ADOPTION, ENFORCEMENT_ACTION, INVESTIGATION
    rule_or_matter_reference: str
    status: str
    summary: str
    effective_date: Optional[str] = None
    public_comment_deadline: Optional[str] = None


class CorporateActionEventPayload(BaseModel):
    """Structured payload for mergers, acquisitions, dividends, and corporate restructurings."""
    issuer_reference: str
    action_type: str  # MERGER_ANNOUNCED, MERGER_APPROVED, MERGER_COMPLETED, DIVIDEND, SPLIT
    target_reference: Optional[str] = None
    deal_value_currency: Optional[str] = None
    deal_value_amount: Optional[float] = None
    declaration_date: Optional[str] = None
    record_date: Optional[str] = None
    ex_date: Optional[str] = None
    payment_date: Optional[str] = None
    ratio: Optional[str] = None


class GeopoliticalEventPayload(BaseModel):
    """Structured payload for verified diplomatic, trade, and treaty actions."""
    actor_jurisdiction: str
    target_jurisdiction: Optional[str] = None
    event_type: str
    statement_speaker: Optional[str] = None
    claim_type: str = "OFFICIAL_STATEMENT"
    summary: str = ""
    treaty_or_accord_name: Optional[str] = None


class PhysicalDisasterEventPayload(BaseModel):
    """Structured payload for natural disasters and Stage 134 physical observations."""
    disaster_type: str  # EARTHQUAKE, WILDFIRE, SEVERE_WEATHER, FLOOD, VOLCANO
    magnitude_or_severity: str
    depth_km: Optional[float] = None
    frp_mw: Optional[float] = None
    source_event_id: str
    tsunami_flag: bool = False
    stage134_observation_id: Optional[str] = None
