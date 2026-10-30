"""Multi-Panel Workspace Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class WorkspaceContextAdapter(BaseAiContextAdapter):
    """Integrates with Stage 120 Multi-Panel Workspaces to extract layout and focused panel inventory."""

    @property
    def adapter_id(self) -> str:
        return "adapter_workspace"

    @property
    def context_type(self) -> ContextType:
        return ContextType.WORKSPACE_CONTEXT

    @property
    def supported_module(self) -> str:
        return "workspaces"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        workspace_id = target_id or "ws_institutional_quant"
        name = params.get("name", "Institutional Equities Desk")
        active_panel_id = params.get("active_panel_id", "panel_chart_a")

        # Bounded panel summary from Stage 120 layout
        panels = params.get("panels") or [
            {
                "panel_id": "panel_chart_a",
                "panel_type": "CHART",
                "title": "Chart A: MSFT",
                "instrument": "MSFT",
                "timeframe": "1D",
            },
            {
                "panel_id": "panel_chart_b",
                "panel_type": "CHART",
                "title": "Chart B: NVDA",
                "instrument": "NVDA",
                "timeframe": "1D",
            },
            {
                "panel_id": "panel_fin_msft",
                "panel_type": "COMPANY_FINANCIALS",
                "title": "Financial Statements: MSFT",
                "company": "MSFT",
            },
            {
                "panel_id": "panel_news_tech",
                "panel_type": "NEWS",
                "title": "Tech Newswire",
                "sector": "Technology",
            },
        ]

        payload = {
            "workspace_id": workspace_id,
            "name": name,
            "panel_count": len(panels),
            "active_panel_id": active_panel_id,
            "panels": panels,
            "link_groups_active": params.get("link_groups_count", 1),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_ws_{workspace_id}",
            context_type=self.context_type,
            canonical_target_id=workspace_id,
            source_module="workspaces",
            source_reference=f"atlas://workspaces/{workspace_id}",
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Workspace: {name} ({len(panels)} panels, focused: {active_panel_id})",
            structured_payload=payload,
            estimated_tokens=140,
            relevance_score=3.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        panel_lines = [
            f"  - [{pnl['panel_id']}] {pnl['title']} ({pnl['panel_type']}) {'[ACTIVE FOCUS]' if pnl['panel_id'] == p.get('active_panel_id') else ''}"
            for pnl in p.get("panels", [])
        ]
        return (
            f"[Active Multi-Panel Workspace: {p.get('name')} ({p.get('workspace_id')})]\n"
            f"- Total Panels: {p.get('panel_count')} | Focused Active Panel: {p.get('active_panel_id')}\n"
            f"- Panel Inventory:\n" + "\n".join(panel_lines)
        )
