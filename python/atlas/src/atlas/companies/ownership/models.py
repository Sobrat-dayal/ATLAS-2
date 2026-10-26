"""Domain models for Company Ownership Intelligence (Stage 85).

Defines internal dataclasses representing corporate shareholders, positions,
filing disclosures, historical snapshots, position changes, and shareholding patterns.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from .enums import (
    DisclosureType,
    HolderCategory,
    Jurisdiction,
    OwnershipForm,
    PositionChangeStatus,
    PositionType,
)


@dataclass
class OwnershipHolder:
    """Canonical shareholder or reporting person."""
    holder_entity_id: str
    name: str
    category: HolderCategory
    reporting_party: Optional[str] = None
    parent_manager_id: Optional[str] = None
    cik: Optional[str] = None
    lei: Optional[str] = None
    country: Optional[str] = None
    is_institution: bool = False
    is_insider: bool = False
    is_promoter: bool = False


@dataclass
class OwnershipPosition:
    """Disclosed security holding by a shareholder in an issuer."""
    position_id: str
    company_id: str
    security_id: str
    security_name: str
    share_class: str
    holder: OwnershipHolder
    shares_held: Decimal
    position_type: PositionType = PositionType.COMMON_SHARES
    ownership_form: OwnershipForm = OwnershipForm.DIRECT
    source_reported_percentage: Optional[Decimal] = None
    calculated_percentage: Optional[Decimal] = None
    voting_percentage: Optional[Decimal] = None
    reporting_date: str = ""
    filing_date: str = ""
    filing_delay_days: int = 0
    disclosure_type: DisclosureType = DisclosureType.FORM_13F
    jurisdiction: Jurisdiction = Jurisdiction.US_SEC
    source_document_id: Optional[str] = None
    is_amendment: bool = False
    notes: Optional[str] = None
    # 13D/13G beneficial voting & dispositive breakdowns
    sole_voting_power: Optional[Decimal] = None
    shared_voting_power: Optional[Decimal] = None
    sole_dispositive_power: Optional[Decimal] = None
    shared_dispositive_power: Optional[Decimal] = None
    # Form 3/4/5 Insider specific attributes
    insider_role: Optional[str] = None
    is_officer: bool = False
    is_director: bool = False
    is_ten_percent_owner: bool = False


@dataclass
class ShareholdingPatternCategory:
    """Taxonomic category breakdown (e.g. SEBI Indian shareholding pattern or aggregate institutional/public)."""
    category_name: str
    shares_held: Decimal
    percentage_of_total: Decimal
    pledged_shares: Optional[Decimal] = None
    pledged_percentage: Optional[Decimal] = None
    shareholder_count: Optional[int] = None


@dataclass
class OwnershipSnapshot:
    """Integrated point-in-time snapshot of company ownership as of a disclosure period."""
    snapshot_id: str
    company_id: str
    security_id: str
    reporting_period: str
    reporting_date: str
    filing_date: str
    shares_outstanding: Decimal
    positions: List[OwnershipPosition] = field(default_factory=list)
    patterns: List[ShareholdingPatternCategory] = field(default_factory=list)


@dataclass
class OwnershipChange:
    """Derived change in a holder's reported position between two comparable snapshot periods."""
    holder: OwnershipHolder
    security_id: str
    prior_shares: Decimal
    current_shares: Decimal
    shares_change: Decimal
    percentage_change: Optional[Decimal]
    prior_ownership_pct: Optional[Decimal]
    current_ownership_pct: Optional[Decimal]
    pp_change: Optional[Decimal]
    status: PositionChangeStatus
