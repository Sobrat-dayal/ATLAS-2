"""Service orchestration layer for Company Ownership Intelligence (Stage 85).

Implements institutional ownership queries, shareholding pattern categorization,
concentration analytics, comparative position change calculations, and
point-in-time snapshot integrity.
"""

from decimal import Decimal
from typing import List, Optional

from .calculator import (
    calculate_concentration_metrics,
    format_indicative_value,
    format_percentage,
    format_shares_count,
)
from .enums import DisclosureType, HolderCategory, PositionChangeStatus
from .models import OwnershipPosition
from .repository import CompanyOwnershipRepository
from .schemas import (
    BeneficialOwnerDTO,
    BeneficialOwnersResponseDTO,
    CompanyOwnershipOverviewDTO,
    HistoricalOwnershipSnapshotDTO,
    HolderSummaryDTO,
    InsiderHoldingDTO,
    InsiderHoldingsResponseDTO,
    InstitutionalHoldingDTO,
    InstitutionalHoldingsResponseDTO,
    OwnershipChangeDTO,
    OwnershipChangesResponseDTO,
    OwnershipConcentrationDTO,
    OwnershipHistoryResponseDTO,
    OwnershipHoldersResponseDTO,
    OwnershipPositionDTO,
    OwnershipSecuritiesResponseDTO,
    PatternCategoryDTO,
    SecuritySummaryDTO,
    ShareholdingPatternDTO,
)


class CompanyOwnershipService:
    """Service providing institutional-grade company ownership intelligence."""

    def __init__(self, repository: Optional[CompanyOwnershipRepository] = None):
        self.repository = repository or CompanyOwnershipRepository()

    def get_securities(self, company_id: str) -> OwnershipSecuritiesResponseDTO:
        """Returns verified securities and share classes for an issuer."""
        sec_dicts = self.repository.get_securities(company_id)
        summaries = [
            SecuritySummaryDTO(
                security_id=s["security_id"],
                security_name=s["security_name"],
                ticker=s.get("ticker"),
                share_class=s.get("share_class", "Common Stock"),
                is_primary=s.get("is_primary", True),
                shares_outstanding=float(s["shares_outstanding"]),
                formatted_shares_outstanding=format_shares_count(s["shares_outstanding"]),
            )
            for s in sec_dicts
        ]
        return OwnershipSecuritiesResponseDTO(
            company_id=company_id,
            securities=summaries,
        )

    def get_ownership_overview(
        self, company_id: str, security_id: Optional[str] = None
    ) -> CompanyOwnershipOverviewDTO:
        """Builds executive ownership intelligence overview."""
        securities_resp = self.get_securities(company_id)
        selected_sec = (
            next((s for s in securities_resp.securities if s.security_id == security_id), None)
            if security_id
            else securities_resp.securities[0]
        )
        sec_id = selected_sec.security_id if selected_sec else "sec-default"

        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)

        if not snapshot:
            # Clean transparent empty response when company has no filed ownership records
            return CompanyOwnershipOverviewDTO(
                company_id=company_id,
                company_name="Company",
                selected_security=selected_sec,
                available_securities=securities_resp.securities,
                reporting_period="—",
                reporting_date="—",
                filing_date="—",
                source_coverage="No public ownership disclosures registered.",
                concentration=OwnershipConcentrationDTO(),
                top_holders=[],
            )

        # Concentration metrics
        shares_list = [p.shares_held for p in snapshot.positions]
        conc_dict = calculate_concentration_metrics(shares_list, snapshot.shares_outstanding)

        concentration_dto = OwnershipConcentrationDTO(
            top_1_shares=float(conc_dict["top_1_shares"]),
            top_1_formatted=format_shares_count(conc_dict["top_1_shares"]),
            top_1_pct=float(conc_dict["top_1_pct"]) if conc_dict["top_1_pct"] is not None else None,
            top_5_shares=float(conc_dict["top_5_shares"]),
            top_5_formatted=format_shares_count(conc_dict["top_5_shares"]),
            top_5_pct=float(conc_dict["top_5_pct"]) if conc_dict["top_5_pct"] is not None else None,
            top_10_shares=float(conc_dict["top_10_shares"]),
            top_10_formatted=format_shares_count(conc_dict["top_10_shares"]),
            top_10_pct=float(conc_dict["top_10_pct"]) if conc_dict["top_10_pct"] is not None else None,
            total_disclosed_shares=float(conc_dict["total_disclosed_shares"]),
            total_disclosed_formatted=format_shares_count(conc_dict["total_disclosed_shares"]),
            total_disclosed_pct=float(conc_dict["total_disclosed_pct"]) if conc_dict["total_disclosed_pct"] is not None else None,
            shares_outstanding=float(snapshot.shares_outstanding),
            shares_outstanding_formatted=format_shares_count(snapshot.shares_outstanding),
        )

        # Map top holders
        sorted_positions = sorted(snapshot.positions, key=lambda p: p.shares_held, reverse=True)
        top_holders_dto = [self._map_position_dto(p) for p in sorted_positions[:10]]

        # Category sums
        inst_shares = sum(
            (p.shares_held for p in snapshot.positions if p.holder.is_institution), Decimal("0")
        )
        insider_shares = sum(
            (p.shares_held for p in snapshot.positions if p.holder.is_insider), Decimal("0")
        )

        institutional_summary = {
            "total_shares": float(inst_shares),
            "formatted_shares": format_shares_count(inst_shares),
            "percentage": float((inst_shares / snapshot.shares_outstanding * Decimal("100")).quantize(Decimal("0.01"))),
            "holder_count": len([p for p in snapshot.positions if p.holder.is_institution]),
        }

        insider_summary = {
            "total_shares": float(insider_shares),
            "formatted_shares": format_shares_count(insider_shares),
            "percentage": float((insider_shares / snapshot.shares_outstanding * Decimal("100")).quantize(Decimal("0.01"))),
            "holder_count": len([p for p in snapshot.positions if p.holder.is_insider]),
        }

        # Patterns
        patterns_dto = None
        if snapshot.patterns:
            patterns_dto = ShareholdingPatternDTO(
                company_id=company_id,
                reporting_period=snapshot.reporting_period,
                reporting_date=snapshot.reporting_date,
                categories=[
                    PatternCategoryDTO(
                        category_name=cat.category_name,
                        shares_held=float(cat.shares_held),
                        formatted_shares=format_shares_count(cat.shares_held),
                        percentage_of_total=float(cat.percentage_of_total),
                        formatted_percentage=format_percentage(cat.percentage_of_total),
                        pledged_percentage=float(cat.pledged_percentage) if cat.pledged_percentage is not None else None,
                        shareholder_count=cat.shareholder_count,
                    )
                    for cat in snapshot.patterns
                ],
            )

        return CompanyOwnershipOverviewDTO(
            company_id=company_id,
            company_name="Apple Inc." if company_id == self.repository.apple_company_id else "Company",
            selected_security=selected_sec,
            available_securities=securities_resp.securities,
            reporting_period=snapshot.reporting_period,
            reporting_date=snapshot.reporting_date,
            filing_date=snapshot.filing_date,
            source_coverage="US SEC Form 13F Institutional & Form 4 Insider Disclosures",
            concentration=concentration_dto,
            top_holders=top_holders_dto,
            institutional_summary=institutional_summary,
            insider_summary=insider_summary,
            beneficial_summary={},
            patterns=patterns_dto,
        )

    def get_all_holders(
        self,
        company_id: str,
        security_id: Optional[str] = None,
        category: Optional[HolderCategory] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> OwnershipHoldersResponseDTO:
        """Returns paginated collection of all disclosed holders."""
        sec_id = security_id or self.repository.apple_security_id
        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)
        if not snapshot:
            return OwnershipHoldersResponseDTO(company_id=company_id, total_count=0, items=[])

        filtered = snapshot.positions
        if category:
            filtered = [p for p in filtered if p.holder.category == category]

        sorted_positions = sorted(filtered, key=lambda p: p.shares_held, reverse=True)
        paginated = sorted_positions[offset : offset + limit]

        return OwnershipHoldersResponseDTO(
            company_id=company_id,
            total_count=len(filtered),
            items=[self._map_position_dto(p) for p in paginated],
        )

    def get_institutional_holdings(
        self,
        company_id: str,
        security_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> InstitutionalHoldingsResponseDTO:
        """Returns institutional holdings with comparative changes vs prior quarter."""
        sec_id = security_id or self.repository.apple_security_id
        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)
        if not snapshot:
            return InstitutionalHoldingsResponseDTO(
                company_id=company_id, total_count=0, reporting_period="", reporting_date="", items=[]
            )

        # Institutional filter
        inst_positions = [
            p for p in snapshot.positions
            if p.holder.is_institution or p.holder.category in (
                HolderCategory.INSTITUTIONAL_MANAGER,
                HolderCategory.INVESTMENT_FUND,
                HolderCategory.GOVERNMENT_SOVEREIGN,
            )
        ]
        sorted_inst = sorted(inst_positions, key=lambda p: p.shares_held, reverse=True)

        # Compute changes vs prior period (e.g. 2024-Q2)
        prior_changes = {
            c.holder.holder_entity_id: c
            for c in self.repository.calculate_position_changes(company_id, sec_id, snapshot.reporting_period, "2024-Q2")
        }

        # Reference price for indicative market value calculation (~$225.00/share)
        ref_price = Decimal("225.00")

        items: List[InstitutionalHoldingDTO] = []
        for p in sorted_inst[offset : offset + limit]:
            h_id = p.holder.holder_entity_id
            change = prior_changes.get(h_id)
            sh_diff = change.shares_change if change else Decimal("0")
            status = change.status if change else PositionChangeStatus.UNCHANGED

            items.append(
                InstitutionalHoldingDTO(
                    position_id=p.position_id,
                    holder=self._map_holder_summary(p.holder),
                    shares_held=float(p.shares_held),
                    formatted_shares=format_shares_count(p.shares_held),
                    calculated_percentage=float(p.calculated_percentage) if p.calculated_percentage is not None else None,
                    formatted_percentage=format_percentage(p.calculated_percentage),
                    shares_change=float(sh_diff),
                    formatted_shares_change=format_shares_count(sh_diff, compact=True),
                    change_status=status,
                    indicative_value_formatted=format_indicative_value(p.shares_held, ref_price),
                    reporting_date=p.reporting_date,
                    filing_date=p.filing_date,
                    source_document_id=p.source_document_id,
                )
            )

        return InstitutionalHoldingsResponseDTO(
            company_id=company_id,
            total_count=len(inst_positions),
            reporting_period=snapshot.reporting_period,
            reporting_date=snapshot.reporting_date,
            items=items,
        )

    def get_insider_holdings(
        self, company_id: str, security_id: Optional[str] = None
    ) -> InsiderHoldingsResponseDTO:
        """Returns executive and director insider holdings."""
        sec_id = security_id or self.repository.apple_security_id
        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)
        if not snapshot:
            return InsiderHoldingsResponseDTO(company_id=company_id, total_count=0, reporting_date="", items=[])

        insiders = [p for p in snapshot.positions if p.holder.is_insider or p.holder.category == HolderCategory.INSIDER_PERSON]
        sorted_insiders = sorted(insiders, key=lambda p: p.shares_held, reverse=True)

        items = [
            InsiderHoldingDTO(
                position_id=p.position_id,
                holder=self._map_holder_summary(p.holder),
                insider_role=p.insider_role or "Corporate Insider",
                is_officer=p.is_officer,
                is_director=p.is_director,
                is_ten_percent_owner=p.is_ten_percent_owner,
                ownership_form=p.ownership_form,
                shares_held=float(p.shares_held),
                formatted_shares=format_shares_count(p.shares_held),
                calculated_percentage=float(p.calculated_percentage) if p.calculated_percentage is not None else None,
                formatted_percentage=format_percentage(p.calculated_percentage),
                reporting_date=p.reporting_date,
                filing_date=p.filing_date,
                source_document_id=p.source_document_id,
                notes=p.notes,
            )
            for p in sorted_insiders
        ]

        return InsiderHoldingsResponseDTO(
            company_id=company_id,
            total_count=len(items),
            reporting_date=snapshot.reporting_date,
            items=items,
        )

    def get_beneficial_ownership(
        self, company_id: str, security_id: Optional[str] = None
    ) -> BeneficialOwnersResponseDTO:
        """Returns Schedule 13D/13G beneficial owners with voting & dispositive breakdowns."""
        sec_id = security_id or self.repository.apple_security_id
        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)
        if not snapshot:
            return BeneficialOwnersResponseDTO(company_id=company_id, total_count=0, reporting_date="", items=[])

        # Beneficial owners are >=5% holders or those with explicit voting/dispositive powers
        beneficial_positions = [
            p for p in snapshot.positions
            if (p.calculated_percentage and p.calculated_percentage >= Decimal("5.0"))
            or p.sole_voting_power is not None
            or p.disclosure_type in (DisclosureType.SCHEDULE_13D, DisclosureType.SCHEDULE_13G)
        ]
        sorted_beneficial = sorted(beneficial_positions, key=lambda p: p.shares_held, reverse=True)

        items = [
            BeneficialOwnerDTO(
                position_id=p.position_id,
                holder=self._map_holder_summary(p.holder),
                shares_held=float(p.shares_held),
                formatted_shares=format_shares_count(p.shares_held),
                calculated_percentage=float(p.calculated_percentage) if p.calculated_percentage is not None else None,
                formatted_percentage=format_percentage(p.calculated_percentage),
                sole_voting_power=float(p.sole_voting_power) if p.sole_voting_power is not None else None,
                shared_voting_power=float(p.shared_voting_power) if p.shared_voting_power is not None else None,
                sole_dispositive_power=float(p.sole_dispositive_power) if p.sole_dispositive_power is not None else None,
                shared_dispositive_power=float(p.shared_dispositive_power) if p.shared_dispositive_power is not None else None,
                reporting_date=p.reporting_date,
                filing_date=p.filing_date,
                disclosure_type=p.disclosure_type,
                source_document_id=p.source_document_id,
            )
            for p in sorted_beneficial
        ]

        return BeneficialOwnersResponseDTO(
            company_id=company_id,
            total_count=len(items),
            reporting_date=snapshot.reporting_date,
            items=items,
        )

    def get_shareholding_patterns(
        self, company_id: str, security_id: Optional[str] = None
    ) -> ShareholdingPatternDTO:
        """Returns taxonomic category breakdown of shareholding patterns."""
        sec_id = security_id or self.repository.apple_security_id
        snapshot = self.repository.get_latest_snapshot(company_id, sec_id)
        if not snapshot or not snapshot.patterns:
            return ShareholdingPatternDTO(
                company_id=company_id,
                reporting_period="",
                reporting_date="",
                categories=[],
            )

        return ShareholdingPatternDTO(
            company_id=company_id,
            reporting_period=snapshot.reporting_period,
            reporting_date=snapshot.reporting_date,
            categories=[
                PatternCategoryDTO(
                    category_name=cat.category_name,
                    shares_held=float(cat.shares_held),
                    formatted_shares=format_shares_count(cat.shares_held),
                    percentage_of_total=float(cat.percentage_of_total),
                    formatted_percentage=format_percentage(cat.percentage_of_total),
                    pledged_percentage=float(cat.pledged_percentage) if cat.pledged_percentage is not None else None,
                    shareholder_count=cat.shareholder_count,
                )
                for cat in snapshot.patterns
            ],
        )

    def get_ownership_history(
        self, company_id: str, security_id: Optional[str] = None, limit: int = 12
    ) -> OwnershipHistoryResponseDTO:
        """Returns historical quarterly ownership snapshots."""
        sec_id = security_id or self.repository.apple_security_id
        snapshots = self.repository.get_historical_snapshots(company_id, sec_id, limit=limit)

        items: List[HistoricalOwnershipSnapshotDTO] = []
        for s in snapshots:
            inst_shares = sum(
                (p.shares_held for p in s.positions if p.holder.is_institution), Decimal("0")
            )
            insider_shares = sum(
                (p.shares_held for p in s.positions if p.holder.is_insider), Decimal("0")
            )
            inst_pct = (inst_shares / s.shares_outstanding * Decimal("100")).quantize(Decimal("0.01")) if s.shares_outstanding else None
            insider_pct = (insider_shares / s.shares_outstanding * Decimal("100")).quantize(Decimal("0.01")) if s.shares_outstanding else None

            items.append(
                HistoricalOwnershipSnapshotDTO(
                    snapshot_id=s.snapshot_id,
                    reporting_period=s.reporting_period,
                    reporting_date=s.reporting_date,
                    filing_date=s.filing_date,
                    shares_outstanding=float(s.shares_outstanding),
                    formatted_shares_outstanding=format_shares_count(s.shares_outstanding),
                    institutional_shares=float(inst_shares),
                    institutional_pct=float(inst_pct) if inst_pct is not None else None,
                    insider_shares=float(insider_shares),
                    insider_pct=float(insider_pct) if insider_pct is not None else None,
                    holder_count=len(s.positions),
                )
            )

        return OwnershipHistoryResponseDTO(
            company_id=company_id,
            total_count=len(items),
            snapshots=items,
        )

    def get_position_changes(
        self,
        company_id: str,
        security_id: Optional[str] = None,
        current_period: Optional[str] = None,
        prior_period: Optional[str] = None,
    ) -> OwnershipChangesResponseDTO:
        """Calculates comparative position changes between two quarters."""
        sec_id = security_id or self.repository.apple_security_id
        curr_p = current_period or "2024-Q3"
        prior_p = prior_period or "2024-Q2"

        raw_changes = self.repository.calculate_position_changes(company_id, sec_id, curr_p, prior_p)

        items = [
            OwnershipChangeDTO(
                holder=self._map_holder_summary(c.holder),
                prior_shares=float(c.prior_shares),
                current_shares=float(c.current_shares),
                shares_change=float(c.shares_change),
                formatted_shares_change=format_shares_count(c.shares_change, compact=True),
                percentage_change=float(c.percentage_change) if c.percentage_change is not None else None,
                formatted_percentage_change=format_percentage(c.percentage_change, include_sign=True),
                prior_ownership_pct=float(c.prior_ownership_pct) if c.prior_ownership_pct is not None else None,
                current_ownership_pct=float(c.current_ownership_pct) if c.current_ownership_pct is not None else None,
                pp_change=float(c.pp_change) if c.pp_change is not None else None,
                status=c.status,
            )
            for c in raw_changes
        ]

        return OwnershipChangesResponseDTO(
            company_id=company_id,
            prior_period=prior_p,
            current_period=curr_p,
            total_count=len(items),
            changes=items,
        )

    def _map_holder_summary(self, holder) -> HolderSummaryDTO:
        """Helper to map domain OwnershipHolder to HolderSummaryDTO."""
        return HolderSummaryDTO(
            holder_entity_id=holder.holder_entity_id,
            name=holder.name,
            category=holder.category,
            reporting_party=holder.reporting_party,
            country=holder.country,
            is_institution=holder.is_institution,
            is_insider=holder.is_insider,
            is_promoter=holder.is_promoter,
        )

    def _map_position_dto(self, pos: OwnershipPosition) -> OwnershipPositionDTO:
        """Helper to map domain OwnershipPosition to OwnershipPositionDTO."""
        return OwnershipPositionDTO(
            position_id=pos.position_id,
            company_id=pos.company_id,
            security_id=pos.security_id,
            security_name=pos.security_name,
            share_class=pos.share_class,
            holder=self._map_holder_summary(pos.holder),
            shares_held=float(pos.shares_held),
            formatted_shares=format_shares_count(pos.shares_held),
            position_type=pos.position_type,
            ownership_form=pos.ownership_form,
            source_reported_percentage=float(pos.source_reported_percentage) if pos.source_reported_percentage is not None else None,
            calculated_percentage=float(pos.calculated_percentage) if pos.calculated_percentage is not None else None,
            formatted_percentage=format_percentage(pos.calculated_percentage or pos.source_reported_percentage),
            voting_percentage=float(pos.voting_percentage) if pos.voting_percentage is not None else None,
            reporting_date=pos.reporting_date,
            filing_date=pos.filing_date,
            filing_delay_days=pos.filing_delay_days,
            disclosure_type=pos.disclosure_type,
            jurisdiction=pos.jurisdiction,
            source_document_id=pos.source_document_id,
            is_amendment=pos.is_amendment,
            notes=pos.notes,
        )
