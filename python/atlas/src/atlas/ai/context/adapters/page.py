"""Page & Route Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)

CANONICAL_MODULE_NAMES: Dict[str, str] = {
    "/home": "Executive Overview",
    "/markets": "Markets Monitor",
    "/charts": "Interactive Charts",
    "/watchlists": "Watchlists",
    "/screeners": "Screeners",
    "/companies": "Companies",
    "/economics": "Economics",
    "/news": "News Intelligence",
    "/research": "Research Library",
    "/maps": "Geopolitical & Supply Maps",
    "/intelligence": "Intelligence Signals",
    "/options": "Options Analytics",
    "/trading": "Trading Blotter",
    "/portfolios": "Portfolios",
    "/risk": "Risk Engine",
    "/ai": "AI Workspace",
    "/data": "Data Platform",
    "/saved": "Saved Library",
    "/workspaces": "Workspaces",
    "/agents": "Autonomous Agents",
}


class PageContextAdapter(BaseAiContextAdapter):
    """Extracts verified page and route context."""

    @property
    def adapter_id(self) -> str:
        return "adapter_page"

    @property
    def context_type(self) -> ContextType:
        return ContextType.PAGE_CONTEXT

    @property
    def supported_module(self) -> str:
        return "global_page"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        route = target_id.strip() if target_id else "/home"
        module_name = CANONICAL_MODULE_NAMES.get(route, "ATLAS Operating System")
        view_mode = (parameters or {}).get("view_mode", "standard")

        payload = {
            "route": route,
            "module_name": module_name,
            "view_mode": view_mode,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_page_{abs(hash(route)) % 1000000}",
            context_type=self.context_type,
            canonical_target_id=route,
            source_module="shell",
            source_reference=f"atlas://routes{route}",
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Current Page: {module_name} ({route})",
            structured_payload=payload,
            estimated_tokens=40,
            relevance_score=1.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        route = item.structured_payload.get("route", "")
        module = item.structured_payload.get("module_name", "")
        return f"[Platform Navigation] Route: {route} | Module: {module}"
