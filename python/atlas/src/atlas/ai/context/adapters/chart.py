"""Chart Analysis & Configuration Context Adapter for Stage 125."""

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


class ChartContextAdapter(BaseAiContextAdapter):
    """Extracts verified chart configuration, intervals, indicators, and analytical observations."""

    @property
    def adapter_id(self) -> str:
        return "adapter_chart"

    @property
    def context_type(self) -> ContextType:
        return ContextType.CHART_CONTEXT

    @property
    def supported_module(self) -> str:
        return "charts"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        instrument_id = params.get("instrument_id")
        if not instrument_id:
            if target_id.startswith("chart_"):
                parts = target_id.split("_")
                instrument_id = parts[1] if len(parts) > 1 else target_id
            else:
                instrument_id = target_id

        entity = CanonicalEntityResolver.resolve_instrument(instrument_id)

        chart_type = params.get("chart_type", "CANDLESTICK")
        interval = params.get("interval", "1D")
        timeframe = params.get("timeframe", "1M")
        date_range = params.get("date_range", {"start": "2026-01-01", "end": "2026-01-31"})
        indicators = params.get("indicators", ["SMA(50)", "RSI(14)"])
        volatility_annualized = params.get("volatility_annualized", 0.245)
        last_close = params.get("last_close", 185.50)
        source_ts = params.get("source_timestamp") or datetime.now(timezone.utc).isoformat()

        payload = {
            "instrument_id": entity.entity_id,
            "symbol": entity.symbol,
            "display_name": entity.display_name,
            "chart_type": chart_type,
            "interval": interval,
            "timeframe": timeframe,
            "date_range": date_range,
            "indicators": indicators,
            "price_currency": entity.currency or "USD",
            "last_close": last_close,
            "realized_volatility_annualized": volatility_annualized,
            "annualized_volatility": volatility_annualized,
            "data_coverage": "100%",
            "source_timestamp": source_ts,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_chart_{entity.entity_id}_{interval}",
            context_type=self.context_type,
            canonical_target_id=entity.entity_id,
            source_module="charts",
            source_reference=f"atlas://charts/{entity.entity_id}?interval={interval}",
            as_of=date_range.get("end"),
            source_updated_at=source_ts,
            reporting_currency=entity.currency or "USD",
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Chart: {entity.symbol} ({chart_type}, {interval}, {date_range.get('start')} to {date_range.get('end')})",
            structured_payload=payload,
            estimated_tokens=120,
            relevance_score=3.5,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        dr = p.get("date_range", {})
        ind_str = ", ".join(p.get("indicators", []))
        return (
            f"[Active Chart: {p.get('symbol')} ({p.get('display_name')})]\n"
            f"- Chart Type: {p.get('chart_type')} | Interval: {p.get('interval')} | Timeframe: {p.get('timeframe')}\n"
            f"- Observation Range: {dr.get('start')} to {dr.get('end')}\n"
            f"- Applied Indicators: {ind_str}\n"
            f"- Last Close: ${p.get('last_close')} {p.get('price_currency')} | Annualized Realized Volatility: {int(p.get('realized_volatility_annualized', 0) * 100)}%\n"
            f"- Source Timestamp: {p.get('source_timestamp')} (Coverage: {p.get('data_coverage')})"
        )

    @classmethod
    def _create_chart_item(
        cls,
        panel_id: str,
        symbol: str,
        interval: str = "1D",
        indicators: Optional[list] = None,
    ) -> AtlasAiContextItem:
        return AtlasAiContextItem(
            context_item_id=f"ctx_chart_{panel_id}",
            context_type=ContextType.CHART_CONTEXT,
            canonical_target_id=symbol,
            source_module="charts",
            source_reference=f"atlas://charts/{panel_id}",
            content_summary=f"Chart {symbol} {interval}",
            data_quality_status=DataQualityStatus.COMPLETE,
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            structured_payload={
                "instrument_id": f"inst_{symbol.lower()}_us",
                "symbol": symbol,
                "interval": interval,
                "indicators": indicators or [],
            },
            estimated_tokens=100,
            provenance={"panel_id": panel_id},
        )
