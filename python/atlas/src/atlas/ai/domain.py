"""Domain models, enums, and data classes for Stage 124 AI Assistant V1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class MessageRole(str, Enum):
    """Role of the message author."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Lifecycle status of a message."""

    PENDING = "PENDING"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class GenerationStatus(str, Enum):
    """Status of an AI generation run."""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StreamEventType(str, Enum):
    """Types of Server-Sent Events emitted during AI streaming."""

    RUN_STARTED = "run_started"
    DELTA = "delta"
    TOOL_PROPOSED = "tool_proposed"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    APPROVAL_REQUIRED = "approval_required"
    RUN_COMPLETED = "run_completed"
    RUN_CANCELLED = "run_cancelled"
    ERROR = "error"


@dataclass(frozen=True)
class RouteContext:
    """Minimal allowlisted route descriptor for context-light navigation awareness."""

    route: str
    module_name: str
    summary: str


@dataclass(frozen=True)
class ModelCapability:
    """Represents an approved model and its operational parameters."""

    model_id: str
    name: str
    provider: str
    description: str
    context_window: int
    supports_streaming: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    is_default: bool = False


@dataclass
class AiGenerationRun:
    """Tracks an individual model generation run."""

    generation_id: str
    conversation_id: str
    user_message_id: str
    assistant_message_id: Optional[str]
    owner_user_id: str
    tenant_id: Optional[str]
    status: GenerationStatus
    model_id: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: Optional[float] = None
    source_manifest_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None


@dataclass
class AiMessage:
    """Represents a conversational message."""

    message_id: str
    conversation_id: str
    owner_user_id: str
    tenant_id: Optional[str]
    role: MessageRole
    content: str
    status: MessageStatus = MessageStatus.COMPLETED
    route_context: Optional[Dict[str, Any]] = None
    token_count: int = 0
    generation_run_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AiConversation:
    """Represents a multi-turn chat conversation session."""

    conversation_id: str
    owner_user_id: str
    tenant_id: Optional[str]
    title: str
    model_id: str
    provider: str
    system_prompt_override: Optional[str] = None
    is_archived: bool = False
    is_pinned: bool = False
    pinned_at: Optional[datetime] = None
    message_count: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: Optional[datetime] = None


@dataclass
class AiUserPreferences:
    """User preferences for the AI Assistant overlay and behaviour."""

    preference_id: str
    owner_user_id: str
    tenant_id: Optional[str]
    default_model_id: str = "atlas-intelligence-v1"
    temperature: float = 0.2
    send_on_enter: bool = True
    sound_enabled: bool = False
    overlay_dock_side: str = "right"
    overlay_width_px: int = 420
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StreamEvent:
    """SSE streaming event payload."""

    event_type: StreamEventType
    data: Dict[str, Any]
