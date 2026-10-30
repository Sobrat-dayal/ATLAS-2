"""Chart Tool Adapters for ATLAS AI Tool Gateway (Stage 128)."""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.actions.registry import get_action_registry
from atlas.ai.actions.service import get_action_service
from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError


class ChartConfigureToolAdapter(BaseAiToolAdapter):
    """Configures chart timeframe, type, indicators, or comparisons."""

    async def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        chart_id = arguments.get("chart_id")
        if not chart_id:
            raise AiToolArgumentInvalidError("chart_id", "Missing required argument 'chart_id'")

        action_service = get_action_service()
        # Create action plan directly
        plan = await action_service.create_plan(
            intent=f"Configure chart {chart_id}",
            actor_user_id=context.user_id,
            tenant_id=context.tenant_id,
            context_hints={"chart_id": chart_id, **arguments},
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return AtlasAiToolResult(
            tool_call_id=context.tool_call_id,
            tool_id=self.tool_id,
            success=True,
            data=plan.to_dict(),
            duration_ms=duration_ms,
        )

