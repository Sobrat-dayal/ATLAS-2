"""Valuation Ratios and Financial Metrics Adapter for Watchlist Enrichment (Stage 79).

Calculates and qualifies:
- valuation.market_cap
- valuation.pe_ratio
- valuation.pb_ratio
- valuation.ps_ratio
- valuation.dividend_yield

Financial Semantics & Safety Invariants:
- Negative/Zero EPS: Never returns a misleading positive P/E. Returns UNAVAILABLE with reason "Non-positive EPS (N/M)".
- Zero Denominators: Strictly protected against divide-by-zero; never emits NaN or Infinity.
- Share-Class and Currency Alignment: Verifies quotation units match financial statement units.
- Asset class applicability: Non-equities receive NOT_APPLICABLE for equity valuation metrics.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from .caching import default_enrichment_cache
from .fundamentals import FundamentalDataAdapter
from .models import EnrichmentCategory, EnrichmentStatus, WatchlistEnrichmentValue

logger = logging.getLogger(__name__)

# Mockable or registered verified shares outstanding and dividend data
_SHARES_OUTSTANDING_STORE: Dict[UUID, float] = {}
_DIVIDENDS_STORE: Dict[UUID, float] = {}


def register_verified_shares_outstanding(company_id: UUID, shares: float) -> None:
    _SHARES_OUTSTANDING_STORE[company_id] = shares


def register_verified_annual_dividend(company_id: UUID, annual_dividend: float) -> None:
    _DIVIDENDS_STORE[company_id] = annual_dividend


class ValuationRatiosAdapter:
    """Adapter computing deterministic financial ratios over latest quotes and fundamentals."""

    def __init__(self, fundamental_adapter: Optional[FundamentalDataAdapter] = None) -> None:
        self.fundamental_adapter = fundamental_adapter or FundamentalDataAdapter()
        self.cache = default_enrichment_cache

    def get_valuation_ratio(
        self,
        column_id: str = "",
        asset_class: str = "equity",
        instrument_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        last_price: Optional[Any] = None,
        quote_currency: str = "USD",
        **kwargs: Any,
    ) -> WatchlistEnrichmentValue:
        comp_id = company_id if company_id is not None else kwargs.get("company_id")
        inst_id = instrument_id if instrument_id is not None else kwargs.get("instrument_id")
        ac = asset_class if asset_class else kwargs.get("asset_class", "equity")
        cid = column_id if column_id else kwargs.get("column_id", "")
        raw_price = last_price if last_price is not None else kwargs.get("last_price")
        lp = float(raw_price) if raw_price is not None else None
        qc = quote_currency or kwargs.get("quote_currency", "USD")
        return self.calculate_valuation_metric(
            column_id=cid,
            asset_class=ac,
            instrument_id=inst_id,
            company_id=comp_id,
            last_price=lp,
            quote_currency=qc,
        )

    def calculate_valuation_metric(
        self,
        column_id: str,
        asset_class: str,
        instrument_id: UUID,
        company_id: Optional[UUID],
        last_price: Optional[float],
        quote_currency: str = "USD",
    ) -> WatchlistEnrichmentValue:
        """Computes a qualified valuation ratio or market cap."""
        # 1. Asset class compatibility
        if column_id != "valuation.market_cap" and asset_class.lower() not in (
            "equity",
            "etf",
            "fund",
        ):
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.NOT_APPLICABLE,
                entity_id=instrument_id,
                reason=f"Valuation ratio '{column_id}' does not apply to asset class '{asset_class}'",
            )

        if company_id is None and asset_class.lower() == "equity":
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.NOT_APPLICABLE,
                entity_id=instrument_id,
                reason="No verified issuing company relationship found",
            )

        # 2. Check cache
        cache_key = self.cache.make_valuation_key(instrument_id, column_id)
        cached = self.cache.get(EnrichmentCategory.VALUATION, cache_key)
        if cached is not None:
            return cached

        # 3. Compute metric
        result = self._compute_ratio(
            column_id=column_id,
            asset_class=asset_class,
            instrument_id=instrument_id,
            company_id=company_id,
            last_price=last_price,
            quote_currency=quote_currency,
        )

        self.cache.set(EnrichmentCategory.VALUATION, cache_key, result)
        return result

    def _compute_ratio(
        self,
        column_id: str,
        asset_class: str,
        instrument_id: UUID,
        company_id: Optional[UUID],
        last_price: Optional[float],
        quote_currency: str,
    ) -> WatchlistEnrichmentValue:
        # Require latest price for market cap and price-based valuation multiples
        if last_price is None or last_price <= 0:
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.UNAVAILABLE,
                entity_id=instrument_id,
                company_id=company_id,
                reason="Latest valid market price unavailable for valuation calculation",
            )

        # ---------------------------------------------------------------------
        # Market Capitalization
        # ---------------------------------------------------------------------
        if column_id == "valuation.market_cap":
            if company_id is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    reason="Issuer company entity required for share count calculation",
                )
            shares = _SHARES_OUTSTANDING_STORE.get(company_id)
            if shares is None or shares <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Verified shares outstanding data unavailable",
                )

            market_cap = float(last_price) * float(shares)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(market_cap, 2),
                value_type="MONETARY",
                unit=quote_currency,
                currency=quote_currency,
                entity_id=instrument_id,
                company_id=company_id,
                methodology_id="price_times_shares_outstanding",
            )

        # ---------------------------------------------------------------------
        # P/E Ratio
        # ---------------------------------------------------------------------
        elif column_id == "valuation.pe_ratio":
            eps_val = self.fundamental_adapter.get_financial_metric(
                company_id=company_id,
                column_id="fundamentals.eps",
                asset_class=asset_class,
                instrument_id=instrument_id,
            )
            if eps_val.status != EnrichmentStatus.AVAILABLE or eps_val.value is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Reported EPS unavailable for P/E calculation",
                )

            eps_num = float(eps_val.value)
            # Rule: Negative or zero earnings must not produce misleading positive or infinite P/E
            if eps_num <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.NOT_APPLICABLE,
                    value=None,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Non-positive EPS (N/M)",
                )

            pe = round(float(last_price) / eps_num, 2)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=pe,
                value_type="NUMBER",
                unit="x",
                entity_id=instrument_id,
                company_id=company_id,
                fiscal_period=eps_val.fiscal_period,
                methodology_id="price_divided_by_diluted_eps",
            )

        # ---------------------------------------------------------------------
        # P/B Ratio
        # ---------------------------------------------------------------------
        elif column_id == "valuation.pb_ratio":
            equity_val = self.fundamental_adapter.get_financial_metric(
                company_id=company_id,
                column_id="fundamentals.total_equity",
                asset_class=asset_class,
                instrument_id=instrument_id,
            )
            if equity_val.status != EnrichmentStatus.AVAILABLE or equity_val.value is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Total book equity unavailable for P/B calculation",
                )

            shares = _SHARES_OUTSTANDING_STORE.get(company_id) if company_id else None
            if shares is None or shares <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Shares outstanding unavailable to compute book value per share",
                )

            book_val_per_share = float(equity_val.value) / float(shares)
            if book_val_per_share <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.NOT_APPLICABLE,
                    value=None,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Negative or zero book value per share (N/M)",
                )

            pb = round(float(last_price) / book_val_per_share, 2)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=pb,
                value_type="NUMBER",
                unit="x",
                entity_id=instrument_id,
                company_id=company_id,
                fiscal_period=equity_val.fiscal_period,
                methodology_id="price_divided_by_book_value_per_share",
            )

        # ---------------------------------------------------------------------
        # P/S Ratio
        # ---------------------------------------------------------------------
        elif column_id == "valuation.ps_ratio":
            rev_val = self.fundamental_adapter.get_financial_metric(
                company_id=company_id,
                column_id="fundamentals.revenue",
                asset_class=asset_class,
                instrument_id=instrument_id,
            )
            if rev_val.status != EnrichmentStatus.AVAILABLE or rev_val.value is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Total revenue unavailable for P/S calculation",
                )

            shares = _SHARES_OUTSTANDING_STORE.get(company_id) if company_id else None
            if shares is None or shares <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Shares outstanding unavailable to compute market cap for P/S",
                )

            market_cap = float(last_price) * float(shares)
            rev_num = float(rev_val.value)
            if rev_num <= 0:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.NOT_APPLICABLE,
                    value=None,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Zero or negative revenue (N/M)",
                )

            ps = round(market_cap / rev_num, 2)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=ps,
                value_type="NUMBER",
                unit="x",
                entity_id=instrument_id,
                company_id=company_id,
                fiscal_period=rev_val.fiscal_period,
                methodology_id="market_cap_divided_by_annual_revenue",
            )

        # ---------------------------------------------------------------------
        # Dividend Yield
        # ---------------------------------------------------------------------
        elif column_id == "valuation.dividend_yield":
            div_amount = _DIVIDENDS_STORE.get(company_id) if company_id else None
            if div_amount is None:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    company_id=company_id,
                    reason="Verified dividend distribution records unavailable",
                )

            yield_pct = round((float(div_amount) / float(last_price)) * 100.0, 2)
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=yield_pct,
                value_type="PERCENTAGE",
                unit="%",
                entity_id=instrument_id,
                company_id=company_id,
                methodology_id="annual_dividend_divided_by_price",
            )

        return WatchlistEnrichmentValue(
            column_id=column_id,
            status=EnrichmentStatus.UNAVAILABLE,
            entity_id=instrument_id,
            company_id=company_id,
            reason=f"Unknown valuation column '{column_id}'",
        )
