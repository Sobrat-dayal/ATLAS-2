"""Universal Saved Resource Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class SavedResourceContextAdapter(BaseAiContextAdapter):
    """Integrates with Stage 119 Universal Saved Library to resolve persisted targets."""

    @property
    def adapter_id(self) -> str:
        return "adapter_saved"

    @property
    def context_type(self) -> ContextType:
        return ContextType.SAVED_RESOURCE_CONTEXT

    @property
    def supported_module(self) -> str:
        return "saved"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        saved_id = target_id or "saved_workspace_quant_desk"
        target_type = params.get("target_type", "WORKSPACE")
        target_resource_id = params.get("target_id", "ws_quant_equities")
        name = params.get("name", "Active Quant Trading Workspace")

        payload = {
            "saved_id": saved_id,
            "target_type": target_type,
            "target_id": target_resource_id,
            "name": name,
            "version": params.get("version", 1),
            "is_favorite": params.get("is_favorite", True),
            "permission_status": "AUTHORIZED",
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_saved_{saved_id}",
            context_type=self.context_type,
            canonical_target_id=saved_id,
            source_module="saved",
            source_reference=f"atlas://saved/{saved_id}",
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Saved Resource: '{name}' ({target_type} -> {target_resource_id})",
            structured_payload=payload,
            estimated_tokens=60,
            relevance_score=2.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        return (
            f"[Universal Saved Resource: '{p.get('name')}']\n"
            f"- Saved Target: {p.get('target_type')} ({p.get('target_id')}) | Version: {p.get('version')}"
        )
