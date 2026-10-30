"""ATLAS AI Tool Gateway Package (Stage 126 of 150).

Provides secure, permission-aware function calling, tool registry, discovery,
and dispatch for the ATLAS AI Assistant.
"""

# Ensure all adapters are registered
import atlas.ai.tools.adapters  # noqa: F401
from atlas.ai.tools.approval import AiToolApprovalEngine
from atlas.ai.tools.discovery import ToolDiscoveryService
from atlas.ai.tools.dispatcher import AiToolDispatcher
from atlas.ai.tools.domain import (
    AiToolApprovalRequest,
    AiToolCall,
    AiToolSourceManifest,
    AiToolUserPreferences,
    ApprovalClass,
    ApprovalStatus,
    AtlasAiToolDefinition,
    AtlasAiToolResult,
    CapabilityScope,
    ProviderDisclosurePolicy,
    ToolCallStatus,
    ToolCategory,
    ToolLifecycleStatus,
)
from atlas.ai.tools.errors import (
    AiToolApprovalDeniedError,
    AiToolApprovalExpiredError,
    AiToolApprovalMismatchError,
    AiToolApprovalRequiredError,
    AiToolArgumentInvalidError,
    AiToolDisabledError,
    AiToolError,
    AiToolNotAuthorizedError,
    AiToolNotFoundError,
    AiToolProviderDisclosureDeniedError,
    AiToolQuotaExceededError,
    AiToolRateLimitedError,
    AiToolResourceAccessDeniedError,
    AiToolSequenceLimitExceededError,
    AiToolTimeoutError,
)
from atlas.ai.tools.gateway import AiToolSecurityGateway
from atlas.ai.tools.registry import AtlasAiToolRegistry

__all__ = [
    "AiToolApprovalEngine",
    "AiToolApprovalRequest",
    "AiToolCall",
    "AiToolDispatcher",
    "AiToolSecurityGateway",
    "AiToolSourceManifest",
    "AiToolUserPreferences",
    "AtlasAiToolDefinition",
    "AtlasAiToolRegistry",
    "AtlasAiToolResult",
    "ToolDiscoveryService",
    "ApprovalClass",
    "ApprovalStatus",
    "CapabilityScope",
    "ProviderDisclosurePolicy",
    "ToolCategory",
    "ToolCallStatus",
    "ToolLifecycleStatus",
    "AiToolError",
    "AiToolNotFoundError",
    "AiToolDisabledError",
    "AiToolNotAuthorizedError",
    "AiToolResourceAccessDeniedError",
    "AiToolProviderDisclosureDeniedError",
    "AiToolArgumentInvalidError",
    "AiToolApprovalRequiredError",
    "AiToolApprovalDeniedError",
    "AiToolApprovalExpiredError",
    "AiToolApprovalMismatchError",
    "AiToolQuotaExceededError",
    "AiToolRateLimitedError",
    "AiToolTimeoutError",
    "AiToolSequenceLimitExceededError",
]
