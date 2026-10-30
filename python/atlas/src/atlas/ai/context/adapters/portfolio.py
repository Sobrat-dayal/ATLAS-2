"""Portfolio Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)
from atlas.ai.context.errors import AiContextTargetAccessDeniedError
from atlas.context.resolution import CanonicalEntityResolver


class PortfolioContextAdapter(BaseAiContextAdapter):
    """Extracts authorized portfolio allocations, benchmarks, and concentration metrics."""

    @property
    def adapter_id(self) -> str:
        return "adapter_portfolio"

    @property
    def context_type(self) -> ContextType:
        return ContextType.PORTFOLIO_CONTEXT

    @property
    def supported_module(self) -> str:
        return "portfolios"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        entity = CanonicalEntityResolver.resolve_portfolio(target_id)
        params = parameters or {}

        # Permission gate: verify user ownership or tenant authorization
        allowed_users = params.get("allowed_users", ["usr_pm_101"])
        if user_id not in allowed_users:
            raise AiContextTargetAccessDeniedError("PORTFOLIO", entity.entity_id)

        currency = entity.currency or "USD"
        as_of_date = params.get("valuation_as_of", "2025-12-31")
        benchmark = params.get("benchmark_id", "SPX")
        holdings_authorized = params.get("allow_holdings", False)

        allocation = params.get("allocation_summary") or {
            "Equities": 0.65,
            "Fixed Income": 0.25,
            "Cash & Equivalents": 0.10,
        }

        top_concentration = params.get("top_concentration") or [
            {"asset": "Technology Sector", "weight": 0.32},
            {"asset": "Healthcare Sector", "weight": 0.18},
            {"asset": "US Treasuries (5-7Y)", "weight": 0.15},
        ]

        sample_holdings = [
            {"symbol": "MSFT", "weight": 0.085},
            {"symbol": "AAPL", "weight": 0.080},
            {"symbol": "NVDA", "weight": 0.075},
        ]

        payload = {
            "portfolio_id": entity.entity_id,
            "portfolio_name": entity.canonical_name,
            "reporting_currency": currency,
            "valuation_as_of": as_of_date,
            "benchmark_id": benchmark,
            "allocation_summary": allocation,
            "top_concentration": top_concentration,
            "holdings_shared": holdings_authorized,
            "holdings_redacted": not holdings_authorized,
            "holdings": sample_holdings if holdings_authorized else [],
            "total_value": params.get("total_value", 12500000.0),
            "total_value_usd": params.get("total_value", 12500000.0),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_port_{entity.entity_id}",
            context_type=self.context_type,
            canonical_target_id=entity.entity_id,
            source_module="portfolios",
            source_reference=f"atlas://portfolios/{entity.entity_id}",
            as_of=as_of_date,
            observed_at=datetime.now(timezone.utc).isoformat(),
            reporting_currency=currency,
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Portfolio: {entity.canonical_name} (Valued as of {as_of_date})",
            structured_payload=payload,
            estimated_tokens=140,
            relevance_score=3.2,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        alloc_str = ", ".join(
            [f"{k}: {int(v * 100)}%" for k, v in p.get("allocation_summary", {}).items()]
        )
        conc_str = ", ".join(
            [f"{c['asset']} ({int(c['weight'] * 100)}%)" for c in p.get("top_concentration", [])]
        )
        return (
            f"[Authorized Portfolio: {p.get('portfolio_name')} ({p.get('portfolio_id')})]\n"
            f"- Valuation As-of: {p.get('valuation_as_of')} | Reporting Currency: {p.get('reporting_currency')} | Benchmark: {p.get('benchmark_id')}\n"
            f"- Asset Allocation: {alloc_str}\n"
            f"- Major Concentrations: {conc_str}\n"
            f"- Granular Holdings Disclosure: {'Consented' if p.get('holdings_shared') else 'Redacted (Aggregate view only)'}"
        )
