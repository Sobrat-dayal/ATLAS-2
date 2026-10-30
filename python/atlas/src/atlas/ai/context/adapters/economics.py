"""Economics Indicator Context Adapter for Stage 125."""

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


class EconomicsContextAdapter(BaseAiContextAdapter):
    """Extracts macroeconomic indicator series, frequency, units, and vintage point-in-time data."""

    @property
    def adapter_id(self) -> str:
        return "adapter_economics"

    @property
    def context_type(self) -> ContextType:
        return ContextType.ECONOMICS_CONTEXT

    @property
    def supported_module(self) -> str:
        return "economics"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        entity = CanonicalEntityResolver.resolve_economic_series(target_id)
        params = parameters or {}
        vintage_date = params.get("vintage_date", "2026-01-15")
        latest_value = params.get("latest_value", 3.1)
        units = params.get("units", "PERCENT_YOY")

        payload = {
            "series_id": entity.entity_id,
            "canonical_name": entity.canonical_name,
            "country": entity.country or "USA",
            "units": units,
            "frequency": params.get("frequency", "MONTHLY"),
            "seasonal_adjustment": params.get("seasonal_adjustment", "SEASONALLY_ADJUSTED"),
            "latest_value": latest_value,
            "observation_date": params.get("observation_date", "2025-12-01"),
            "vintage_date": vintage_date,
            "source_agency": params.get("source_agency", "Bureau of Labor Statistics"),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_econ_{entity.entity_id}",
            context_type=self.context_type,
            canonical_target_id=entity.entity_id,
            source_module="economics",
            source_reference=f"atlas://economics/series/{entity.entity_id}?vintage={vintage_date}",
            as_of=payload["observation_date"],
            observed_at=datetime.now(timezone.utc).isoformat(),
            units=units,
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Economics Series: {entity.canonical_name} ({latest_value}%, as of {payload['observation_date']})",
            structured_payload=payload,
            estimated_tokens=85,
            relevance_score=2.6,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        return (
            f"[Macroeconomic Indicator: {p.get('canonical_name')} ({p.get('series_id')})]\n"
            f"- Country/Region: {p.get('country')} | Frequency: {p.get('frequency')} | Adjustment: {p.get('seasonal_adjustment')}\n"
            f"- Observation: {p.get('observation_date')} | Latest Value: {p.get('latest_value')}% ({p.get('units')})\n"
            f"- Publication Vintage: {p.get('vintage_date')} | Source: {p.get('source_agency')}"
        )
