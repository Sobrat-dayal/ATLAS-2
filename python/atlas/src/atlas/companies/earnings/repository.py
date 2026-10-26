"""Earnings Repository and Store for Company Earnings Intelligence (Stage 84).

Integrates corporate earnings events, reported financial actuals from Stage 82 Financial
Statements, pre-release consensus estimates, management guidance, and earnings call records.
"""

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from atlas.companies.earnings.enums import (
    AccountingBasis,
    EarningsEventStatus,
    EarningsEventType,
    EarningsPeriodType,
    GuidanceMetricType,
    GuidanceStatus,
    MarketSession,
    TranscriptStatus,
)
from atlas.companies.earnings.models import (
    ConsensusSnapshot,
    EarningsActual,
    EarningsCall,
    EarningsEvent,
    ManagementGuidance,
)
from atlas.companies.statements.enums import StatementPeriodType, StatementType
from atlas.companies.statements.repository import CompanyStatementsRepository

# Primary in-memory stores
_EARNINGS_EVENTS_STORE: Dict[str, EarningsEvent] = {}
_EARNINGS_ACTUALS_STORE: Dict[Tuple[uuid.UUID, str], EarningsActual] = {}
_CONSENSUS_STORE: Dict[Tuple[uuid.UUID, str], ConsensusSnapshot] = {}
_GUIDANCE_STORE: Dict[str, ManagementGuidance] = {}
_EARNINGS_CALLS_STORE: Dict[Tuple[uuid.UUID, str], EarningsCall] = {}


def clear_earnings_store(company_id: Optional[uuid.UUID] = None) -> None:
    """Clears stores, optionally filtered by company ID (for test teardown)."""
    global _EARNINGS_EVENTS_STORE, _EARNINGS_ACTUALS_STORE, _CONSENSUS_STORE, _GUIDANCE_STORE, _EARNINGS_CALLS_STORE
    if company_id is None:
        _EARNINGS_EVENTS_STORE.clear()
        _EARNINGS_ACTUALS_STORE.clear()
        _CONSENSUS_STORE.clear()
        _GUIDANCE_STORE.clear()
        _EARNINGS_CALLS_STORE.clear()
    else:
        _EARNINGS_EVENTS_STORE = {
            k: v for k, v in _EARNINGS_EVENTS_STORE.items() if v.company_id != company_id
        }
        _EARNINGS_ACTUALS_STORE = {
            k: v for k, v in _EARNINGS_ACTUALS_STORE.items() if k[0] != company_id
        }
        _CONSENSUS_STORE = {
            k: v for k, v in _CONSENSUS_STORE.items() if k[0] != company_id
        }
        _GUIDANCE_STORE = {
            k: v for k, v in _GUIDANCE_STORE.items() if v.company_id != company_id
        }
        _EARNINGS_CALLS_STORE = {
            k: v for k, v in _EARNINGS_CALLS_STORE.items() if k[0] != company_id
        }


class CompanyEarningsRepository:
    """Authoritative repository for company earnings intelligence."""

    def __init__(self, statements_repo: Optional[CompanyStatementsRepository] = None) -> None:
        self.statements_repo = statements_repo or CompanyStatementsRepository()
        _seed_canonical_reference_earnings()

    def register_event(self, event: EarningsEvent) -> None:
        """Registers a corporate earnings event."""
        _EARNINGS_EVENTS_STORE[event.event_id] = event

    def register_actual(self, actual: EarningsActual) -> None:
        """Registers reported financial actuals for a company fiscal period."""
        _EARNINGS_ACTUALS_STORE[(actual.company_id, actual.fiscal_period)] = actual

    def register_consensus(self, consensus: ConsensusSnapshot) -> None:
        """Registers a qualified pre-release consensus estimate snapshot."""
        _CONSENSUS_STORE[(consensus.company_id, consensus.fiscal_period)] = consensus

    def register_guidance(self, guidance: ManagementGuidance) -> None:
        """Registers management guidance."""
        _GUIDANCE_STORE[guidance.guidance_id] = guidance

    def register_call(self, call: EarningsCall) -> None:
        """Registers an earnings call reference."""
        _EARNINGS_CALLS_STORE[(call.company_id, call.fiscal_period)] = call

    def get_event_by_id(self, event_id: str) -> Optional[EarningsEvent]:
        """Looks up an event by its unique ID."""
        return _EARNINGS_EVENTS_STORE.get(event_id)

    def get_events(
        self,
        company_id: uuid.UUID,
        status: Optional[EarningsEventStatus] = None,
    ) -> List[EarningsEvent]:
        """Retrieves earnings events for a company, sorted chronologically."""
        events = [e for e in _EARNINGS_EVENTS_STORE.values() if e.company_id == company_id]
        if status:
            events = [e for e in events if e.status == status]

        # Sort by announced_date descending
        return sorted(
            events,
            key=lambda x: (x.announced_date or datetime.date.min, x.announced_time or datetime.time.min),
            reverse=True,
        )

    def get_next_event(self, company_id: uuid.UUID) -> Optional[EarningsEvent]:
        """Returns the next scheduled/upcoming earnings event for a company."""
        today = datetime.date.today()
        upcoming = [
            e
            for e in _EARNINGS_EVENTS_STORE.values()
            if e.company_id == company_id
            and e.status in (EarningsEventStatus.CONFIRMED, EarningsEventStatus.ESTIMATED, EarningsEventStatus.TENTATIVE)
            and (e.announced_date is None or e.announced_date >= today)
        ]
        if not upcoming:
            return None
        # Sort ascending to get earliest upcoming event
        return sorted(upcoming, key=lambda x: x.announced_date or datetime.date.max)[0]

    def get_latest_completed_event(self, company_id: uuid.UUID) -> Optional[EarningsEvent]:
        """Returns the most recent completed earnings release event."""
        completed = [
            e
            for e in _EARNINGS_EVENTS_STORE.values()
            if e.company_id == company_id and e.status == EarningsEventStatus.COMPLETED
        ]
        if not completed:
            return None
        return sorted(completed, key=lambda x: x.announced_date or datetime.date.min, reverse=True)[0]

    def get_actual(self, company_id: uuid.UUID, fiscal_period: str) -> Optional[EarningsActual]:
        """Retrieves reported actuals from earnings store, falling back to Stage 82 Statements."""
        # 1. Direct earnings store lookup
        if (company_id, fiscal_period) in _EARNINGS_ACTUALS_STORE:
            return _EARNINGS_ACTUALS_STORE[(company_id, fiscal_period)]

        # 2. Stage 82 Financial Statements integration fallback
        stmt = self.statements_repo.get_statement(
            company_id=company_id,
            statement_type=StatementType.INCOME_STATEMENT,
            period_id=fiscal_period,
        )
        if stmt:
            facts = stmt.get("facts", {})
            period_type = (
                EarningsPeriodType.ANNUAL
                if stmt.get("period_type") == StatementPeriodType.ANNUAL
                else EarningsPeriodType.QUARTERLY
            )
            actual = EarningsActual(
                actual_id=f"act_{fiscal_period}_{uuid.uuid4().hex[:6]}",
                company_id=company_id,
                fiscal_period=fiscal_period,
                period_type=period_type,
                diluted_eps=facts.get("diluted_eps"),
                basic_eps=facts.get("basic_eps"),
                revenue=facts.get("revenue"),
                net_income=facts.get("net_income"),
                reporting_currency=stmt.get("reporting_currency", "USD"),
                is_restated=stmt.get("is_restated", False),
                announcement_date=stmt.get("filing_date"),
                reported_at=stmt.get("reported_at"),
                source_statement_id=fiscal_period,
            )
            # Cache dynamically
            _EARNINGS_ACTUALS_STORE[(company_id, fiscal_period)] = actual
            return actual

        return None

    def get_all_actuals(
        self,
        company_id: uuid.UUID,
        period_type: Optional[EarningsPeriodType] = None,
    ) -> List[EarningsActual]:
        """Retrieves all reported actuals for a company."""
        # Also ensure Stage 82 periods are checked
        cat = self.statements_repo.get_statement_catalog(company_id)
        for p in cat.available_periods:
            self.get_actual(company_id, p.period_id)

        actuals = [a for a in _EARNINGS_ACTUALS_STORE.values() if a.company_id == company_id]
        if period_type:
            actuals = [a for a in actuals if a.period_type == period_type]

        return sorted(
            actuals,
            key=lambda x: x.announcement_date or datetime.date.min,
            reverse=True,
        )

    def get_consensus(self, company_id: uuid.UUID, fiscal_period: str) -> Optional[ConsensusSnapshot]:
        """Retrieves pre-release consensus estimates for a period."""
        return _CONSENSUS_STORE.get((company_id, fiscal_period))

    def get_all_consensus(self, company_id: uuid.UUID) -> List[ConsensusSnapshot]:
        """Retrieves all consensus snapshots for a company."""
        return [c for c in _CONSENSUS_STORE.values() if c.company_id == company_id]

    def get_guidance(
        self,
        company_id: uuid.UUID,
        status: Optional[GuidanceStatus] = None,
    ) -> List[ManagementGuidance]:
        """Retrieves management guidance items."""
        items = [g for g in _GUIDANCE_STORE.values() if g.company_id == company_id]
        if status:
            items = [g for g in items if g.status == status]
        return sorted(items, key=lambda x: x.issued_at, reverse=True)

    def get_calls(self, company_id: uuid.UUID) -> List[EarningsCall]:
        """Retrieves earnings call events and transcript links."""
        calls = [c for c in _EARNINGS_CALLS_STORE.values() if c.company_id == company_id]
        return sorted(calls, key=lambda x: x.call_datetime or datetime.datetime.min, reverse=True)


# ---------------------------------------------------------------------------
# Canonical Reference Seeding (Apple Inc. c0000000-0000-0000-0000-000000000001)
# ---------------------------------------------------------------------------
def _seed_canonical_reference_earnings() -> None:
    apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
    if (apple_id, "Q4-2024") in _EARNINGS_ACTUALS_STORE:
        return  # Already seeded

    # Historical Quarters Data: (Period, Date, Session, Actual EPS, Est EPS, Actual Rev, Est Rev, Confirmed)
    quarters_data = [
        ("Q1-2024", datetime.date(2024, 2, 1), MarketSession.AFTER_MARKET, Decimal("2.18"), Decimal("2.10"), Decimal("119575000000"), Decimal("117910000000"), True),
        ("Q2-2024", datetime.date(2024, 5, 2), MarketSession.AFTER_MARKET, Decimal("1.53"), Decimal("1.50"), Decimal("90753000000"), Decimal("90010000000"), True),
        ("Q3-2024", datetime.date(2024, 8, 1), MarketSession.AFTER_MARKET, Decimal("1.40"), Decimal("1.35"), Decimal("85777000000"), Decimal("84530000000"), True),
        ("Q4-2024", datetime.date(2024, 10, 31), MarketSession.AFTER_MARKET, Decimal("1.64"), Decimal("1.60"), Decimal("94930000000"), Decimal("94560000000"), True),
    ]

    for pid, dt, session, a_eps, e_eps, a_rev, e_rev, conf in quarters_data:
        # 1. Event
        event_id = f"evt_{pid}_{apple_id.hex[:6]}"
        _EARNINGS_EVENTS_STORE[event_id] = EarningsEvent(
            event_id=event_id,
            company_id=apple_id,
            fiscal_period=pid,
            fiscal_year=2024,
            fiscal_quarter=pid.split("-")[0],
            event_type=EarningsEventType.EARNINGS_RELEASE,
            status=EarningsEventStatus.COMPLETED,
            announced_date=dt,
            announced_time=datetime.time(16, 30),
            timezone="America/New_York",
            market_session=session,
            is_confirmed=conf,
            source="CANONICAL",
            webcast_url="https://www.apple.com/investor/earnings-call/",
        )

        # 2. Actuals
        _EARNINGS_ACTUALS_STORE[(apple_id, pid)] = EarningsActual(
            actual_id=f"act_{pid}_{apple_id.hex[:6]}",
            company_id=apple_id,
            fiscal_period=pid,
            period_type=EarningsPeriodType.QUARTERLY,
            diluted_eps=a_eps,
            basic_eps=a_eps + Decimal("0.01"),
            revenue=a_rev,
            reporting_currency="USD",
            accounting_basis=AccountingBasis.GAAP,
            announcement_date=dt,
            reported_at=datetime.datetime.combine(dt, datetime.time(16, 30)),
            source_statement_id=pid,
        )

        # 3. Consensus Snapshot
        _CONSENSUS_STORE[(apple_id, pid)] = ConsensusSnapshot(
            consensus_id=f"cons_{pid}_{apple_id.hex[:6]}",
            company_id=apple_id,
            fiscal_period=pid,
            period_type=EarningsPeriodType.QUARTERLY,
            consensus_eps=e_eps,
            consensus_revenue=e_rev,
            eps_high=e_eps + Decimal("0.08"),
            eps_low=e_eps - Decimal("0.06"),
            revenue_high=e_rev + Decimal("1500000000"),
            revenue_low=e_rev - Decimal("1200000000"),
            analyst_count=32,
            methodology="MEAN",
            snapshot_timestamp=datetime.datetime.combine(dt - datetime.timedelta(days=1), datetime.time(18, 0)),
            pre_release_cutoff=True,
        )

        # 4. Earnings Call
        _EARNINGS_CALLS_STORE[(apple_id, pid)] = EarningsCall(
            call_id=f"call_{pid}_{apple_id.hex[:6]}",
            company_id=apple_id,
            fiscal_period=pid,
            call_datetime=datetime.datetime.combine(dt, datetime.time(17, 0)),
            timezone="America/New_York",
            webcast_url="https://www.apple.com/investor/earnings-call/",
            transcript_document_id=f"doc_transcript_{pid}",
            transcript_status=TranscriptStatus.AVAILABLE,
            audio_available=True,
            key_topics=["Services Momentum", "Gross Margin Expansion", "Apple Intelligence", "iPhone 16 Demand"],
        )

    # 5. Upcoming Next Scheduled Release: Q1-2025
    next_pid = "Q1-2025"
    next_date = datetime.date.today() + datetime.timedelta(days=45)
    next_evt_id = f"evt_{next_pid}_{apple_id.hex[:6]}"
    _EARNINGS_EVENTS_STORE[next_evt_id] = EarningsEvent(
        event_id=next_evt_id,
        company_id=apple_id,
        fiscal_period=next_pid,
        fiscal_year=2025,
        fiscal_quarter="Q1",
        event_type=EarningsEventType.EARNINGS_RELEASE,
        status=EarningsEventStatus.CONFIRMED,
        announced_date=next_date,
        announced_time=datetime.time(16, 30),
        timezone="America/New_York",
        market_session=MarketSession.AFTER_MARKET,
        is_confirmed=True,
        source="CANONICAL",
        webcast_url="https://www.apple.com/investor/earnings-call/",
    )

    # Consensus for upcoming Q1-2025
    _CONSENSUS_STORE[(apple_id, next_pid)] = ConsensusSnapshot(
        consensus_id=f"cons_{next_pid}_{apple_id.hex[:6]}",
        company_id=apple_id,
        fiscal_period=next_pid,
        period_type=EarningsPeriodType.QUARTERLY,
        consensus_eps=Decimal("2.36"),
        consensus_revenue=Decimal("124200000000"),
        eps_high=Decimal("2.45"),
        eps_low=Decimal("2.28"),
        revenue_high=Decimal("126500000000"),
        revenue_low=Decimal("122000000000"),
        analyst_count=35,
        methodology="MEAN",
        snapshot_timestamp=datetime.datetime.utcnow(),
        pre_release_cutoff=True,
    )

    # 6. Active Management Guidance
    guidance_items = [
        ManagementGuidance(
            guidance_id="gid_q1_rev",
            company_id=apple_id,
            fiscal_period="Q1-2025",
            metric=GuidanceMetricType.REVENUE,
            low_value=Decimal("123000000000"),
            high_value=Decimal("126000000000"),
            currency="USD",
            accounting_basis=AccountingBasis.GAAP,
            issued_at=datetime.date(2024, 10, 31),
            status=GuidanceStatus.ACTIVE,
            notes="Expect revenue to grow low to mid single digits year over year.",
            source_document="Q4 FY24 Earnings Call & Press Release",
        ),
        ManagementGuidance(
            guidance_id="gid_q1_margin",
            company_id=apple_id,
            fiscal_period="Q1-2025",
            metric=GuidanceMetricType.GROSS_MARGIN,
            low_value=Decimal("46.0"),
            high_value=Decimal("47.0"),
            currency="PERCENT",
            accounting_basis=AccountingBasis.GAAP,
            issued_at=datetime.date(2024, 10, 31),
            status=GuidanceStatus.ACTIVE,
            notes="Gross margin expected between 46.0% and 47.0%.",
            source_document="Q4 FY24 Press Release",
        ),
    ]
    for g in guidance_items:
        _GUIDANCE_STORE[g.guidance_id] = g
