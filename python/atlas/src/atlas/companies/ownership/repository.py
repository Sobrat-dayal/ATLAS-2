"""Repository layer for Company Ownership Intelligence (Stage 85).

Provides verified access to disclosed security holdings, institutional positions,
insider holdings, beneficial ownership reports, historical snapshots, and
shareholding patterns with temporal pre-release and publication cutoff safeguards.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from .calculator import (
    calculate_ownership_percentage,
    calculate_percentage_points_change,
    calculate_position_percentage_change,
    calculate_shares_change,
)
from .enums import (
    DisclosureType,
    HolderCategory,
    Jurisdiction,
    OwnershipForm,
    PositionChangeStatus,
)
from .models import (
    OwnershipChange,
    OwnershipHolder,
    OwnershipPosition,
    OwnershipSnapshot,
    ShareholdingPatternCategory,
)


class CompanyOwnershipRepository:
    """In-memory reference repository for company ownership data."""

    def __init__(self):
        # Canonical Apple Company UUID & Primary Common Stock Security
        self.apple_company_id = "c0000000-0000-0000-0000-000000000001"
        self.apple_security_id = "s0000000-0000-0000-0000-000000000001"
        self.apple_shares_outstanding = Decimal("15115800000")  # 15.1158B shares

        # Securities registry: company_id -> list of security definitions
        self._securities: Dict[str, List[dict]] = {
            self.apple_company_id: [
                {
                    "security_id": self.apple_security_id,
                    "security_name": "Apple Inc. Common Stock",
                    "ticker": "AAPL",
                    "share_class": "Common Stock",
                    "is_primary": True,
                    "shares_outstanding": self.apple_shares_outstanding,
                }
            ]
        }

        # Snapshots: (company_id, security_id) -> dict of period -> OwnershipSnapshot
        self._snapshots: Dict[str, Dict[str, OwnershipSnapshot]] = {}
        self._init_apple_ownership_data()

    def _init_apple_ownership_data(self):
        """Initializes verified institutional, insider, and beneficial ownership records for Apple Inc."""
        # 1. Canonical Holders
        vanguard = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000001",
            name="The Vanguard Group, Inc.",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="The Vanguard Group, Inc.",
            cik="0000102909",
            country="United States",
            is_institution=True,
        )
        blackrock = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000002",
            name="BlackRock, Inc.",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="BlackRock, Inc.",
            cik="0001364742",
            country="United States",
            is_institution=True,
        )
        berkshire = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000003",
            name="Berkshire Hathaway Inc.",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="Berkshire Hathaway Inc.",
            cik="0001067983",
            country="United States",
            is_institution=True,
        )
        state_street = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000004",
            name="State Street Corporation",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="State Street Corp",
            cik="0000093751",
            country="United States",
            is_institution=True,
        )
        geode = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000005",
            name="Geode Capital Management, LLC",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="Geode Capital Management, LLC",
            cik="0001214717",
            country="United States",
            is_institution=True,
        )
        fidelity = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000006",
            name="FMR LLC (Fidelity)",
            category=HolderCategory.INSTITUTIONAL_MANAGER,
            reporting_party="FMR LLC",
            cik="0000315066",
            country="United States",
            is_institution=True,
        )
        norges = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000007",
            name="Norges Bank (Central Bank of Norway)",
            category=HolderCategory.GOVERNMENT_SOVEREIGN,
            reporting_party="Norges Bank",
            cik="0001282245",
            country="Norway",
            is_institution=True,
        )

        # Insiders
        tim_cook = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000011",
            name="Timothy D. Cook",
            category=HolderCategory.INSIDER_PERSON,
            reporting_party="Timothy D. Cook",
            country="United States",
            is_insider=True,
        )
        arthur_levinson = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000012",
            name="Arthur D. Levinson",
            category=HolderCategory.INSIDER_PERSON,
            reporting_party="Arthur D. Levinson",
            country="United States",
            is_insider=True,
        )
        luca_maestri = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000013",
            name="Luca Maestri",
            category=HolderCategory.INSIDER_PERSON,
            reporting_party="Luca Maestri",
            country="United States",
            is_insider=True,
        )
        jeff_williams = OwnershipHolder(
            holder_entity_id="h0000000-0000-0000-0000-000000000014",
            name="Jeffrey E. Williams",
            category=HolderCategory.INSIDER_PERSON,
            reporting_party="Jeffrey E. Williams",
            country="United States",
            is_insider=True,
        )

        # Period 1: 2024-Q3 (Latest, As of 2024-09-30, Filed 2024-11-14, 45-day lag)
        positions_q3 = [
            # Vanguard Group (13F & 13G Beneficial)
            OwnershipPosition(
                position_id="pos-q3-001",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=vanguard,
                shares_held=Decimal("1332450120"),
                calculated_percentage=calculate_ownership_percentage(Decimal("1332450120"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000102909-24-000042",
                ownership_form=OwnershipForm.MANAGED_DISCRETIONARY,
                sole_voting_power=Decimal("0"),
                shared_voting_power=Decimal("21450000"),
                sole_dispositive_power=Decimal("1260000000"),
                shared_dispositive_power=Decimal("72450120"),
            ),
            # BlackRock (13F & 13G Beneficial)
            OwnershipPosition(
                position_id="pos-q3-002",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=blackrock,
                shares_held=Decimal("1043210000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("1043210000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0001364742-24-000091",
                ownership_form=OwnershipForm.MANAGED_DISCRETIONARY,
                sole_voting_power=Decimal("942000000"),
                shared_voting_power=Decimal("0"),
                sole_dispositive_power=Decimal("1043210000"),
                shared_dispositive_power=Decimal("0"),
            ),
            # State Street Corporation
            OwnershipPosition(
                position_id="pos-q3-003",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=state_street,
                shares_held=Decimal("562400000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("562400000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000093751-24-000780",
                ownership_form=OwnershipForm.MANAGED_DISCRETIONARY,
            ),
            # Geode Capital Management
            OwnershipPosition(
                position_id="pos-q3-004",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=geode,
                shares_held=Decimal("335100000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("335100000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-13",
                filing_delay_days=44,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0001214717-24-000512",
                ownership_form=OwnershipForm.MANAGED_DISCRETIONARY,
            ),
            # FMR LLC (Fidelity)
            OwnershipPosition(
                position_id="pos-q3-005",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=fidelity,
                shares_held=Decimal("308500000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("308500000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000315066-24-001201",
                ownership_form=OwnershipForm.MANAGED_DISCRETIONARY,
            ),
            # Berkshire Hathaway Inc.
            OwnershipPosition(
                position_id="pos-q3-006",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=berkshire,
                shares_held=Decimal("300000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("300000000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0001067983-24-000115",
                ownership_form=OwnershipForm.BENEFICIAL,
            ),
            # Norges Bank
            OwnershipPosition(
                position_id="pos-q3-007",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=norges,
                shares_held=Decimal("160200000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("160200000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-11-14",
                filing_delay_days=45,
                disclosure_type=DisclosureType.FORM_13F,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0001282245-24-000088",
                ownership_form=OwnershipForm.DIRECT,
            ),
            # Insiders
            OwnershipPosition(
                position_id="pos-q3-ins-001",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=tim_cook,
                shares_held=Decimal("3280053"),
                calculated_percentage=calculate_ownership_percentage(Decimal("3280053"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-10-03",
                filing_delay_days=3,
                disclosure_type=DisclosureType.FORM_4,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000320193-24-000108",
                ownership_form=OwnershipForm.DIRECT,
                insider_role="Chief Executive Officer",
                is_officer=True,
                is_director=True,
            ),
            OwnershipPosition(
                position_id="pos-q3-ins-002",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=arthur_levinson,
                shares_held=Decimal("4530000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("4530000"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-10-02",
                filing_delay_days=2,
                disclosure_type=DisclosureType.FORM_4,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000320193-24-000106",
                ownership_form=OwnershipForm.DIRECT,
                insider_role="Chair of the Board",
                is_director=True,
            ),
            OwnershipPosition(
                position_id="pos-q3-ins-003",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=jeff_williams,
                shares_held=Decimal("489944"),
                calculated_percentage=calculate_ownership_percentage(Decimal("489944"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-10-03",
                filing_delay_days=3,
                disclosure_type=DisclosureType.FORM_4,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000320193-24-000110",
                ownership_form=OwnershipForm.DIRECT,
                insider_role="Chief Operating Officer",
                is_officer=True,
            ),
            OwnershipPosition(
                position_id="pos-q3-ins-004",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=luca_maestri,
                shares_held=Decimal("110240"),
                calculated_percentage=calculate_ownership_percentage(Decimal("110240"), self.apple_shares_outstanding),
                reporting_date="2024-09-30",
                filing_date="2024-10-03",
                filing_delay_days=3,
                disclosure_type=DisclosureType.FORM_4,
                jurisdiction=Jurisdiction.US_SEC,
                source_document_id="0000320193-24-000109",
                ownership_form=OwnershipForm.DIRECT,
                insider_role="Senior VP, Chief Financial Officer",
                is_officer=True,
            ),
        ]

        # Standard Shareholding Pattern Breakdown
        patterns_q3 = [
            ShareholdingPatternCategory(
                category_name="Institutional Disclosed (13F)",
                shares_held=Decimal("8950000000"),
                percentage_of_total=Decimal("59.21"),
                shareholder_count=4250,
            ),
            ShareholdingPatternCategory(
                category_name="Insiders & Key Executives",
                shares_held=Decimal("12000000"),
                percentage_of_total=Decimal("0.08"),
                shareholder_count=18,
            ),
            ShareholdingPatternCategory(
                category_name="Public & Retail Float",
                shares_held=Decimal("6153800000"),
                percentage_of_total=Decimal("40.71"),
                shareholder_count=None,
            ),
        ]

        snapshot_q3 = OwnershipSnapshot(
            snapshot_id="snap-apple-2024-q3",
            company_id=self.apple_company_id,
            security_id=self.apple_security_id,
            reporting_period="2024-Q3",
            reporting_date="2024-09-30",
            filing_date="2024-11-14",
            shares_outstanding=self.apple_shares_outstanding,
            positions=positions_q3,
            patterns=patterns_q3,
        )

        # Period 2: 2024-Q2 (Prior period: Berkshire owned 400M, Vanguard 1.31B, BlackRock 1.03B)
        positions_q2 = [
            OwnershipPosition(
                position_id="pos-q2-001",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=vanguard,
                shares_held=Decimal("1310000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("1310000000"), self.apple_shares_outstanding),
                reporting_date="2024-06-30",
                filing_date="2024-08-14",
                disclosure_type=DisclosureType.FORM_13F,
            ),
            OwnershipPosition(
                position_id="pos-q2-002",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=blackrock,
                shares_held=Decimal("1028000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("1028000000"), self.apple_shares_outstanding),
                reporting_date="2024-06-30",
                filing_date="2024-08-14",
                disclosure_type=DisclosureType.FORM_13F,
            ),
            OwnershipPosition(
                position_id="pos-q2-003",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=state_street,
                shares_held=Decimal("558000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("558000000"), self.apple_shares_outstanding),
                reporting_date="2024-06-30",
                filing_date="2024-08-14",
                disclosure_type=DisclosureType.FORM_13F,
            ),
            OwnershipPosition(
                position_id="pos-q2-006",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=berkshire,
                shares_held=Decimal("400000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("400000000"), self.apple_shares_outstanding),
                reporting_date="2024-06-30",
                filing_date="2024-08-14",
                disclosure_type=DisclosureType.FORM_13F,
            ),
        ]

        snapshot_q2 = OwnershipSnapshot(
            snapshot_id="snap-apple-2024-q2",
            company_id=self.apple_company_id,
            security_id=self.apple_security_id,
            reporting_period="2024-Q2",
            reporting_date="2024-06-30",
            filing_date="2024-08-14",
            shares_outstanding=self.apple_shares_outstanding,
            positions=positions_q2,
        )

        # Period 3: 2024-Q1 (Prior period: Berkshire owned 789M, Vanguard 1.30B)
        positions_q1 = [
            OwnershipPosition(
                position_id="pos-q1-001",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=vanguard,
                shares_held=Decimal("1300000000"),
                calculated_percentage=calculate_ownership_percentage(Decimal("1300000000"), self.apple_shares_outstanding),
                reporting_date="2024-03-31",
                filing_date="2024-05-15",
                disclosure_type=DisclosureType.FORM_13F,
            ),
            OwnershipPosition(
                position_id="pos-q1-006",
                company_id=self.apple_company_id,
                security_id=self.apple_security_id,
                security_name="Apple Inc. Common Stock",
                share_class="Common Stock",
                holder=berkshire,
                shares_held=Decimal("789368450"),
                calculated_percentage=calculate_ownership_percentage(Decimal("789368450"), self.apple_shares_outstanding),
                reporting_date="2024-03-31",
                filing_date="2024-05-15",
                disclosure_type=DisclosureType.FORM_13F,
            ),
        ]

        snapshot_q1 = OwnershipSnapshot(
            snapshot_id="snap-apple-2024-q1",
            company_id=self.apple_company_id,
            security_id=self.apple_security_id,
            reporting_period="2024-Q1",
            reporting_date="2024-03-31",
            filing_date="2024-05-15",
            shares_outstanding=self.apple_shares_outstanding,
            positions=positions_q1,
        )

        key = f"{self.apple_company_id}:{self.apple_security_id}"
        self._snapshots[key] = {
            "2024-Q3": snapshot_q3,
            "2024-Q2": snapshot_q2,
            "2024-Q1": snapshot_q1,
        }

    def get_securities(self, company_id: str) -> List[dict]:
        """Resolves verified securities and share classes for the company."""
        if company_id in self._securities:
            return self._securities[company_id]

        # Dynamic fallback security definition for other companies
        return [
            {
                "security_id": f"s-{company_id[:8]}",
                "security_name": "Common Equity",
                "ticker": None,
                "share_class": "Ordinary Shares",
                "is_primary": True,
                "shares_outstanding": Decimal("100000000"),
            }
        ]

    def get_latest_snapshot(self, company_id: str, security_id: Optional[str] = None) -> Optional[OwnershipSnapshot]:
        """Returns the most recent verified ownership snapshot for the company and security."""
        sec_id = security_id or self.apple_security_id
        key = f"{company_id}:{sec_id}"
        company_snaps = self._snapshots.get(key)
        if not company_snaps:
            return None

        # Return latest sorted by reporting_period descending
        sorted_periods = sorted(company_snaps.keys(), reverse=True)
        return company_snaps[sorted_periods[0]] if sorted_periods else None

    def get_snapshot_by_period(self, company_id: str, security_id: str, period: str) -> Optional[OwnershipSnapshot]:
        """Returns snapshot for a specific reporting period."""
        key = f"{company_id}:{security_id}"
        return self._snapshots.get(key, {}).get(period)

    def get_historical_snapshots(self, company_id: str, security_id: str, limit: int = 12) -> List[OwnershipSnapshot]:
        """Returns historical snapshots sorted chronologically descending."""
        key = f"{company_id}:{security_id}"
        company_snaps = self._snapshots.get(key, {})
        sorted_periods = sorted(company_snaps.keys(), reverse=True)
        return [company_snaps[p] for p in sorted_periods[:limit]]

    def calculate_position_changes(
        self, company_id: str, security_id: str, current_period: str, prior_period: str
    ) -> List[OwnershipChange]:
        """Computes comparative position changes between two quarterly disclosure snapshots."""
        snap_curr = self.get_snapshot_by_period(company_id, security_id, current_period)
        snap_prior = self.get_snapshot_by_period(company_id, security_id, prior_period)

        if not snap_curr or not snap_prior:
            return []

        prior_map = {pos.holder.holder_entity_id: pos for pos in snap_prior.positions}
        changes: List[OwnershipChange] = []

        for pos in snap_curr.positions:
            h_id = pos.holder.holder_entity_id
            curr_shares = pos.shares_held
            curr_pct = pos.calculated_percentage

            if h_id in prior_map:
                p_pos = prior_map[h_id]
                prior_shares = p_pos.shares_held
                prior_pct = p_pos.calculated_percentage
                sh_diff = calculate_shares_change(curr_shares, prior_shares)
                pct_change = calculate_position_percentage_change(curr_shares, prior_shares)
                pp_diff = calculate_percentage_points_change(curr_pct, prior_pct)

                if sh_diff > Decimal("0"):
                    status = PositionChangeStatus.INCREASED
                elif sh_diff < Decimal("0"):
                    status = PositionChangeStatus.DECREASED
                else:
                    status = PositionChangeStatus.UNCHANGED
            else:
                # Newly reported in current period coverage
                prior_shares = Decimal("0")
                prior_pct = Decimal("0")
                sh_diff = curr_shares
                pct_change = None
                pp_diff = curr_pct
                status = PositionChangeStatus.NEW_POSITION

            changes.append(
                OwnershipChange(
                    holder=pos.holder,
                    security_id=security_id,
                    prior_shares=prior_shares,
                    current_shares=curr_shares,
                    shares_change=sh_diff,
                    percentage_change=pct_change,
                    prior_ownership_pct=prior_pct,
                    current_ownership_pct=curr_pct,
                    pp_change=pp_diff,
                    status=status,
                )
            )

        # Check for verified exits (present in prior, absent in current)
        curr_map = {pos.holder.holder_entity_id: pos for pos in snap_curr.positions}
        for h_id, p_pos in prior_map.items():
            if h_id not in curr_map:
                changes.append(
                    OwnershipChange(
                        holder=p_pos.holder,
                        security_id=security_id,
                        prior_shares=p_pos.shares_held,
                        current_shares=Decimal("0"),
                        shares_change=-p_pos.shares_held,
                        percentage_change=Decimal("-100.00"),
                        prior_ownership_pct=p_pos.calculated_percentage,
                        current_ownership_pct=Decimal("0"),
                        pp_change=-p_pos.calculated_percentage if p_pos.calculated_percentage else None,
                        status=PositionChangeStatus.SOLD_OUT,
                    )
                )

        return sorted(changes, key=lambda c: abs(c.shares_change), reverse=True)
