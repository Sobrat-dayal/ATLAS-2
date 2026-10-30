"""Pydantic schemas for request validation and response serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ---------------- Conversations ----------------


class CreateConversationRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    model_id: Optional[str] = Field(None, max_length=64)
    system_prompt_override: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    is_archived: Optional[bool] = None
    is_pinned: Optional[bool] = None
    model_id: Optional[str] = Field(None, max_length=64)
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    conversation_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    title: str
    model_id: str
    provider: str
    system_prompt_override: Optional[str] = None
    is_archived: bool
    is_pinned: bool
    pinned_at: Optional[datetime] = None
    message_count: int
    total_tokens: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    limit: int
    offset: int


# ---------------- Messages ----------------


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=16000)
    route_context: Optional[Dict[str, Any]] = None


class RegenerateMessageRequest(BaseModel):
    target_message_id: Optional[str] = None


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    role: str
    content: str
    status: str
    route_context: Optional[Dict[str, Any]] = None
    token_count: int
    generation_run_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int


class SendMessageResponse(BaseModel):
    message: MessageResponse
    generation_id: str


# ---------------- Generations ----------------


class GenerationRunResponse(BaseModel):
    generation_id: str
    conversation_id: str
    user_message_id: str
    assistant_message_id: Optional[str] = None
    status: str
    model_id: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None


class CancelGenerationResponse(BaseModel):
    generation_id: str
    cancelled: bool = True


# ---------------- Models & Preferences ----------------


class ModelCapabilityResponse(BaseModel):
    model_id: str
    name: str
    provider: str
    description: str
    context_window: int
    supports_streaming: bool
    cost_per_1k_input: float
    cost_per_1k_output: float
    is_default: bool


class ModelListResponse(BaseModel):
    models: List[ModelCapabilityResponse]


class UserPreferencesResponse(BaseModel):
    preference_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    default_model_id: str
    temperature: float
    send_on_enter: bool
    sound_enabled: bool
    overlay_dock_side: str
    overlay_width_px: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class UpdateUserPreferencesRequest(BaseModel):
    default_model_id: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    send_on_enter: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    overlay_dock_side: Optional[str] = None
    overlay_width_px: Optional[int] = Field(None, ge=320, le=800)
    metadata: Optional[Dict[str, Any]] = None
