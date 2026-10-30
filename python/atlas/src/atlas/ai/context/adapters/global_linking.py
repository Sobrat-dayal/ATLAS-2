"""Stage 121 Global Linking Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class GlobalLinkingContextAdapter(BaseAiContextAdapter):
    """Integrates with Stage 121 Global Workspace Linking to extract synchronized link channel context."""

    @property
    def adapter_id(self) -> str:
        return "adapter_global_linking"

    @property
    def context_type(self) -> ContextType:
        return ContextType.LINKED_CONTEXT

    @property
    def supported_module(self) -> str:
        return "global_linking"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        channel_id = target_id or "channel_blue"
        name = params.get("channel_name", "Channel Blue")
        color = params.get("display_color_token", "blue")
        revision = params.get("revision", 1)

        # Stage 121 synchronized context snapshot
        snapshot = params.get("context_snapshot") or {
            "instrument": "inst_msft_us",
            "company": "comp_microsoft_us",
            "timeframe": "1D",
            "reporting_currency": "USD",
        }

        payload = {
            "channel_id": channel_id,
            "channel_name": name,
            "color_token": color,
            "revision": revision,
            "snapshot": snapshot,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_link_{channel_id}",
            context_type=self.context_type,
            canonical_target_id=channel_id,
            source_module="global_linking",
            source_reference=f"atlas://linking/channels/{channel_id}",
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Linked Context ({name}, Rev {revision}): {snapshot.get('instrument')} / {snapshot.get('timeframe')}",
            structured_payload=payload,
            estimated_tokens=80,
            relevance_score=2.9,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        snap = p.get("snapshot", {})
        snap_str = ", ".join([f"{k}={v}" for k, v in snap.items()])
        return (
            f"[Stage 121 Synchronized Link Channel: {p.get('channel_name')} (Rev {p.get('revision')})]\n"
            f"- Linked Active Entities: {snap_str}"
        )
