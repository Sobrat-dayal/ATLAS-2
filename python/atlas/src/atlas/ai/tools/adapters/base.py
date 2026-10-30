"""Base Adapter Interface for Stage 126: ATLAS AI Tool Gateway.

Defines the execution contract, context envelope, and helper methods for all
financial domain tool adapters.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.ai.tools.domain import (
    AiToolSourceManifest,
    AtlasAiToolResult,
    ProviderDisclosurePolicy,
)
from atlas.ai.tools.errors import AiToolResultTooLargeError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolExecutionContext:
    """Security and runtime context supplied to every tool adapter invocation."""

    user_id: str
    tool_call_id: str
    tenant_id: Optional[str] = None
    generation_run_id: Optional[str] = None
    conversation_id: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    active_route: Optional[str] = None
    provider_id: Optional[str] = None


class BaseAiToolAdapter(ABC):
    """Abstract base class for all typed financial tool adapters."""

    tool_id: str = ""
    max_result_size_bytes: int = 100_000

    @abstractmethod
    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        """Executes the tool operation against underlying ATLAS services and returns a typed envelope."""
        raise NotImplementedError

    def build_result(
        self,
        context: ToolExecutionContext,
        data: Any,
        data_source: str,
        attribution: str = "ATLAS Financial Engine",
        as_of: Optional[str] = None,
        provider_disclosure: ProviderDisclosurePolicy = ProviderDisclosurePolicy.ALLOWED,
        record_count: int = 1,
        execution_time_ms: float = 0.0,
    ) -> AtlasAiToolResult:
        """Constructs a fully populated, source-manifested tool result envelope."""
        as_of_str = as_of or datetime.now(timezone.utc).isoformat()

        # Check payload size
        serialized = json.dumps(data, sort_keys=True, default=str)
        payload_size = len(serialized.encode("utf-8"))
        truncated = False

        if payload_size > self.max_result_size_bytes:
            if isinstance(data, list) and len(data) > 1:
                # Truncate list
                data = data[: max(1, len(data) // 2)]
                truncated = True
            else:
                raise AiToolResultTooLargeError(
                    self.tool_id, payload_size, self.max_result_size_bytes
                )

        manifest = AiToolSourceManifest(
            tool_id=self.tool_id,
            data_source=data_source,
            as_of=as_of_str,
            attribution=attribution,
            provider_disclosure_status=provider_disclosure,
            record_count=record_count,
        )

        result = AtlasAiToolResult(
            tool_call_id=context.tool_call_id,
            tool_id=self.tool_id,
            success=True,
            data=data,
            source_manifest=manifest,
            execution_time_ms=execution_time_ms,
            as_of=as_of_str,
            truncated=truncated,
        )
        return AtlasAiToolResult(
            tool_call_id=result.tool_call_id,
            tool_id=result.tool_id,
            success=result.success,
            data=result.data,
            source_manifest=result.source_manifest,
            execution_time_ms=result.execution_time_ms,
            as_of=result.as_of,
            truncated=result.truncated,
            content_hash=result.calculate_hash(),
        )

    def build_error_result(
        self,
        context: ToolExecutionContext,
        error_code: str,
        error_message: str,
        execution_time_ms: float = 0.0,
    ) -> AtlasAiToolResult:
        """Constructs an explicit error result envelope without fabricating data."""
        return AtlasAiToolResult(
            tool_call_id=context.tool_call_id,
            tool_id=self.tool_id,
            success=False,
            data=None,
            source_manifest=None,
            execution_time_ms=execution_time_ms,
            error_code=error_code,
            error_message=error_message,
        )
