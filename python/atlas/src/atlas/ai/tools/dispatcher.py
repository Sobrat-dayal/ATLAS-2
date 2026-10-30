"""Tool Dispatcher for Stage 126: ATLAS AI Tool Gateway.

Orchestrates validation, authorization, timeout enforcement, adapter execution,
and state-machine tracking for AI tool invocations.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import (
    AiToolCall,
    AtlasAiToolResult,
    ToolCallStatus,
    hash_arguments,
)
from atlas.ai.tools.errors import (
    AiToolArgumentInvalidError,
    AiToolCancelledError,
    AiToolError,
    AiToolNotFoundError,
    AiToolSequenceLimitExceededError,
    AiToolTimeoutError,
)
from atlas.ai.tools.gateway import AiToolSecurityGateway
from atlas.ai.tools.registry import AtlasAiToolRegistry

logger = logging.getLogger(__name__)

# Strict limits to prevent unbounded execution loops (Fixture H)
MAX_TOOL_CALLS_PER_GENERATION = 4
DEFAULT_TOOL_TIMEOUT_SECONDS = 10.0


class AiToolDispatcher:
    """Dispatches and tracks tool executions with zero-trust safety checks."""

    _instance: Optional["AiToolDispatcher"] = None

    def __init__(
        self,
        registry: Optional[AtlasAiToolRegistry] = None,
        security_gateway: Optional[AiToolSecurityGateway] = None,
    ) -> None:
        self.registry = registry or AtlasAiToolRegistry.get_instance()
        self.security_gateway = security_gateway or AiToolSecurityGateway.get_instance()
        self._tool_calls: Dict[str, AiToolCall] = {}

    @classmethod
    def get_instance(cls) -> "AiToolDispatcher":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def get_tool_call(self, tool_call_id: str) -> Optional[AiToolCall]:
        """Retrieves a past tool call record by ID."""
        return self._tool_calls.get(tool_call_id)

    def list_tool_calls(self, user_id: str, limit: int = 50) -> List[AiToolCall]:
        """Lists tool calls for a user, sorted newest first."""
        calls = [c for c in self._tool_calls.values() if c.user_id == user_id]
        calls.sort(key=lambda c: c.created_at, reverse=True)
        return calls[:limit]

    async def dispatch(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        user_id: str,
        generation_run_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_permissions: Optional[List[str]] = None,
        disabled_tools: Optional[List[str]] = None,
        approval_request_id: Optional[str] = None,
        active_route: Optional[str] = None,
        provider_id: Optional[str] = None,
        generation_tool_call_count: int = 0,
    ) -> AtlasAiToolResult:
        """Executes the full zero-trust tool execution pipeline."""
        tool_call_id = f"call_{uuid.uuid4().hex[:16]}"
        arg_hash = hash_arguments(arguments)
        start_time = time.perf_counter()

        # Step 0: Check sequence limit / infinite loop defense (Fixture H)
        if generation_tool_call_count >= MAX_TOOL_CALLS_PER_GENERATION:
            logger.warning(
                "Tool call sequence limit (%d) reached for user %s",
                MAX_TOOL_CALLS_PER_GENERATION,
                user_id,
            )
            raise AiToolSequenceLimitExceededError(MAX_TOOL_CALLS_PER_GENERATION)

        call_record = AiToolCall(
            id=tool_call_id,
            user_id=user_id,
            tool_id=tool_id,
            arguments=arguments,
            normalized_arguments_hash=arg_hash,
            generation_run_id=generation_run_id,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            status=ToolCallStatus.PROPOSED,
        )
        self._tool_calls[tool_call_id] = call_record

        try:
            # Step 1: Look up tool in registry (Fixture G: unknown tool rejected)
            call_record.status = ToolCallStatus.VALIDATING
            if not self.registry.is_registered(tool_id):
                call_record.status = ToolCallStatus.REJECTED
                call_record.error_code = "AI_TOOL_NOT_FOUND"
                call_record.error_message = f"AI tool '{tool_id}' is not registered."
                raise AiToolNotFoundError(tool_id)

            tool_def = self.registry.get_tool(tool_id)
            call_record.tool_version = tool_def.version
            call_record.approval_class = tool_def.approval_class

            # Step 2: Validate arguments
            # Note: arguments must be a dict
            if not isinstance(arguments, dict):
                raise AiToolArgumentInvalidError(
                    tool_id, "Arguments must be a valid JSON dictionary."
                )

            # Step 3: Authorization & Security Gateway Checks (Anti-IDOR, Scopes, Provider Disclosure, Approval)
            call_record.status = ToolCallStatus.AUTHORIZING
            self.security_gateway.authorize_tool_invocation(
                tool=tool_def,
                user_id=user_id,
                arguments=arguments,
                user_permissions=user_permissions,
                disabled_tools=disabled_tools,
                approval_request_id=approval_request_id,
                provider_id=provider_id,
                tenant_id=tenant_id,
            )

            # Step 4: Resolve adapter
            adapter_cls = self.registry.get_adapter_class(tool_id)
            if not adapter_cls:
                raise AiToolError(
                    f"No execution adapter registered for tool '{tool_id}'.",
                    code="AI_TOOL_ADAPTER_MISSING",
                )

            adapter: BaseAiToolAdapter = adapter_cls()

            # Step 5: Execute with timeout
            call_record.status = ToolCallStatus.RUNNING
            context = ToolExecutionContext(
                user_id=user_id,
                tool_call_id=tool_call_id,
                tenant_id=tenant_id,
                generation_run_id=generation_run_id,
                conversation_id=conversation_id,
                permissions=user_permissions or [],
                active_route=active_route,
                provider_id=provider_id,
            )

            timeout_sec = min(tool_def.timeout_seconds, DEFAULT_TOOL_TIMEOUT_SECONDS)
            try:
                result = await asyncio.wait_for(
                    adapter.execute(arguments, context), timeout=timeout_sec
                )
            except asyncio.TimeoutError:
                call_record.status = ToolCallStatus.TIMED_OUT
                raise AiToolTimeoutError(tool_id, timeout_sec)
            except asyncio.CancelledError:
                call_record.status = ToolCallStatus.CANCELLED
                raise AiToolCancelledError(tool_id)

            # Step 6: Mark completed
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            call_record.status = ToolCallStatus.COMPLETED
            call_record.result = result
            call_record.execution_time_ms = elapsed_ms
            call_record.updated_at = datetime.now(timezone.utc)
            return result

        except AiToolError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if call_record.status not in (
                ToolCallStatus.REJECTED,
                ToolCallStatus.TIMED_OUT,
                ToolCallStatus.CANCELLED,
            ):
                call_record.status = ToolCallStatus.FAILED
            call_record.error_code = e.code
            call_record.error_message = e.message
            call_record.execution_time_ms = elapsed_ms
            call_record.updated_at = datetime.now(timezone.utc)
            raise

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            call_record.status = ToolCallStatus.FAILED
            call_record.error_code = "AI_TOOL_EXECUTION_FAILED"
            call_record.error_message = str(e)
            call_record.execution_time_ms = elapsed_ms
            call_record.updated_at = datetime.now(timezone.utc)
            logger.exception("Unexpected error executing AI tool %s: %s", tool_id, e)
            raise AiToolError(
                f"Unexpected error executing tool '{tool_id}': {e}", code="AI_TOOL_EXECUTION_FAILED"
            ) from e
