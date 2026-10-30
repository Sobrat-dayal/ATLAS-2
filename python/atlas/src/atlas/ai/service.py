"""AiAssistantService coordinating conversation management, prompt generation, and streaming."""

from __future__ import annotations

import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from atlas.ai.domain import (
    AiConversation,
    AiGenerationRun,
    AiMessage,
    AiUserPreferences,
    GenerationStatus,
    MessageRole,
    MessageStatus,
    ModelCapability,
    StreamEvent,
    StreamEventType,
)
from atlas.ai.errors import (
    AiConversationEmptyError,
    AiConversationNotFoundError,
    AiGenerationRunNotFoundError,
    AiMessageTooLargeError,
    AiModelNotFoundError,
)
from atlas.ai.prompts.prompt_builder import PromptBuilder
from atlas.ai.providers.factory import get_ai_provider
from atlas.ai.providers.registry import (
    DEFAULT_MODEL_ID,
    get_model_capability,
    is_valid_model,
    list_approved_models,
)
from atlas.ai.repository import AiRepository

logger = logging.getLogger(__name__)


class AiAssistantService:
    """Core domain service for Stage 124 AI Assistant V1 and AppShell Overlay."""

    _instance: Optional["AiAssistantService"] = None

    def __init__(self, repository: Optional[AiRepository] = None):
        self.repository = repository or AiRepository.get_instance()

    @classmethod
    def get_instance(cls) -> "AiAssistantService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ---------------- Conversation Management ----------------

    def create_conversation(
        self,
        owner_user_id: str,
        title: str = "New Conversation",
        model_id: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AiConversation:
        selected_model = model_id or DEFAULT_MODEL_ID
        if not is_valid_model(selected_model):
            raise AiModelNotFoundError(selected_model)

        model_cap = get_model_capability(selected_model)
        return self.repository.create_conversation(
            owner_user_id=owner_user_id,
            title=title,
            model_id=selected_model,
            provider=model_cap.provider,
            system_prompt_override=system_prompt_override,
            metadata=metadata,
            tenant_id=tenant_id,
        )

    def list_conversations(
        self,
        owner_user_id: str,
        search_query: Optional[str] = None,
        is_archived: Optional[bool] = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[AiConversation], int]:
        return self.repository.list_conversations(
            owner_user_id=owner_user_id,
            search_query=search_query,
            is_archived=is_archived,
            limit=limit,
            offset=offset,
        )

    def get_conversation(self, conversation_id: str, owner_user_id: str) -> AiConversation:
        conv = self.repository.get_conversation(conversation_id, owner_user_id)
        if not conv:
            raise AiConversationNotFoundError(conversation_id)
        return conv

    def update_conversation(
        self,
        conversation_id: str,
        owner_user_id: str,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        model_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AiConversation:
        if model_id is not None and not is_valid_model(model_id):
            raise AiModelNotFoundError(model_id)

        return self.repository.update_conversation(
            conversation_id=conversation_id,
            owner_user_id=owner_user_id,
            title=title,
            is_archived=is_archived,
            is_pinned=is_pinned,
            model_id=model_id,
            metadata=metadata,
        )

    def delete_conversation(self, conversation_id: str, owner_user_id: str) -> bool:
        return self.repository.delete_conversation(conversation_id, owner_user_id)

    # ---------------- Messages & Generation ----------------

    def list_messages(
        self,
        conversation_id: str,
        owner_user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AiMessage]:
        return self.repository.list_messages(
            conversation_id=conversation_id,
            owner_user_id=owner_user_id,
            limit=limit,
            offset=offset,
        )

    def send_message(
        self,
        conversation_id: str,
        owner_user_id: str,
        content: str,
        route_context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> Tuple[AiMessage, AiGenerationRun]:
        """Validates input, records user message turn, and prepares generation run."""
        clean_content = content.strip()
        if len(clean_content) > 16000:
            raise AiMessageTooLargeError(len(clean_content), 16000)

        conv = self.get_conversation(conversation_id, owner_user_id)

        # 1. Store User Message
        user_msg = self.repository.add_message(
            conversation_id=conversation_id,
            owner_user_id=owner_user_id,
            role=MessageRole.USER,
            content=clean_content,
            route_context=route_context,
            status=MessageStatus.COMPLETED,
            tenant_id=tenant_id,
        )

        # 2. Prepare Generation Run
        gen_run = self.repository.create_generation_run(
            conversation_id=conversation_id,
            user_message_id=user_msg.message_id,
            owner_user_id=owner_user_id,
            model_id=conv.model_id,
            provider=conv.provider,
            tenant_id=tenant_id,
        )
        self.repository.register_cancellation_token(gen_run.generation_id)

        return user_msg, gen_run

    async def stream_generation(
        self,
        generation_id: str,
        owner_user_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """Streams Server-Sent Events for a generation run, accumulating output into the database."""
        gen_run = self.repository.get_generation_run(generation_id, owner_user_id)
        if not gen_run:
            raise AiGenerationRunNotFoundError(generation_id)

        conv = self.get_conversation(gen_run.conversation_id, owner_user_id)
        user_msg = self.repository.get_message(gen_run.user_message_id, owner_user_id)
        messages_history = self.repository.list_messages(gen_run.conversation_id, owner_user_id)

        # Build prompt message turns
        active_route = user_msg.route_context if user_msg else None
        prompt_turns = PromptBuilder.build_prompt_messages(
            history=messages_history,
            system_override=conv.system_prompt_override,
            active_route=active_route,
        )

        # Create placeholder assistant message
        assistant_msg = self.repository.add_message(
            conversation_id=conv.conversation_id,
            owner_user_id=owner_user_id,
            role=MessageRole.ASSISTANT,
            content="",
            generation_run_id=generation_id,
            status=MessageStatus.STREAMING,
            tenant_id=conv.tenant_id,
        )
        self.repository.update_generation_run(
            generation_id=generation_id,
            owner_user_id=owner_user_id,
            assistant_message_id=assistant_msg.message_id,
        )

        provider = get_ai_provider(conv.provider)
        start_time = time.monotonic()
        accumulated_chunks: List[str] = []

        try:
            async for event in provider.generate_stream(
                messages=prompt_turns,
                model_id=gen_run.model_id,
                temperature=0.2,
                cancellation_check=lambda: self.repository.is_cancelled(generation_id),
            ):
                if event.event_type == StreamEventType.DELTA:
                    delta_text = event.data.get("delta", "")
                    accumulated_chunks.append(delta_text)
                    yield event

                elif event.event_type == StreamEventType.RUN_CANCELLED:
                    final_content = "".join(accumulated_chunks)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    self.repository.update_message(
                        message_id=assistant_msg.message_id,
                        owner_user_id=owner_user_id,
                        content=final_content,
                        status=MessageStatus.CANCELLED,
                    )
                    self.repository.update_generation_run(
                        generation_id=generation_id,
                        owner_user_id=owner_user_id,
                        status=GenerationStatus.CANCELLED,
                        duration_ms=duration_ms,
                    )
                    yield event
                    return

                elif event.event_type == StreamEventType.RUN_COMPLETED:
                    final_content = "".join(accumulated_chunks)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    prompt_toks = event.data.get(
                        "prompt_tokens", len(str(prompt_turns).split()) * 2
                    )
                    comp_toks = event.data.get("completion_tokens", len(final_content.split()) * 2)
                    total_toks = event.data.get("total_tokens", prompt_toks + comp_toks)

                    self.repository.update_message(
                        message_id=assistant_msg.message_id,
                        owner_user_id=owner_user_id,
                        content=final_content,
                        status=MessageStatus.COMPLETED,
                        token_count=comp_toks,
                    )
                    self.repository.update_generation_run(
                        generation_id=generation_id,
                        owner_user_id=owner_user_id,
                        status=GenerationStatus.COMPLETED,
                        prompt_tokens=prompt_toks,
                        completion_tokens=comp_toks,
                        total_tokens=total_toks,
                        duration_ms=duration_ms,
                    )
                    yield event
                    return

                elif event.event_type == StreamEventType.ERROR:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    err_code = event.data.get("error_code", "AI_PROVIDER_ERROR")
                    err_msg = event.data.get("message", "Error during generation")
                    self.repository.update_message(
                        message_id=assistant_msg.message_id,
                        owner_user_id=owner_user_id,
                        status=MessageStatus.FAILED,
                        error_code=err_code,
                        error_message=err_msg,
                    )
                    self.repository.update_generation_run(
                        generation_id=generation_id,
                        owner_user_id=owner_user_id,
                        status=GenerationStatus.FAILED,
                        duration_ms=duration_ms,
                        error_code=err_code,
                        error_message=err_msg,
                    )
                    yield event
                    return

                else:
                    yield event

        except Exception as exc:
            logger.error("Unhandled exception in stream_generation: %s", exc)
            duration_ms = (time.monotonic() - start_time) * 1000
            self.repository.update_message(
                message_id=assistant_msg.message_id,
                owner_user_id=owner_user_id,
                status=MessageStatus.FAILED,
                error_code="AI_GENERATION_FAILED",
                error_message=str(exc),
            )
            self.repository.update_generation_run(
                generation_id=generation_id,
                owner_user_id=owner_user_id,
                status=GenerationStatus.FAILED,
                duration_ms=duration_ms,
                error_code="AI_GENERATION_FAILED",
                error_message=str(exc),
            )
            yield StreamEvent(
                event_type=StreamEventType.ERROR,
                data={"error_code": "AI_GENERATION_FAILED", "message": str(exc)},
            )

    def cancel_generation(self, generation_id: str, owner_user_id: str) -> bool:
        """Requests cancellation of an ongoing generation run."""
        gen_run = self.repository.get_generation_run(generation_id, owner_user_id)
        if not gen_run:
            raise AiGenerationRunNotFoundError(generation_id)

        self.repository.request_cancellation(generation_id)
        self.repository.update_generation_run(
            generation_id=generation_id,
            owner_user_id=owner_user_id,
            status=GenerationStatus.CANCELLED,
        )
        if gen_run.assistant_message_id:
            self.repository.update_message(
                message_id=gen_run.assistant_message_id,
                owner_user_id=owner_user_id,
                status=MessageStatus.CANCELLED,
            )
        return True

    def regenerate_message(
        self,
        conversation_id: str,
        owner_user_id: str,
        target_message_id: Optional[str] = None,
    ) -> Tuple[AiMessage, AiGenerationRun]:
        """Regenerates the assistant response for the target message or the last user prompt."""
        conv = self.get_conversation(conversation_id, owner_user_id)
        messages = self.repository.list_messages(conversation_id, owner_user_id)

        user_msg = None
        if target_message_id:
            target = self.repository.get_message(target_message_id, owner_user_id)
            if target and target.role == MessageRole.USER:
                user_msg = target
            elif target and target.role == MessageRole.ASSISTANT:
                # Find previous user message
                idx = next(
                    (i for i, m in enumerate(messages) if m.message_id == target_message_id), None
                )
                if idx is not None and idx > 0:
                    user_msg = messages[idx - 1]

        if not user_msg:
            # Find the most recent user message
            user_msg = next((m for m in reversed(messages) if m.role == MessageRole.USER), None)

        if not user_msg:
            raise AiConversationEmptyError(conversation_id)

        # Create new generation run
        gen_run = self.repository.create_generation_run(
            conversation_id=conversation_id,
            user_message_id=user_msg.message_id,
            owner_user_id=owner_user_id,
            model_id=conv.model_id,
            provider=conv.provider,
            tenant_id=conv.tenant_id,
        )
        self.repository.register_cancellation_token(gen_run.generation_id)

        return user_msg, gen_run

    def get_generation_run(self, generation_id: str, owner_user_id: str) -> AiGenerationRun:
        run = self.repository.get_generation_run(generation_id, owner_user_id)
        if not run:
            raise AiGenerationRunNotFoundError(generation_id)
        return run

    # ---------------- User Preferences ----------------

    def get_user_preferences(
        self, owner_user_id: str, tenant_id: Optional[str] = None
    ) -> AiUserPreferences:
        return self.repository.get_user_preferences(owner_user_id, tenant_id)

    def update_user_preferences(
        self,
        owner_user_id: str,
        default_model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        send_on_enter: Optional[bool] = None,
        sound_enabled: Optional[bool] = None,
        overlay_dock_side: Optional[str] = None,
        overlay_width_px: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AiUserPreferences:
        if default_model_id is not None and not is_valid_model(default_model_id):
            raise AiModelNotFoundError(default_model_id)

        return self.repository.update_user_preferences(
            owner_user_id=owner_user_id,
            default_model_id=default_model_id,
            temperature=temperature,
            send_on_enter=send_on_enter,
            sound_enabled=sound_enabled,
            overlay_dock_side=overlay_dock_side,
            overlay_width_px=overlay_width_px,
            metadata=metadata,
        )

    # ---------------- Model Catalog ----------------

    def list_models(self) -> List[ModelCapability]:
        return list_approved_models()

    def get_model(self, model_id: str) -> ModelCapability:
        return get_model_capability(model_id)
