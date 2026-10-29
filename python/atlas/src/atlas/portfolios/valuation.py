"""ATLAS Portfolios V1 — Valuation Engine.

Computes mark-to-market position valuations, multi-currency FX conversions,
and comprehensive portfolio valuation snapshots with strict completeness auditing.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from atlas.portfolios.enums import (
    QuoteFreshness,
    ValuationCompletenessStatus,
)
from atlas.portfolios.models import (
    Portfolio,
    PortfolioCashBalance,
    PortfolioCashValuation,
    PortfolioPosition,
    PortfolioPositionValuation,
    PortfolioValuation,
)


class PortfolioValuationEngine:
    """Pure valuation calculator implementing multi-currency and freshness-aware portfolio marks."""

    @classmethod
    def calculate_valuation(
        cls,
        portfolio: Portfolio,
        positions: list[PortfolioPosition],
        cash_balances: list[PortfolioCashBalance],
        market_quotes: dict[str, dict[str, Any]],
        fx_rates: dict[tuple[str, str], dict[str, Any]],
        as_of: Optional[datetime] = None,
    ) -> PortfolioValuation:
        """Compute the marked portfolio valuation snapshot with completeness validation."""
        val_time = as_of or datetime.utcnow()
        base_cur = portfolio.base_currency

        position_valuations: list[PortfolioPositionValuation] = []
        cash_valuations: list[PortfolioCashValuation] = []

        missing_prices = 0
        missing_fx = 0
        stale_quotes = 0

        # 1. Position Valuations
        total_positions_market_val = Decimal("0")
        total_cost_basis = Decimal("0")
        total_unrealized_pnl = Decimal("0")
        has_incomplete_position = False

        for pos in positions:
            if pos.quantity <= Decimal("0"):
                continue

            total_cost_basis += pos.remaining_cost_basis
            quote_data = market_quotes.get(pos.instrument_id)

            if not quote_data or quote_data.get("price") is None:
                missing_prices += 1
                has_incomplete_position = True
                pv = PortfolioPositionValuation(
                    account_id=pos.account_id,
                    instrument_id=pos.instrument_id,
                    symbol=pos.symbol,
                    exchange=pos.exchange,
                    company_name=pos.company_name,
                    quantity=pos.quantity,
                    remaining_basis=pos.remaining_cost_basis,
                    basis_currency=pos.cost_basis_currency,
                    valuation_status=ValuationCompletenessStatus.PARTIAL_MISSING_PRICES,
                    quote_freshness=QuoteFreshness.UNAVAILABLE,
                )
                position_valuations.append(pv)
                continue

            price = Decimal(str(quote_data["price"]))
            price_cur = quote_data.get("currency", pos.cost_basis_currency)
            quote_time = quote_data.get("as_of", val_time)
            quote_source = quote_data.get("source", "MARKET_FEED")
            freshness = quote_data.get("freshness", QuoteFreshness.REALTIME)
            if isinstance(freshness, str):
                freshness = QuoteFreshness(freshness)

            if freshness == QuoteFreshness.STALE:
                stale_quotes += 1

            native_mkt_val = pos.quantity * price

            # FX conversion
            fx_rate = Decimal("1.0")
            fx_pair = None
            fx_as_of = None
            pos_val_status = ValuationCompletenessStatus.COMPLETE

            if price_cur != base_cur:
                fx_key = (price_cur, base_cur)
                fx_data = fx_rates.get(fx_key)
                if not fx_data or fx_data.get("rate") is None:
                    missing_fx += 1
                    has_incomplete_position = True
                    pos_val_status = ValuationCompletenessStatus.PARTIAL_MISSING_FX
                    base_mkt_val = None
                    unrealized_pnl = None
                else:
                    fx_rate = Decimal(str(fx_data["rate"]))
                    fx_pair = f"{price_cur}/{base_cur}"
                    fx_as_of = fx_data.get("as_of", val_time)
                    base_mkt_val = native_mkt_val * fx_rate
                    # Unrealized P&L in base currency
                    basis_in_base = pos.remaining_cost_basis * fx_rate
                    unrealized_pnl = base_mkt_val - basis_in_base
                    total_positions_market_val += base_mkt_val
                    total_unrealized_pnl += unrealized_pnl
            else:
                base_mkt_val = native_mkt_val
                unrealized_pnl = native_mkt_val - pos.remaining_cost_basis
                total_positions_market_val += base_mkt_val
                total_unrealized_pnl += unrealized_pnl

            pv = PortfolioPositionValuation(
                account_id=pos.account_id,
                instrument_id=pos.instrument_id,
                symbol=pos.symbol,
                exchange=pos.exchange,
                company_name=pos.company_name,
                quantity=pos.quantity,
                remaining_basis=pos.remaining_cost_basis,
                basis_currency=pos.cost_basis_currency,
                mark_price=price,
                price_currency=price_cur,
                mark_as_of=quote_time,
                mark_source=quote_source,
                quote_freshness=freshness,
                native_market_value=native_mkt_val,
                fx_rate_to_base=fx_rate if price_cur != base_cur else None,
                fx_pair=fx_pair,
                fx_as_of=fx_as_of,
                base_market_value=base_mkt_val,
                unrealized_pnl=unrealized_pnl,
                valuation_status=pos_val_status,
            )
            position_valuations.append(pv)

        # 2. Cash Valuations
        total_cash_market_val = Decimal("0")
        has_incomplete_cash = False

        for cb in cash_balances:
            cur = cb.currency
            fx_rate = Decimal("1.0")
            if cur != base_cur:
                fx_key = (cur, base_cur)
                fx_data = fx_rates.get(fx_key)
                if not fx_data or fx_data.get("rate") is None:
                    missing_fx += 1
                    has_incomplete_cash = True
                    base_cash = Decimal("0")
                else:
                    fx_rate = Decimal(str(fx_data["rate"]))
                    base_cash = cb.settled_cash * fx_rate
            else:
                base_cash = cb.settled_cash

            total_cash_market_val += base_cash
            cv = PortfolioCashValuation(
                account_id=cb.account_id,
                currency=cur,
                posted_cash=cb.posted_cash,
                settled_cash=cb.settled_cash,
                unsettled_receivable=cb.unsettled_receivable,
                unsettled_payable=cb.unsettled_payable,
                available_cash=cb.available_cash,
                fx_rate_to_base=fx_rate,
                base_cash_value=base_cash,
                as_of=val_time,
            )
            cash_valuations.append(cv)

        # 3. Overall Portfolio Completeness
        known_subtotal = total_cash_market_val + total_positions_market_val

        overall_status = ValuationCompletenessStatus.COMPLETE
        verified_total: Optional[Decimal] = known_subtotal

        if missing_prices > 0:
            overall_status = ValuationCompletenessStatus.PARTIAL_MISSING_PRICES
            verified_total = None
        elif missing_fx > 0 or has_incomplete_cash:
            overall_status = ValuationCompletenessStatus.PARTIAL_MISSING_FX
            verified_total = None
        elif stale_quotes > 0:
            overall_status = ValuationCompletenessStatus.PARTIAL_STALE_DATA

        # Sum realized P&L across all positions
        total_realized_pnl = sum((p.realized_pnl for p in positions), Decimal("0"))

        return PortfolioValuation(
            id=f"val_{uuid.uuid4().hex[:12]}",
            portfolio_id=portfolio.id,
            as_of=val_time,
            base_currency=base_cur,
            valuation_status=overall_status,
            known_valued_subtotal=known_subtotal,
            verified_total_portfolio_value=verified_total,
            total_positions_market_value=total_positions_market_val if not has_incomplete_position else None,
            total_cash_market_value=total_cash_market_val,
            total_cost_basis=total_cost_basis,
            total_unrealized_pnl=total_unrealized_pnl if not has_incomplete_position else None,
            total_realized_pnl=total_realized_pnl,
            missing_prices_count=missing_prices,
            missing_fx_count=missing_fx,
            stale_quotes_count=stale_quotes,
            position_valuations=position_valuations,
            cash_valuations=cash_valuations,
            source_manifest={
                "positions_count": len(positions),
                "cash_balances_count": len(cash_balances),
                "quotes_resolved": len(market_quotes),
                "fx_rates_resolved": len(fx_rates),
                "valuation_timestamp": val_time.isoformat(),
            },
            calculation_version="1.0.0",
        )

