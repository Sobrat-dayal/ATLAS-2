"""Watchlist Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class WatchlistContextAdapter(BaseAiContextAdapter):
    """Extracts watchlist items, selected security, and sorting configurations."""

    @property
    def adapter_id(self) -> str:
        return "adapter_watchlist"

    @property
    def context_type(self) -> ContextType:
        return ContextType.WATCHLIST_CONTEXT

    @property
    def supported_module(self) -> str:
        return "watchlists"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        watchlist_id = target_id or "wl_core_tech"
        name = params.get("name", "Core Tech Leaders")
        instruments = params.get("instruments", ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"])
        selected_inst = params.get("selected_instrument", "AAPL")

        payload = {
            "watchlist_id": watchlist_id,
            "name": name,
            "instrument_count": len(instruments),
            "instruments": instruments[:15],  # Bounded to top 15
            "selected_instrument": selected_inst,
            "sort_order": params.get("sort_order", "MARKET_CAP_DESC"),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_wl_{watchlist_id}",
            context_type=self.context_type,
            canonical_target_id=watchlist_id,
            source_module="watchlists",
            source_reference=f"atlas://watchlists/{watchlist_id}",
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Watchlist: {name} ({len(instruments)} instruments, selected: {selected_inst})",
            structured_payload=payload,
            estimated_tokens=90,
            relevance_score=2.5,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        inst_list = ", ".join(p.get("instruments", []))
        return (
            f"[Watchlist: {p.get('name')}]\n"
            f"- Selected Active Symbol: {p.get('selected_instrument')}\n"
            f"- Total Securities: {p.get('instrument_count')} | Included: {inst_list}"
        )
