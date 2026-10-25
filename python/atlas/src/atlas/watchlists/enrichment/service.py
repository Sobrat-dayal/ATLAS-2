"""Watchlist Enrichment Domain Service (Stage 79).

Coordinates batched, qualified financial enrichment across:
1. Canonical Company Fundamentals (Revenue, Net Income, EPS, Assets, Liabilities, Equity)
2. Financial Valuation Ratios (Market Cap, P/E, P/B, P/S, Dividend Yield)
3. Technical Indicator Snapshots (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV)
4. Corporate Events (Earnings Dates, Ex-Dividend Dates, Payment Dates)
5. Earnings Metadata (Reported EPS, Estimated EPS, Surprise %)
6. Canonical News References (Headline, Publication Time, Publisher)

Guarantees:
- Deduplicated planning: Batch resolves issuers once, groups indicators by market series.
- Strict asset applicability: Equities supported; FX, Crypto, Futures marked NOT_APPLICABLE for corporate metrics.
- Exact arithmetic: No NaN or Infinity; non-positive EPS returns NOT_APPLICABLE for P/E.
- Lookahead protection: Indicators evaluated strictly on finalized bars (t <= T).
- Multi-tier caching with TTLs and revision tracking.
"""

from __future__ import annotations

import datetime
import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .caching import default_enrichment_cache
from .events import CorporateEventsAdapter
from .fundamentals import FundamentalDataAdapter
from .models import (
    EnrichmentCategory,
    EnrichmentStatus,
    WatchlistEnrichmentItemResult,
    WatchlistEnrichmentRequest,
    WatchlistEnrichmentResponse,
    WatchlistEnrichmentValue,
)
from .news import NewsReferenceAdapter
from .planner import EnrichmentExecutionPlan, EnrichmentItemContext, EnrichmentPlanner
from .registry import is_enrichment_column
from .technicals import TechnicalIndicatorAdapter
from .valuation import ValuationRatiosAdapter

logger = logging.getLogger(__name__)


class WatchlistEnrichmentService:
    """Core domain service for Watchlist Enrichment (Stage 79)."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self.cache = default_enrichment_cache
        self.planner = EnrichmentPlanner()

        # Source Adapters
        self.fundamentals_adapter = FundamentalDataAdapter(session)
        self.valuation_adapter = ValuationRatiosAdapter(self.fundamentals_adapter)
        self.technicals_adapter = TechnicalIndicatorAdapter()
        self.events_adapter = CorporateEventsAdapter(session)
        self.news_adapter = NewsReferenceAdapter(session)

    async def batch_enrich_items(
        self,
        items: List[EnrichmentItemContext],
        requested_column_ids: List[str],
        quotes_map: Optional[Dict[UUID, Decimal]] = None,
        is_news_entitled: bool = True,
    ) -> Dict[UUID, Dict[str, WatchlistEnrichmentValue]]:
        """Batched enrichment execution for a set of items and selected columns.

        Returns a dictionary mapping item_id -> dict of column_id -> WatchlistEnrichmentValue.
        """
        # Filter for enrichment columns
        enrichment_cols = [cid for cid in requested_column_ids if is_enrichment_column(cid)]
        if not enrichment_cols or not items:
            return {item.item_id: {} for item in items}

        quotes_map = quotes_map or {}

        # 1. Plan execution
        req = WatchlistEnrichmentRequest(selected_column_ids=enrichment_cols)
        plan: EnrichmentExecutionPlan = self.planner.plan(req, items)

        # 2. Batch resolve company issuers if needed
        resolved_issuers: Dict[UUID, Optional[UUID]] = {}
        if plan.company_issuers_needed:
            # Check items that already have company_id provided
            missing_issuer_inst_ids = [
                item.instrument_id for item in items if item.company_id is None
            ]
            if missing_issuer_inst_ids:
                fetched = await self.fundamentals_adapter.resolve_company_issuers(
                    missing_issuer_inst_ids
                )
                resolved_issuers.update(fetched)

            for item in items:
                if item.company_id is not None:
                    resolved_issuers[item.instrument_id] = item.company_id
                elif item.instrument_id in resolved_issuers:
                    item.company_id = resolved_issuers[item.instrument_id]

        # 3. Populate results per item
        results: Dict[UUID, Dict[str, WatchlistEnrichmentValue]] = {}

        for item in items:
            item_values: Dict[str, WatchlistEnrichmentValue] = {}
            company_id = item.company_id or resolved_issuers.get(item.instrument_id)
            last_quote = quotes_map.get(item.instrument_id)

            for col_meta in plan.columns:
                col_id = col_meta.column_id
                category = col_meta.category

                try:
                    if category == EnrichmentCategory.FUNDAMENTALS:
                        val = self.fundamentals_adapter.get_financial_metric(
                            company_id=company_id,
                            column_id=col_id,
                            asset_class=item.asset_class,
                            instrument_id=item.instrument_id,
                        )
                    elif category == EnrichmentCategory.VALUATION:
                        val = self.valuation_adapter.get_valuation_ratio(
                            company_id=company_id,
                            column_id=col_id,
                            asset_class=item.asset_class,
                            instrument_id=item.instrument_id,
                            last_price=last_quote,
                            quote_currency=item.quote_currency,
                        )
                    elif category == EnrichmentCategory.TECHNICAL:
                        series_id = item.market_series_id or f"{item.instrument_id}:1D:CLOSE"
                        val = self.technicals_adapter.compute_snapshot(
                            column_id=col_id,
                            market_series_id=series_id,
                            instrument_id=item.instrument_id,
                        )
                    elif category == EnrichmentCategory.EVENTS:
                        val = self.events_adapter.get_event_metric(
                            company_id=company_id,
                            column_id=col_id,
                            asset_class=item.asset_class,
                            instrument_id=item.instrument_id,
                        )
                    elif category == EnrichmentCategory.EARNINGS:
                        val = self.events_adapter.get_earnings_metric(
                            company_id=company_id,
                            column_id=col_id,
                            asset_class=item.asset_class,
                            instrument_id=item.instrument_id,
                        )
                    elif category == EnrichmentCategory.NEWS:
                        val = self.news_adapter.get_news_metric(
                            column_id=col_id,
                            instrument_id=item.instrument_id,
                            company_id=company_id,
                            is_entitled=is_news_entitled,
                        )
                    else:
                        val = WatchlistEnrichmentValue(
                            column_id=col_id,
                            status=EnrichmentStatus.ERROR,
                            entity_id=item.instrument_id,
                            reason=f"Unsupported category '{category}'",
                        )
                except Exception as ex:
                    logger.exception(
                        "Error enriching column %s for item %s: %s", col_id, item.item_id, ex
                    )
                    val = WatchlistEnrichmentValue(
                        column_id=col_id,
                        status=EnrichmentStatus.ERROR,
                        entity_id=item.instrument_id,
                        reason=str(ex),
                    )

                item_values[col_id] = val

            results[item.item_id] = item_values

        return results

    async def execute_enrichment_query(
        self,
        watchlist_id: UUID,
        membership_revision: int,
        items: List[EnrichmentItemContext],
        request: WatchlistEnrichmentRequest,
        quotes_map: Optional[Dict[UUID, Decimal]] = None,
    ) -> WatchlistEnrichmentResponse:
        """Executes full API query endpoint response for a watchlist."""
        now = datetime.datetime.now(datetime.timezone.utc)
        enriched_map = await self.batch_enrich_items(
            items=items,
            requested_column_ids=request.selected_column_ids,
            quotes_map=quotes_map,
        )

        item_results: List[WatchlistEnrichmentItemResult] = []
        for item in items:
            item_vals = enriched_map.get(item.item_id, {})
            item_results.append(
                WatchlistEnrichmentItemResult(
                    watchlist_item_id=item.item_id,
                    instrument_entity_id=item.instrument_id,
                    market_series_id=item.market_series_id,
                    company_id=item.company_id,
                    values=item_vals,
                )
            )

        return WatchlistEnrichmentResponse(
            watchlist_id=watchlist_id,
            membership_revision=membership_revision,
            column_registry_version=1,
            as_of=now,
            results=item_results,
            partial_errors={},
            source_context={
                "fundamentals": "Stage 34 Canonical Fundamentals",
                "technicals": "Stage 69/70 TA-Lib",
                "events": "Stage 20/34 Corporate Events",
                "news": "Stage 36 Canonical News References",
            },
        )
