"""Screener Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class ScreenerContextAdapter(BaseAiContextAdapter):
    """Extracts verified screener filters, universe rules, and bounded result summaries."""

    @property
    def adapter_id(self) -> str:
        return "adapter_screener"

    @property
    def context_type(self) -> ContextType:
        return ContextType.SCREENER_CONTEXT

    @property
    def supported_module(self) -> str:
        return "screeners"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        screener_id = target_id or "scr_high_yield_tech"
        name = params.get("name", "High Yield Quality Tech")
        universe = params.get("universe", "US_EQUITIES_LARGE_CAP")
        filters = params.get("filters") or [
            {"field": "pe_ratio", "operator": "LESS_THAN", "value": 25.0},
            {"field": "dividend_yield", "operator": "GREATER_THAN", "value": 0.02},
            {"field": "roe", "operator": "GREATER_THAN", "value": 0.15},
        ]
        result_count = params.get("result_count", 18)
        # Bounded subset: only top 3-5 results passed, never full universe dump
        sample_results = params.get("sample_results") or [
            {"symbol": "MSFT", "pe_ratio": 24.2, "dividend_yield": 0.022, "roe": 0.32},
            {"symbol": "AAPL", "pe_ratio": 22.8, "dividend_yield": 0.021, "roe": 0.28},
            {"symbol": "CSCO", "pe_ratio": 16.5, "dividend_yield": 0.034, "roe": 0.22},
        ]

        payload = {
            "screener_id": screener_id,
            "name": name,
            "universe": universe,
            "filters": filters,
            "result_count": result_count,
            "sample_results": sample_results,
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_scr_{screener_id}",
            context_type=self.context_type,
            canonical_target_id=screener_id,
            source_module="screeners",
            source_reference=f"atlas://screeners/{screener_id}",
            observed_at=payload["execution_timestamp"],
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Screener: {name} ({result_count} matches in {universe})",
            structured_payload=payload,
            estimated_tokens=150,
            relevance_score=2.8,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        filter_lines = [
            f"  - {f['field']} {f['operator']} {f['value']}" for f in p.get("filters", [])
        ]
        results_preview = ", ".join([r["symbol"] for r in p.get("sample_results", [])])
        return (
            f"[Screener Configuration: {p.get('name')}]\n"
            f"- Universe: {p.get('universe')} | Total Matches: {p.get('result_count')}\n"
            f"- Filter Conditions:\n" + "\n".join(filter_lines) + "\n"
            f"- Top Permitted Matching Candidates: {results_preview} (bounded sample)"
        )
