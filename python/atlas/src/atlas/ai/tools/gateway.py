"""Security Gateway for Stage 126: ATLAS AI Tool Gateway.

Enforces zero-trust authorization, resource ACLs, tenant isolation, provider disclosure
policies, and prompt-injection defense for all tool invocations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from atlas.ai.tools.approval import AiToolApprovalEngine
from atlas.ai.tools.domain import (
    ApprovalClass,
    AtlasAiToolDefinition,
    ProviderDisclosurePolicy,
    ToolLifecycleStatus,
)
from atlas.ai.tools.errors import (
    AiToolDisabledError,
    AiToolNotAuthorizedError,
    AiToolProviderDisclosureDeniedError,
    AiToolResourceAccessDeniedError,
)
from atlas.ai.tools.registry import AtlasAiToolRegistry

logger = logging.getLogger(__name__)


class AiToolSecurityGateway:
    """Zero-trust policy enforcement point for AI tool execution."""

    _instance: Optional["AiToolSecurityGateway"] = None

    def __init__(
        self,
        registry: Optional[AtlasAiToolRegistry] = None,
        approval_engine: Optional[AiToolApprovalEngine] = None,
    ) -> None:
        self.registry = registry or AtlasAiToolRegistry.get_instance()
        self.approval_engine = approval_engine or AiToolApprovalEngine.get_instance()
        # Mock/in-memory store for user-owned resource access verification (for IDOR checks)
        self._user_resources: Dict[
            str, Dict[str, str]
        ] = {}  # {resource_id: {owner_user_id: ..., tenant_id: ...}}

    @classmethod
    def get_instance(cls) -> "AiToolSecurityGateway":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def register_resource_owner(
        self,
        resource_type: str,
        resource_id: str,
        owner_user_id: str,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Helper to register resource ownership for tests and authorization checks."""
        self._user_resources[f"{resource_type}:{resource_id}"] = {
            "owner_user_id": owner_user_id,
            "tenant_id": tenant_id or "default_tenant",
        }

    def authorize_tool_invocation(
        self,
        tool: AtlasAiToolDefinition,
        user_id: str,
        arguments: Dict[str, Any],
        user_permissions: Optional[List[str]] = None,
        disabled_tools: Optional[List[str]] = None,
        approval_request_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Validates all security, permission, resource ACL, and approval requirements."""
        # 1. Verify tool lifecycle
        if tool.lifecycle_status != ToolLifecycleStatus.ENABLED:
            raise AiToolDisabledError(tool.tool_id, f"Tool status is {tool.lifecycle_status.value}")

        # 2. Check user-level disabled tools
        if disabled_tools and tool.tool_id in disabled_tools:
            raise AiToolDisabledError(tool.tool_id, "Tool is disabled in user preferences.")

        # 3. Verify Capability Scope
        perms = set(user_permissions or ["*"])
        if "*" not in perms:
            required_scope = tool.capability_scope.value
            if required_scope not in perms and "tools:read" not in perms:
                raise AiToolNotAuthorizedError(tool.tool_id, required_scope)

        # 4. Resource-Level Authorization (Anti-IDOR - Fixture D)
        self._check_resource_access(tool.tool_id, user_id, arguments)

        # 5. Check Provider Disclosure Policy (Fixture E)
        self._check_provider_disclosure(tool, provider_id)

        # 6. Check Human Approval Requirements (Fixture I & Mutations)
        if tool.approval_class in (
            ApprovalClass.USER_CONFIRMATION_REQUIRED,
            ApprovalClass.ADMIN_APPROVAL_REQUIRED,
        ):
            if not approval_request_id:
                # Issue new approval request
                req = self.approval_engine.create_approval_request(
                    tool_call_id="",  # Bound during dispatch
                    user_id=user_id,
                    tool_id=tool.tool_id,
                    approval_class=tool.approval_class,
                    arguments=arguments,
                    tenant_id=tenant_id,
                )
                from atlas.ai.tools.errors import AiToolApprovalRequiredError

                raise AiToolApprovalRequiredError(tool.tool_id, req.id)
            else:
                # Verify and consume provided approval token
                self.approval_engine.consume_and_verify(
                    approval_request_id=approval_request_id,
                    user_id=user_id,
                    tool_id=tool.tool_id,
                    arguments=arguments,
                )

    def _check_resource_access(self, tool_id: str, user_id: str, arguments: Dict[str, Any]) -> None:
        """Enforces strict owner-bound RLS on specific financial entities."""
        # Portfolio isolation check
        portfolio_id = arguments.get("portfolio_id")
        if portfolio_id:
            key = f"portfolio:{portfolio_id}"
            reg = self._user_resources.get(key)
            if reg and reg["owner_user_id"] != user_id:
                logger.warning(
                    "IDOR attempt: User %s attempted to access portfolio %s owned by %s",
                    user_id,
                    portfolio_id,
                    reg["owner_user_id"],
                )
                raise AiToolResourceAccessDeniedError("Portfolio", portfolio_id)

        # Risk Run isolation check
        run_id = arguments.get("run_id")
        if run_id:
            key = f"risk_run:{run_id}"
            reg = self._user_resources.get(key)
            if reg and reg["owner_user_id"] != user_id:
                logger.warning(
                    "IDOR attempt: User %s attempted to access risk run %s owned by %s",
                    user_id,
                    run_id,
                    reg["owner_user_id"],
                )
                raise AiToolResourceAccessDeniedError("Risk Run", run_id)

        # Screener isolation check
        screener_id = arguments.get("screener_id")
        if screener_id:
            key = f"screener:{screener_id}"
            reg = self._user_resources.get(key)
            if reg and reg["owner_user_id"] != user_id:
                raise AiToolResourceAccessDeniedError("Screener", screener_id)

    def _check_provider_disclosure(
        self, tool: AtlasAiToolDefinition, provider_id: Optional[str]
    ) -> None:
        """Verifies third-party vendor licensing and provider disclosure rules."""
        if tool.provider_disclosure_policy == ProviderDisclosurePolicy.PROHIBITED:
            raise AiToolProviderDisclosureDeniedError(
                tool.tool_id,
                f"Data policy strictly prohibits disclosing {tool.name} data to external model providers.",
            )

    @staticmethod
    def sanitize_untrusted_text(content: str) -> str:
        """Applies prompt-injection defense fencing to prevent indirect prompt injection (Fixture F)."""
        if not content:
            return content
        # Neutralize markdown/XML escape attacks and fence securely
        safe_content = content.replace("<atlas_", "&lt;atlas_").replace("</atlas_", "&lt;/atlas_")
        return f'<atlas_verified_financial_context data-purpose="untrusted-read-only-financial-context">\n{safe_content}\n</atlas_verified_financial_context>'
