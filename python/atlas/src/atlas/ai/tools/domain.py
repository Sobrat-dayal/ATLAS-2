"""Canonical Domain Models for Stage 126: ATLAS AI Tool Gateway.

Defines immutable enumerations, dataclasses, lifecycle states, approval classes,
and result envelopes governing zero-trust AI tool calling.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ToolCategory(str, Enum):
    """Classification of tool capabilities and risk profiles."""

    DISCOVERY = "DISCOVERY"
    DATA_READ = "DATA_READ"
    ANALYTICAL_READ = "ANALYTICAL_READ"
    STATUS_READ = "STATUS_READ"
    COMPUTATIONAL = "COMPUTATIONAL"
    USER_STATE_MUTATION = "USER_STATE_MUTATION"
    FINANCIAL_MUTATION = "FINANCIAL_MUTATION"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    PRIVILEGED_OPERATION = "PRIVILEGED_OPERATION"


class ToolLifecycleStatus(str, Enum):
    """Operational lifecycle status of a registered tool."""

    REGISTERED = "REGISTERED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    DEPRECATED = "DEPRECATED"
    UNAVAILABLE = "UNAVAILABLE"


class ToolCallStatus(str, Enum):
    """State machine states for an AI tool call invocation."""

    PROPOSED = "PROPOSED"
    VALIDATING = "VALIDATING"
    AUTHORIZING = "AUTHORIZING"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    REJECTED = "REJECTED"


class ApprovalClass(str, Enum):
    """Governance tier governing whether human-in-the-loop confirmation is required."""

    NO_APPROVAL_REQUIRED = "NO_APPROVAL_REQUIRED"
    USER_CONFIRMATION_REQUIRED = "USER_CONFIRMATION_REQUIRED"
    STEP_UP_AUTH_REQUIRED = "STEP_UP_AUTH_REQUIRED"
    ADMIN_APPROVAL_REQUIRED = "ADMIN_APPROVAL_REQUIRED"
    PROHIBITED = "PROHIBITED"


class ApprovalStatus(str, Enum):
    """Current resolution status of an approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"


class ProviderDisclosurePolicy(str, Enum):
    """Restrictions governing transmission of tool output to external LLM providers."""

    ALLOWED = "ALLOWED"
    REDACTED = "REDACTED"
    PROHIBITED = "PROHIBITED"


class CapabilityScope(str, Enum):
    """Fine-grained permission scopes for tool authorization."""

    TOOLS_READ = "tools:read"
    INSTRUMENT_READ = "tools:instrument:read"
    MARKET_READ = "tools:market:read"
    COMPANY_READ = "tools:company:read"
    WATCHLIST_READ = "tools:watchlist:read"
    SCREENER_READ = "tools:screener:read"
    ECONOMICS_READ = "tools:economics:read"
    NEWS_READ = "tools:news:read"
    RESEARCH_READ = "tools:research:read"
    PORTFOLIO_READ = "tools:portfolio:read"
    RISK_READ = "tools:risk:read"
    DATA_READ = "tools:data:read"
    SAVED_READ = "tools:saved:read"
    WORKSPACE_READ = "tools:workspace:read"
    ADMIN_OPERATION = "tools:admin"


@dataclass(frozen=True)
class AtlasAiToolDefinition:
    """Canonical registry definition of an institutional AI tool."""

    tool_id: str
    version: str = "1.0.0"
    category: ToolCategory = ToolCategory.DATA_READ
    name: str = ""
    description: str = ""
    capability_scope: CapabilityScope = CapabilityScope.TOOLS_READ
    approval_class: ApprovalClass = ApprovalClass.NO_APPROVAL_REQUIRED
    provider_disclosure_policy: ProviderDisclosurePolicy = ProviderDisclosurePolicy.ALLOWED
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    returns_schema: Dict[str, Any] = field(default_factory=dict)
    idempotency_key_fields: List[str] = field(default_factory=list)
    timeout_seconds: float = 10.0
    rate_limit_per_minute: int = 60
    max_result_size_bytes: int = 100_000
    lifecycle_status: ToolLifecycleStatus = ToolLifecycleStatus.ENABLED
    requires_tenant_scope: bool = False
    supported_models: List[str] = field(default_factory=lambda: ["*"])

    def to_openai_function_declaration(self) -> Dict[str, Any]:
        """Formats the tool definition into OpenAI-compatible function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.tool_id,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


@dataclass(frozen=True)
class AiToolSourceManifest:
    """Provenance and licensing metadata for financial data returned by a tool."""

    tool_id: str
    data_source: str
    as_of: str
    attribution: str
    provider_disclosure_status: ProviderDisclosurePolicy = ProviderDisclosurePolicy.ALLOWED
    record_count: int = 1
    content_hash: str = ""


@dataclass(frozen=True)
class AtlasAiToolResult:
    """Standardized institutional execution envelope for all tool calls."""

    tool_call_id: str
    tool_id: str
    success: bool
    data: Any
    source_manifest: Optional[AiToolSourceManifest] = None
    execution_time_ms: float = 0.0
    as_of: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    truncated: bool = False
    content_hash: str = ""

    def calculate_hash(self) -> str:
        """Computes deterministic SHA-256 hash of result data payload."""
        serialized = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class AiToolCall:
    """Lifecycle tracking entity representing a single tool invocation."""

    id: str
    user_id: str
    tool_id: str
    arguments: Dict[str, Any]
    normalized_arguments_hash: str
    generation_run_id: Optional[str] = None
    conversation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    tool_version: str = "1.0.0"
    status: ToolCallStatus = ToolCallStatus.PROPOSED
    result: Optional[AtlasAiToolResult] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    approval_class: ApprovalClass = ApprovalClass.NO_APPROVAL_REQUIRED
    approval_request_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AiToolApprovalRequest:
    """Security token and approval record binding an explicit operation to human consent."""

    id: str
    tool_call_id: str
    user_id: str
    tool_id: str
    approval_class: ApprovalClass
    normalized_arguments_hash: str
    arguments_summary: Dict[str, Any]
    expires_at: datetime
    tenant_id: Optional[str] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    consumed_at: Optional[datetime] = None
    decision_reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AiToolUserPreferences:
    """User-level settings for AI tool discovery, auto-approval, and permissions."""

    user_id: str
    enabled_tools: List[str] = field(default_factory=list)
    disabled_tools: List[str] = field(default_factory=list)
    auto_approve_read_only: bool = True
    require_approval_for_sensitive: bool = True
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def hash_arguments(arguments: Dict[str, Any]) -> str:
    """Deterministically normalizes and computes SHA-256 digest of tool arguments."""
    normalized = json.dumps(arguments, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
