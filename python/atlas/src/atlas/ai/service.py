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

        # Build prompt message turns with Stage 125 Context Awareness
        active_route = user_msg.route_context if user_msg else None
        context_block: Optional[str] = None

        if active_route:
            try:
                from atlas.ai.context.service import AiContextService

                ctx_service = AiContextService.get_instance()

                route_str = (
                    active_route.get("route") or active_route.get("current_route") or "/home"
                )
                module_str = active_route.get("module_name") or active_route.get("active_module")
                ws_id = active_route.get("workspace_id")
                panel_id = active_route.get("focused_panel_id") or active_route.get("panel_id")
                link_ch = active_route.get("global_link_channel_id") or active_route.get(
                    "link_channel_id"
                )
                mode_str = active_route.get("context_mode")
                req_refs = active_route.get("requested_references")
                extra_params = active_route.get("extra_adapter_params")

                envelope = await ctx_service.assemble_context(
                    user_id=owner_user_id,
                    tenant_id=conv.tenant_id,
                    conversation_id=conv.conversation_id,
                    user_query=user_msg.content,
                    current_route=route_str,
                    active_module=module_str,
                    workspace_id=ws_id,
                    focused_panel_id=panel_id,
                    global_link_channel_id=link_ch,
                    context_mode_override=mode_str,
                    requested_references=req_refs,
                    generation_id=generation_id,
                    model_id=gen_run.model_id,
                    provider_name=gen_run.provider,
                    extra_adapter_params=extra_params,
                )

                # Persist source manifest
                manifest = ctx_service.persist_source_manifest(envelope, generation_id)
                self.repository.update_generation_run(
                    generation_id=generation_id,
                    owner_user_id=owner_user_id,
                    source_manifest_id=manifest.manifest_id,
                )

                # Format verified context block
                context_block = ctx_service.format_context_for_prompt(envelope)
            except Exception as ctx_err:
                logger.warning("AiContextService assembly skipped due to error: %s", ctx_err)

        prompt_turns = PromptBuilder.build_prompt_messages(
            history=messages_history,
            system_override=conv.system_prompt_override,
            active_route=active_route,
            context_block=context_block,
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

        # Discover relevant authorized tools for this turn (Stage 126 Tool Gateway)
        from atlas.ai.tools.discovery import ToolDiscoveryService
        from atlas.ai.tools.dispatcher import AiToolDispatcher

        tool_disc = ToolDiscoveryService.get_instance()
        route_path = active_route.get("route") if active_route else None
        available_tools = tool_disc.discover_tools(
            user_id=owner_user_id,
            active_route=route_path,
            model_id=gen_run.model_id,
        )
        tools_declarations = tool_disc.format_tools_for_model(available_tools)

        provider = get_ai_provider(conv.provider)
        start_time = time.monotonic()
        accumulated_chunks: List[str] = []
        tool_call_count = 0

        try:
            async for event in provider.generate_stream(
                messages=prompt_turns,
                model_id=gen_run.model_id,
                temperature=0.2,
                cancellation_check=lambda: self.repository.is_cancelled(generation_id),
                tools=tools_declarations,
            ):
                if event.event_type == StreamEventType.TOOL_PROPOSED:
                    tool_id = event.data.get("tool_id", "")
                    tool_args = event.data.get("arguments", {})
                    tool_call_count += 1
                    yield event

                    # Emit TOOL_STARTED
                    yield StreamEvent(
                        event_type=StreamEventType.TOOL_STARTED,
                        data={"tool_id": tool_id, "arguments": tool_args},
                    )

                    # Execute via dispatcher
                    dispatcher = AiToolDispatcher.get_instance()
                    try:
                        tool_res = await dispatcher.dispatch(
                            tool_id=tool_id,
                            arguments=tool_args,
                            user_id=owner_user_id,
                            generation_run_id=generation_id,
                            conversation_id=conv.conversation_id,
                            tenant_id=conv.tenant_id,
                            active_route=route_path,
                            provider_id=conv.provider,
                            generation_tool_call_count=tool_call_count - 1,
                        )
                        yield StreamEvent(
                            event_type=StreamEventType.TOOL_COMPLETED,
                            data={
                                "tool_call_id": tool_res.tool_call_id,
                                "tool_id": tool_id,
                                "result": tool_res.data,
                                "execution_time_ms": tool_res.execution_time_ms,
                                "content_hash": tool_res.content_hash,
                            },
                        )

                        # Append tool output and stream continuation turn
                        import json
                        prompt_turns.append({
                            "role": "tool",
                            "name": tool_id,
                            "content": json.dumps(tool_res.data, default=str),
                        })

                        async for cont_event in provider.generate_stream(
                            messages=prompt_turns,
                            model_id=gen_run.model_id,
                            temperature=0.2,
                            cancellation_check=lambda: self.repository.is_cancelled(generation_id),
                            tools=tools_declarations,
                        ):
                            if cont_event.event_type == StreamEventType.DELTA:
                                delta_text = cont_event.data.get("delta", "")
                                accumulated_chunks.append(delta_text)
                                yield cont_event
                            elif cont_event.event_type == StreamEventType.RUN_CANCELLED:
                                yield cont_event
                                return

                    except Exception as tool_exc:
                        err_code = getattr(tool_exc, "code", "AI_TOOL_FAILED")
                        err_msg = getattr(tool_exc, "message", str(tool_exc))
                        yield StreamEvent(
                            event_type=StreamEventType.TOOL_FAILED,
                            data={
                                "tool_id": tool_id,
                                "error_code": err_code,
                                "error_message": err_msg,
                            },
                        )
                        if err_code == "AI_TOOL_APPROVAL_REQUIRED":
                            aprv_id = getattr(tool_exc, "approval_request_id", "")
                            yield StreamEvent(
                                event_type=StreamEventType.APPROVAL_REQUIRED,
                                data={
                                    "tool_id": tool_id,
                                    "approval_request_id": aprv_id,
                                    "message": err_msg,
                                },
                            )
                        # Yield error message chunk to user
                        fallback_msg = f"\n\n*(Tool execution notice: {err_msg})*"
                        accumulated_chunks.append(fallback_msg)
                        yield StreamEvent(
                            event_type=StreamEventType.DELTA,
                            data={"delta": fallback_msg},
                        )

                elif event.event_type == StreamEventType.DELTA:
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
