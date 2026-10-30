"""FastAPI Router for ATLAS Stage 124: AI Assistant V1 and Universal AI Overlay.
Mounted under /ai.
"""

from __future__ import annotations

import json
import logging
from typing import Annotated, Optional

from atlas.ai.domain import AiConversation, AiGenerationRun, AiMessage, AiUserPreferences
from atlas.ai.errors import AiError
from atlas.ai.schemas import (
    CancelGenerationResponse,
    ConversationListResponse,
    ConversationResponse,
    CreateConversationRequest,
    GenerationRunResponse,
    MessageListResponse,
    MessageResponse,
    ModelCapabilityResponse,
    ModelListResponse,
    RegenerateMessageRequest,
    SendMessageRequest,
    SendMessageResponse,
    UpdateConversationRequest,
    UpdateUserPreferencesRequest,
    UserPreferencesResponse,
)
from atlas.ai.service import AiAssistantService
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

_ai_service = AiAssistantService.get_instance()


def get_ai_service() -> AiAssistantService:
    return _ai_service


# ---------------- Model & Preference Helpers ----------------


def _map_conversation(c: AiConversation) -> ConversationResponse:
    return ConversationResponse(
        conversation_id=c.conversation_id,
        owner_user_id=c.owner_user_id,
        tenant_id=c.tenant_id,
        title=c.title,
        model_id=c.model_id,
        provider=c.provider,
        system_prompt_override=c.system_prompt_override,
        is_archived=c.is_archived,
        is_pinned=c.is_pinned,
        pinned_at=c.pinned_at,
        message_count=c.message_count,
        total_tokens=c.total_tokens,
        metadata=c.metadata,
        created_at=c.created_at,
        updated_at=c.updated_at,
        last_message_at=c.last_message_at,
    )


def _map_message(m: AiMessage) -> MessageResponse:
    return MessageResponse(
        message_id=m.message_id,
        conversation_id=m.conversation_id,
        owner_user_id=m.owner_user_id,
        tenant_id=m.tenant_id,
        role=m.role.value if hasattr(m.role, "value") else str(m.role),
        content=m.content,
        status=m.status.value if hasattr(m.status, "value") else str(m.status),
        route_context=m.route_context,
        token_count=m.token_count,
        generation_run_id=m.generation_run_id,
        error_code=m.error_code,
        error_message=m.error_message,
        metadata=m.metadata,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _map_generation(g: AiGenerationRun) -> GenerationRunResponse:
    return GenerationRunResponse(
        generation_id=g.generation_id,
        conversation_id=g.conversation_id,
        user_message_id=g.user_message_id,
        assistant_message_id=g.assistant_message_id,
        status=g.status.value if hasattr(g.status, "value") else str(g.status),
        model_id=g.model_id,
        provider=g.provider,
        prompt_tokens=g.prompt_tokens,
        completion_tokens=g.completion_tokens,
        total_tokens=g.total_tokens,
        duration_ms=g.duration_ms,
        error_code=g.error_code,
        error_message=g.error_message,
        created_at=g.created_at,
        finished_at=g.finished_at,
    )


def _map_preferences(p: AiUserPreferences) -> UserPreferencesResponse:
    return UserPreferencesResponse(
        preference_id=p.preference_id,
        owner_user_id=p.owner_user_id,
        tenant_id=p.tenant_id,
        default_model_id=p.default_model_id,
        temperature=p.temperature,
        send_on_enter=p.send_on_enter,
        sound_enabled=p.sound_enabled,
        overlay_dock_side=p.overlay_dock_side,
        overlay_width_px=p.overlay_width_px,
        metadata=p.metadata,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ---------------- Conversations Endpoints ----------------


@router.post(
    "/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
def create_conversation(
    payload: CreateConversationRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> ConversationResponse:
    try:
        conv = service.create_conversation(
            owner_user_id=current_user.sub,
            title=payload.title or "New Conversation",
            model_id=payload.model_id,
            system_prompt_override=payload.system_prompt_override,
            metadata=payload.metadata,
            tenant_id=getattr(current_user, "tenant_id", None),
        )
        return _map_conversation(conv)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
    search: Optional[str] = Query(None, description="Search term matching title"),
    archived: Optional[bool] = Query(False, description="Filter by archived state"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ConversationListResponse:
    try:
        items, total = service.list_conversations(
            owner_user_id=current_user.sub,
            search_query=search,
            is_archived=archived,
            limit=limit,
            offset=offset,
        )
        return ConversationListResponse(
            items=[_map_conversation(c) for c in items],
            total=total,
            limit=limit,
            offset=offset,
        )
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> ConversationResponse:
    try:
        conv = service.get_conversation(conversation_id, current_user.sub)
        return _map_conversation(conv)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    payload: UpdateConversationRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> ConversationResponse:
    try:
        conv = service.update_conversation(
            conversation_id=conversation_id,
            owner_user_id=current_user.sub,
            title=payload.title,
            is_archived=payload.is_archived,
            is_pinned=payload.is_pinned,
            model_id=payload.model_id,
            metadata=payload.metadata,
        )
        return _map_conversation(conv)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> None:
    try:
        service.delete_conversation(conversation_id, current_user.sub)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Messages Endpoints ----------------


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
def list_messages(
    conversation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> MessageListResponse:
    try:
        msgs = service.list_messages(conversation_id, current_user.sub, limit=limit, offset=offset)
        return MessageListResponse(
            items=[_map_message(m) for m in msgs],
            total=len(msgs),
        )
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
def send_message(
    conversation_id: str,
    payload: SendMessageRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> SendMessageResponse:
    try:
        user_msg, gen_run = service.send_message(
            conversation_id=conversation_id,
            owner_user_id=current_user.sub,
            content=payload.content,
            route_context=payload.route_context,
            tenant_id=getattr(current_user, "tenant_id", None),
        )
        return SendMessageResponse(
            message=_map_message(user_msg),
            generation_id=gen_run.generation_id,
        )
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/conversations/{conversation_id}/regenerate", response_model=SendMessageResponse)
def regenerate_message(
    conversation_id: str,
    payload: RegenerateMessageRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> SendMessageResponse:
    try:
        user_msg, gen_run = service.regenerate_message(
            conversation_id=conversation_id,
            owner_user_id=current_user.sub,
            target_message_id=payload.target_message_id,
        )
        return SendMessageResponse(
            message=_map_message(user_msg),
            generation_id=gen_run.generation_id,
        )
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Streaming & Generation Runs ----------------


@router.get("/generations/{generation_id}", response_model=GenerationRunResponse)
def get_generation(
    generation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> GenerationRunResponse:
    try:
        run = service.get_generation_run(generation_id, current_user.sub)
        return _map_generation(run)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/generations/{generation_id}/stream")
async def stream_generation(
    generation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
):
    """Server-Sent Events endpoint streaming AI response tokens and run status."""
    try:
        # Pre-validate run exists and user has access
        service.get_generation_run(generation_id, current_user.sub)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )

    async def sse_event_generator():
        async for event in service.stream_generation(generation_id, current_user.sub):
            event_name = (
                event.event_type.value
                if hasattr(event.event_type, "value")
                else str(event.event_type)
            )
            data_payload = json.dumps(event.data)
            yield f"event: {event_name}\ndata: {data_payload}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/generations/{generation_id}/cancel", response_model=CancelGenerationResponse)
def cancel_generation(
    generation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> CancelGenerationResponse:
    try:
        service.cancel_generation(generation_id, current_user.sub)
        return CancelGenerationResponse(generation_id=generation_id, cancelled=True)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Model Registry & Preferences ----------------


@router.get("/models", response_model=ModelListResponse)
def list_models(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> ModelListResponse:
    models = service.list_models()
    return ModelListResponse(
        models=[
            ModelCapabilityResponse(
                model_id=m.model_id,
                name=m.name,
                provider=m.provider,
                description=m.description,
                context_window=m.context_window,
                supports_streaming=m.supports_streaming,
                cost_per_1k_input=m.cost_per_1k_input,
                cost_per_1k_output=m.cost_per_1k_output,
                is_default=m.is_default,
            )
            for m in models
        ]
    )


@router.get("/preferences", response_model=UserPreferencesResponse)
def get_preferences(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> UserPreferencesResponse:
    prefs = service.get_user_preferences(
        owner_user_id=current_user.sub,
        tenant_id=getattr(current_user, "tenant_id", None),
    )
    return _map_preferences(prefs)


@router.put("/preferences", response_model=UserPreferencesResponse)
def update_preferences(
    payload: UpdateUserPreferencesRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiAssistantService, Depends(get_ai_service)],
) -> UserPreferencesResponse:
    try:
        prefs = service.update_user_preferences(
            owner_user_id=current_user.sub,
            default_model_id=payload.default_model_id,
            temperature=payload.temperature,
            send_on_enter=payload.send_on_enter,
            sound_enabled=payload.sound_enabled,
            overlay_dock_side=payload.overlay_dock_side,
            overlay_width_px=payload.overlay_width_px,
            metadata=payload.metadata,
        )
        return _map_preferences(prefs)
    except AiError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )
