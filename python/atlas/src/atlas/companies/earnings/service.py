"""Service layer for Company Earnings Intelligence (Stage 84).

Orchestrates corporate earnings events, actual results from Stage 82 Financial Statements,
pre-release consensus estimate snapshots, pure Decimal surprises, management guidance,
and earnings call references.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import List, Optional

from atlas.companies.earnings.calculator import (
    calculate_eps_surprise,
    calculate_revenue_surprise,
    format_eps,
    format_percentage,
    format_revenue,
)
from atlas.companies.earnings.enums import (
    EarningsEventStatus,
    EarningsPeriodType,
    GuidanceStatus,
)
from atlas.companies.earnings.errors import (
    EarningsEventNotFoundError,
)
from atlas.companies.earnings.models import (
    ConsensusSnapshot,
    EarningsActual,
    EarningsCall,
    EarningsEvent,
    ManagementGuidance,
)
from atlas.companies.earnings.repository import CompanyEarningsRepository
from atlas.companies.earnings.schemas import (
    CompanyEarningsOverviewDTO,
    ConsensusSnapshotDTO,
    EarningsCallDTO,
    EarningsCallsResponseDTO,
    EarningsEventDTO,
    EarningsEventsResponseDTO,
    EarningsHistoryResponseDTO,
    GuidanceResponseDTO,
    ManagementGuidanceDTO,
    QuarterlyEarningsItemDTO,
)
from atlas.entities.service import EntityService


class CompanyEarningsService:
    """Institutional service for corporate earnings intelligence and fundamental analysis."""

    def __init__(
        self,
        repository: Optional[CompanyEarningsRepository] = None,
        entity_service: Optional[EntityService] = None,
    ) -> None:
        self.repository = repository or CompanyEarningsRepository()
        self.entity_service = entity_service

    async def _resolve_company_name(self, company_id: uuid.UUID) -> str:
        """Resolves verified canonical company display name."""
        if self.entity_service:
            try:
                ent = await self.entity_service.get_entity(company_id)
                if ent and ent.display_name:
                    return ent.display_name
            except Exception:
                pass
        return "Company"

    def _build_quarterly_item(
        self,
        company_id: uuid.UUID,
        actual: Optional[EarningsActual],
        event: Optional[EarningsEvent],
        consensus: Optional[ConsensusSnapshot],
        fiscal_period: str,
    ) -> QuarterlyEarningsItemDTO:
        """Builds an integrated quarterly earnings row with exact surprise arithmetic."""
        currency = actual.reporting_currency if actual else "USD"
        act_eps = actual.diluted_eps if actual else None
        est_eps = consensus.consensus_eps if consensus else None

        eps_abs, eps_pct, eps_class = calculate_eps_surprise(act_eps, est_eps)

        act_rev = actual.revenue if actual else None
        est_rev = consensus.consensus_revenue if consensus else None

        rev_abs, rev_pct, rev_class = calculate_revenue_surprise(act_rev, est_rev)

        # Parse fiscal year and quarter
        fy = 2024
        fq = None
        if event:
            fy = event.fiscal_year
            fq = event.fiscal_quarter
        elif actual and "-" in fiscal_period:
            try:
                parts = fiscal_period.split("-")
                fq = parts[0]
                fy = int(parts[1])
            except Exception:
                pass

        return QuarterlyEarningsItemDTO(
            fiscal_period=fiscal_period,
            fiscal_year=fy,
            fiscal_quarter=fq,
            announced_date=event.announced_date.isoformat() if event and event.announced_date else (
                actual.announcement_date.isoformat() if actual and actual.announcement_date else None
            ),
            market_session=event.market_session if event else "UNSPECIFIED",
            status=event.status if event else EarningsEventStatus.COMPLETED,
            actual_eps=float(act_eps) if act_eps is not None else None,
            formatted_actual_eps=format_eps(act_eps, currency),
            estimate_eps=float(est_eps) if est_eps is not None else None,
            formatted_estimate_eps=format_eps(est_eps, currency),
            eps_surprise_abs=float(eps_abs) if eps_abs is not None else None,
            eps_surprise_pct=float(eps_pct) if eps_pct is not None else None,
            formatted_eps_surprise_pct=format_percentage(eps_pct),
            eps_classification=eps_class,
            actual_revenue=float(act_rev) if act_rev is not None else None,
            formatted_actual_revenue=format_revenue(act_rev, currency),
            estimate_revenue=float(est_rev) if est_rev is not None else None,
            formatted_estimate_revenue=format_revenue(est_rev, currency),
            revenue_surprise_abs=float(rev_abs) if rev_abs is not None else None,
            revenue_surprise_pct=float(rev_pct) if rev_pct is not None else None,
            formatted_revenue_surprise_pct=format_percentage(rev_pct),
            revenue_classification=rev_class,
            currency=currency,
            is_restated=actual.is_restated if actual else False,
            source="CANONICAL",
        )

    def _event_to_dto(self, event: EarningsEvent) -> EarningsEventDTO:
        """Converts an EarningsEvent model to its DTO."""
        return EarningsEventDTO(
            event_id=event.event_id,
            company_id=str(event.company_id),
            fiscal_period=event.fiscal_period,
            fiscal_year=event.fiscal_year,
            fiscal_quarter=event.fiscal_quarter,
            event_type=event.event_type,
            status=event.status,
            announced_date=event.announced_date.isoformat() if event.announced_date else None,
            announced_time=event.announced_time.isoformat() if event.announced_time else None,
            timezone=event.timezone,
            market_session=event.market_session,
            is_confirmed=event.is_confirmed,
            source=event.source,
            webcast_url=event.webcast_url,
        )

    def _guidance_to_dto(self, g: ManagementGuidance) -> ManagementGuidanceDTO:
        """Converts ManagementGuidance to its DTO with human-readable range format."""
        if g.low_value is not None and g.high_value is not None:
            if g.currency == "PERCENT":
                formatted_range = f"{g.low_value:.1f}% - {g.high_value:.1f}%"
            elif g.low_value >= Decimal("1000000000"):
                formatted_range = f"${g.low_value / Decimal('1000000000'):.1f}B - ${g.high_value / Decimal('1000000000'):.1f}B"
            else:
                formatted_range = f"${g.low_value:.2f} - ${g.high_value:.2f}"
        elif g.point_value is not None:
            formatted_range = f"${g.point_value:.2f}"
        else:
            formatted_range = "—"

        return ManagementGuidanceDTO(
            guidance_id=g.guidance_id,
            fiscal_period=g.fiscal_period,
            metric=g.metric,
            low_value=float(g.low_value) if g.low_value is not None else None,
            high_value=float(g.high_value) if g.high_value is not None else None,
            point_value=float(g.point_value) if g.point_value is not None else None,
            formatted_range=formatted_range,
            currency=g.currency,
            accounting_basis=g.accounting_basis,
            issued_at=g.issued_at.isoformat(),
            status=g.status,
            notes=g.notes,
            source_document=g.source_document,
        )

    def _call_to_dto(self, c: EarningsCall) -> EarningsCallDTO:
        """Converts EarningsCall to DTO."""
        return EarningsCallDTO(
            call_id=c.call_id,
            fiscal_period=c.fiscal_period,
            call_datetime=c.call_datetime.isoformat() if c.call_datetime else None,
            timezone=c.timezone,
            webcast_url=c.webcast_url,
            transcript_document_id=c.transcript_document_id,
            transcript_status=c.transcript_status,
            audio_available=c.audio_available,
            key_topics=c.key_topics,
        )

    async def get_earnings_overview(self, company_id: uuid.UUID) -> CompanyEarningsOverviewDTO:
        """Returns comprehensive latest and upcoming earnings overview for a company."""
        company_name = await self._resolve_company_name(company_id)

        # 1. Latest completed event
        latest_evt = self.repository.get_latest_completed_event(company_id)
        latest_item = None
        if latest_evt:
            actual = self.repository.get_actual(company_id, latest_evt.fiscal_period)
            consensus = self.repository.get_consensus(company_id, latest_evt.fiscal_period)
            latest_item = self._build_quarterly_item(
                company_id=company_id,
                actual=actual,
                event=latest_evt,
                consensus=consensus,
                fiscal_period=latest_evt.fiscal_period,
            )

        # 2. Next scheduled event
        next_evt = self.repository.get_next_event(company_id)
        next_evt_dto = self._event_to_dto(next_evt) if next_evt else None

        # Next consensus
        next_consensus_dto = None
        if next_evt:
            next_cons = self.repository.get_consensus(company_id, next_evt.fiscal_period)
            if next_cons:
                next_consensus_dto = ConsensusSnapshotDTO(
                    consensus_id=next_cons.consensus_id,
                    fiscal_period=next_cons.fiscal_period,
                    period_type=next_cons.period_type,
                    consensus_eps=float(next_cons.consensus_eps) if next_cons.consensus_eps is not None else None,
                    consensus_revenue=float(next_cons.consensus_revenue) if next_cons.consensus_revenue is not None else None,
                    formatted_eps=format_eps(next_cons.consensus_eps),
                    formatted_revenue=format_revenue(next_cons.consensus_revenue),
                    eps_high=float(next_cons.eps_high) if next_cons.eps_high is not None else None,
                    eps_low=float(next_cons.eps_low) if next_cons.eps_low is not None else None,
                    revenue_high=float(next_cons.revenue_high) if next_cons.revenue_high is not None else None,
                    revenue_low=float(next_cons.revenue_low) if next_cons.revenue_low is not None else None,
                    analyst_count=next_cons.analyst_count,
                    methodology=next_cons.methodology,
                    snapshot_timestamp=next_cons.snapshot_timestamp.isoformat() if next_cons.snapshot_timestamp else None,
                    pre_release_cutoff=next_cons.pre_release_cutoff,
                )

        # 3. Active guidance items
        guidance_items = [
            self._guidance_to_dto(g)
            for g in self.repository.get_guidance(company_id, status=GuidanceStatus.ACTIVE)
        ]

        # 4. Latest earnings call
        calls = self.repository.get_calls(company_id)
        latest_call_dto = self._call_to_dto(calls[0]) if calls else None

        # 5. Recent quarters history (up to 4 quarters)
        history_resp = await self.get_earnings_history(company_id, limit=4)

        return CompanyEarningsOverviewDTO(
            company_id=str(company_id),
            company_name=company_name,
            latest_completed=latest_item,
            next_scheduled=next_evt_dto,
            next_consensus=next_consensus_dto,
            active_guidance=guidance_items,
            latest_call=latest_call_dto,
            recent_history=history_resp.items,
        )

    async def get_earnings_history(
        self,
        company_id: uuid.UUID,
        period_type: EarningsPeriodType = EarningsPeriodType.QUARTERLY,
        limit: int = 16,
    ) -> EarningsHistoryResponseDTO:
        """Retrieves verified multi-period earnings history with actuals and surprises."""
        company_name = await self._resolve_company_name(company_id)

        # Collect all actuals and events
        actuals = self.repository.get_all_actuals(company_id, period_type=period_type)
        events = {e.fiscal_period: e for e in self.repository.get_events(company_id)}

        # Also collect periods from events that might not have actuals yet
        periods_seen = set()
        items: List[QuarterlyEarningsItemDTO] = []

        for act in actuals:
            pid = act.fiscal_period
            periods_seen.add(pid)
            evt = events.get(pid)
            cons = self.repository.get_consensus(company_id, pid)
            item = self._build_quarterly_item(
                company_id=company_id,
                actual=act,
                event=evt,
                consensus=cons,
                fiscal_period=pid,
            )
            items.append(item)

        # Sort chronologically descending
        items = sorted(
            items,
            key=lambda x: (x.announced_date or "", x.fiscal_period),
            reverse=True,
        )

        # Apply limit
        items = items[:limit]

        return EarningsHistoryResponseDTO(
            company_id=str(company_id),
            company_name=company_name,
            period_type=period_type,
            total_count=len(items),
            items=items,
        )

    async def get_earnings_events(
        self,
        company_id: uuid.UUID,
        status: Optional[EarningsEventStatus] = None,
    ) -> EarningsEventsResponseDTO:
        """Returns verified earnings announcement events."""
        company_name = await self._resolve_company_name(company_id)
        events = self.repository.get_events(company_id, status=status)
        dtos = [self._event_to_dto(e) for e in events]

        return EarningsEventsResponseDTO(
            company_id=str(company_id),
            company_name=company_name,
            total_count=len(dtos),
            events=dtos,
        )

    async def get_event_detail(self, company_id: uuid.UUID, event_id: str) -> EarningsEventDTO:
        """Looks up a specific earnings event."""
        evt = self.repository.get_event_by_id(event_id)
        if not evt or evt.company_id != company_id:
            raise EarningsEventNotFoundError(event_id)
        return self._event_to_dto(evt)

    async def get_management_guidance(
        self,
        company_id: uuid.UUID,
        status: Optional[GuidanceStatus] = None,
    ) -> GuidanceResponseDTO:
        """Returns company management guidance items."""
        company_name = await self._resolve_company_name(company_id)
        items = self.repository.get_guidance(company_id, status=status)
        dtos = [self._guidance_to_dto(g) for g in items]

        return GuidanceResponseDTO(
            company_id=str(company_id),
            company_name=company_name,
            total_count=len(dtos),
            guidance_items=dtos,
        )

    async def get_earnings_calls(self, company_id: uuid.UUID) -> EarningsCallsResponseDTO:
        """Returns verified earnings call records and transcript documents."""
        company_name = await self._resolve_company_name(company_id)
        calls = self.repository.get_calls(company_id)
        dtos = [self._call_to_dto(c) for c in calls]

        return EarningsCallsResponseDTO(
            company_id=str(company_id),
            company_name=company_name,
            total_count=len(dtos),
            calls=dtos,
        )
