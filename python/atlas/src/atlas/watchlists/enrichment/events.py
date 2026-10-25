"""Corporate Events and Earnings Metadata Adapter for Watchlist Enrichment (Stage 79).

Projects verified corporate event dates and earnings performance metrics:
- events.next_earnings_date
- events.last_earnings_date
- events.next_ex_dividend_date
- events.dividend_payment_date
- earnings.reported_eps
- earnings.estimated_eps
- earnings.eps_surprise_pct

Financial Semantics & Invariants:
- Status Differentiation: Clearly distinguishes CONFIRMED vs ESTIMATED event dates.
- Date-Only Semantics: Never assigns fake exact intraday UTC seconds to date-only corporate events.
- Surprise Calculation: (Actual - Estimate) / |Estimate| * 100. Protected against zero/missing estimates.
- Strict entity scope: Operates on verified issuer company relationships.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from .caching import default_enrichment_cache
from .models import EnrichmentCategory, EnrichmentStatus, WatchlistEnrichmentValue

logger = logging.getLogger(__name__)


# Verified Corporate Event Reference Record
class VerifiedCorporateEvent:
    def __init__(
        self,
        event_type: str,  # "earnings" | "dividend" | "split"
        event_date: datetime.date,
        event_status: str = "CONFIRMED",  # "CONFIRMED" | "ESTIMATED"
        source: str = "CANONICAL",
        reported_eps: Optional[float] = None,
        estimated_eps: Optional[float] = None,
        ex_dividend_date: Optional[datetime.date] = None,
        payment_date: Optional[datetime.date] = None,
    ):
        self.event_type = event_type
        self.event_date = event_date
        self.event_status = event_status
        self.source = source
        self.reported_eps = reported_eps
        self.estimated_eps = estimated_eps
        self.ex_dividend_date = ex_dividend_date
        self.payment_date = payment_date


# In-memory verified events store: (company_id -> List[VerifiedCorporateEvent])
_CORPORATE_EVENTS_STORE: Dict[UUID, Dict[str, Any]] = {}


def register_verified_events_for_company(
    company_id: UUID,
    next_earnings_date: Optional[Any] = None,
    next_earnings_status: str = "CONFIRMED",
    last_earnings_date: Optional[Any] = None,
    reported_eps: Optional[float] = None,
    estimated_eps: Optional[float] = None,
    next_ex_dividend_date: Optional[Any] = None,
    dividend_payment_date: Optional[Any] = None,
    events_data: Optional[Dict[str, Any]] = None,
) -> None:
    """Helper to seed verified corporate events and earnings metadata."""
    if events_data is not None:
        store_entry: Dict[str, Any] = {}
        if "next_earnings" in events_data:
            ne = events_data["next_earnings"]
            d = ne.get("date")
            store_entry["next_earnings_date"] = (
                datetime.date.fromisoformat(d) if isinstance(d, str) else d
            )
            store_entry["next_earnings_status"] = ne.get("status", "CONFIRMED")
            if "estimated_eps" in ne:
                store_entry["estimated_eps"] = ne["estimated_eps"]
        if "last_earnings" in events_data:
            le = events_data["last_earnings"]
            d = le.get("date")
            store_entry["last_earnings_date"] = (
                datetime.date.fromisoformat(d) if isinstance(d, str) else d
            )
            if "reported_eps" in le:
                store_entry["reported_eps"] = le["reported_eps"]
            if "estimated_eps" in le:
                store_entry["estimated_eps"] = le["estimated_eps"]
            if "surprise_pct" in le:
                store_entry["surprise_pct"] = le["surprise_pct"]
        if "next_ex_dividend" in events_data:
            ned = events_data["next_ex_dividend"]
            d = ned.get("date")
            store_entry["next_ex_dividend_date"] = (
                datetime.date.fromisoformat(d) if isinstance(d, str) else d
            )
        if "dividend_payment" in events_data:
            dp = events_data["dividend_payment"]
            d = dp.get("date")
            store_entry["dividend_payment_date"] = (
                datetime.date.fromisoformat(d) if isinstance(d, str) else d
            )
        for k, v in events_data.items():
            if k not in store_entry and not isinstance(v, dict):
                store_entry[k] = v
        _CORPORATE_EVENTS_STORE[company_id] = store_entry
    else:
        _CORPORATE_EVENTS_STORE[company_id] = {
            "next_earnings_date": next_earnings_date,
            "next_earnings_status": next_earnings_status,
            "last_earnings_date": last_earnings_date,
            "reported_eps": reported_eps,
            "estimated_eps": estimated_eps,
            "next_ex_dividend_date": next_ex_dividend_date,
            "dividend_payment_date": dividend_payment_date,
        }


class CorporateEventsAdapter:
    """Adapter projecting corporate events and earnings metadata into WatchlistEnrichmentValues."""

    def __init__(self, session: Optional[Any] = None) -> None:
        self.session = session
        self.cache = default_enrichment_cache

    def get_event_metric(
        self,
        column_id: str = "",
        asset_class: str = "equity",
        instrument_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> WatchlistEnrichmentValue:
        comp_id = company_id if company_id is not None else kwargs.get("company_id")
        inst_id = instrument_id if instrument_id is not None else kwargs.get("instrument_id")
        ac = asset_class if asset_class else kwargs.get("asset_class", "equity")
        cid = column_id if column_id else kwargs.get("column_id", "")
        return self.get_event_or_earnings_metric(
            column_id=cid,
            asset_class=ac,
            instrument_id=inst_id,
            company_id=comp_id,
        )

    def get_earnings_metric(
        self,
        column_id: str = "",
        asset_class: str = "equity",
        instrument_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> WatchlistEnrichmentValue:
        return self.get_event_metric(
            column_id=column_id,
            asset_class=asset_class,
            instrument_id=instrument_id,
            company_id=company_id,
            **kwargs,
        )

    def get_event_or_earnings_metric(
        self,
        column_id: str,
        asset_class: str,
        instrument_id: UUID,
        company_id: Optional[UUID],
    ) -> WatchlistEnrichmentValue:
        """Projects a corporate event date or earnings fact for an instrument/company."""
        # 1. Asset class compatibility
        if asset_class.lower() not in ("equity", "etf", "fund"):
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.NOT_APPLICABLE,
                entity_id=instrument_id,
                reason=f"Corporate events do not apply to asset class '{asset_class}'",
            )

        if company_id is None:
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.NOT_APPLICABLE,
                entity_id=instrument_id,
                reason="No verified issuing company relationship found",
            )

        # 2. Check cache
        cache_key = self.cache.make_event_key(company_id, column_id)
        category = (
            EnrichmentCategory.EARNINGS
            if column_id.startswith("earnings.")
            else EnrichmentCategory.EVENTS
        )
        cached = self.cache.get(category, cache_key)
        if cached is not None:
            return cached

        # 3. Retrieve event data
        event_data = _CORPORATE_EVENTS_STORE.get(company_id, {})
        result = self._extract_event_metric(
            column_id=column_id,
            company_id=company_id,
            instrument_id=instrument_id,
            event_data=event_data,
        )

        self.cache.set(category, cache_key, result)
        return result

    def _extract_event_metric(
        self,
        column_id: str,
        company_id: UUID,
        instrument_id: UUID,
        event_data: Dict[str, Any],
    ) -> WatchlistEnrichmentValue:
        # ---------------------------------------------------------------------
        # Next Earnings Date
        # ---------------------------------------------------------------------
        if column_id == "events.next_earnings_date":
            next_date: Optional[datetime.date] = event_data.get("next_earnings_date")
            if next_date is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Upcoming earnings announcement date not scheduled",
                )

            status_str = event_data.get("next_earnings_status", "CONFIRMED")
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=next_date.isoformat(),
                value_type="TIMESTAMP",
                unit="",
                entity_id=instrument_id,
                company_id=company_id,
                as_of_date=next_date.isoformat(),
                event_status=status_str,
                methodology_id="confirmed_or_estimated_earnings_schedule",
            )

        # ---------------------------------------------------------------------
        # Last Earnings Date
        # ---------------------------------------------------------------------
        elif column_id == "events.last_earnings_date":
            last_date: Optional[datetime.date] = event_data.get("last_earnings_date")
            if last_date is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Previous earnings announcement date record unavailable",
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=last_date.isoformat(),
                value_type="TIMESTAMP",
                unit="",
                entity_id=instrument_id,
                company_id=company_id,
                as_of_date=last_date.isoformat(),
                event_status="COMPLETED",
                methodology_id="historical_earnings_event",
            )

        # ---------------------------------------------------------------------
        # Next Ex-Dividend Date
        # ---------------------------------------------------------------------
        elif column_id == "events.next_ex_dividend_date":
            ex_date: Optional[datetime.date] = event_data.get("next_ex_dividend_date")
            if ex_date is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="No upcoming ex-dividend date declared",
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=ex_date.isoformat(),
                value_type="TIMESTAMP",
                unit="",
                entity_id=instrument_id,
                company_id=company_id,
                as_of_date=ex_date.isoformat(),
                event_status="CONFIRMED",
                methodology_id="corporate_distribution_ex_date",
            )

        # ---------------------------------------------------------------------
        # Dividend Payment Date
        # ---------------------------------------------------------------------
        elif column_id == "events.dividend_payment_date":
            pay_date: Optional[datetime.date] = event_data.get("dividend_payment_date")
            if pay_date is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="No upcoming dividend payment date scheduled",
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=pay_date.isoformat(),
                value_type="TIMESTAMP",
                unit="",
                entity_id=instrument_id,
                company_id=company_id,
                as_of_date=pay_date.isoformat(),
                event_status="CONFIRMED",
                methodology_id="corporate_distribution_payment_date",
            )

        # ---------------------------------------------------------------------
        # Reported EPS
        # ---------------------------------------------------------------------
        elif column_id == "earnings.reported_eps":
            rep_eps: Optional[float] = event_data.get("reported_eps")
            if rep_eps is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Reported EPS for latest earnings release unavailable",
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(rep_eps, 2),
                value_type="MONETARY",
                unit="USD",
                currency="USD",
                entity_id=instrument_id,
                company_id=company_id,
                methodology_id="latest_reported_eps_fact",
            )

        # ---------------------------------------------------------------------
        # Estimated EPS
        # ---------------------------------------------------------------------
        elif column_id == "earnings.estimated_eps":
            est_eps: Optional[float] = event_data.get("estimated_eps")
            if est_eps is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Consensus estimate EPS unavailable",
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(est_eps, 2),
                value_type="MONETARY",
                unit="USD",
                currency="USD",
                entity_id=instrument_id,
                company_id=company_id,
                methodology_id="consensus_estimate_eps",
            )

        # ---------------------------------------------------------------------
        # EPS Surprise %
        # ---------------------------------------------------------------------
        elif column_id == "earnings.eps_surprise_pct":
            rep_eps = event_data.get("reported_eps")
            est_eps = event_data.get("estimated_eps")

            if rep_eps is None or est_eps is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Both reported and estimated EPS are required for surprise % calculation",
                )

            if est_eps == 0.0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Cannot compute percentage surprise against zero consensus estimate",
                )

            surprise_pct = round(((rep_eps - est_eps) / abs(est_eps)) * 100.0, 2)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=surprise_pct,
                value_type="PERCENTAGE",
                unit="%",
                entity_id=instrument_id,
                company_id=company_id,
                methodology_id="eps_surprise_percentage",
            )

        return WatchlistEnrichmentValue(
            column_id=column_id,
            status=EnrichmentStatus.UNAVAILABLE,
            entity_id=instrument_id,
            company_id=company_id,
            reason=f"Unknown corporate event column '{column_id}'",
        )
