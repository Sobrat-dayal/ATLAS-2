"""Canonical Financial Instrument Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)
from atlas.context.resolution import CanonicalEntityResolver


class InstrumentContextAdapter(BaseAiContextAdapter):
    """Extracts canonical financial instrument identity and reference metadata."""

    @property
    def adapter_id(self) -> str:
        return "adapter_instrument"

    @property
    def context_type(self) -> ContextType:
        return ContextType.INSTRUMENT_CONTEXT

    @property
    def supported_module(self) -> str:
        return "markets"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        entity = CanonicalEntityResolver.resolve_instrument(target_id)
        now_str = datetime.now(timezone.utc).isoformat()

        payload = {
            "entity_id": entity.entity_id,
            "symbol": entity.symbol,
            "canonical_name": entity.canonical_name,
            "display_name": entity.display_name,
            "exchange": entity.exchange,
            "currency": entity.currency,
            "country": entity.country,
            "sector": entity.metadata.get("sector", "N/A"),
            "figi": entity.metadata.get("figi", "N/A"),
            "isin": entity.metadata.get("isin", "N/A"),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_inst_{entity.entity_id}",
            context_type=self.context_type,
            canonical_target_id=entity.symbol or entity.entity_id,
            source_module="markets",
            source_reference=f"atlas://instruments/{entity.entity_id}",
            observed_at=now_str,
            source_updated_at=now_str,
            reporting_currency=entity.currency,
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Instrument: {entity.symbol} ({entity.display_name}) [{entity.exchange}]",
            structured_payload=payload,
            estimated_tokens=85,
            relevance_score=3.5,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        return (
            f"[Financial Instrument: {p.get('symbol')} ({p.get('canonical_name')})]\n"
            f"- Entity ID: {p.get('entity_id')}\n"
            f"- Exchange: {p.get('exchange')} | Currency: {p.get('currency')} | Country: {p.get('country')}\n"
            f"- Sector: {p.get('sector')} | FIGI: {p.get('figi')} | ISIN: {p.get('isin')}"
        )
