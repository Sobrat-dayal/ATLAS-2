"""Thread-safe Repository for Stage 124 AI Assistant V1."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.ai.domain import (
    AiConversation,
    AiGenerationRun,
    AiMessage,
    AiUserPreferences,
    GenerationStatus,
    MessageRole,
    MessageStatus,
)
from atlas.ai.errors import (
    AiAccessDeniedError,
    AiConversationNotFoundError,
    AiGenerationRunNotFoundError,
    AiMessageNotFoundError,
)


class AiRepository:
    """Thread-safe in-memory and persistence-ready repository for AI conversations and runs."""

    _instance: Optional["AiRepository"] = None

    def __init__(self):
        self._lock = threading.RLock()
        self._conversations: Dict[str, AiConversation] = {}
        self._messages: Dict[str, List[AiMessage]] = {}  # conversation_id -> list of messages
        self._message_lookup: Dict[str, AiMessage] = {}  # message_id -> AiMessage
        self._generation_runs: Dict[str, AiGenerationRun] = {}  # generation_id -> AiGenerationRun
        self._preferences: Dict[str, AiUserPreferences] = {}  # owner_user_id -> AiUserPreferences
        self._cancelled_generations: Set[str] = set()
        self._audit_events: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "AiRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ---------------- Conversations ----------------

    def create_conversation(
        self,
        owner_user_id: str,
        title: str = "New Conversation",
        model_id: str = "atlas-intelligence-v1",
        provider: str = "atlas",
        system_prompt_override: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AiConversation:
        with self._lock:
            conv_id = f"conv_{uuid.uuid4().hex[:16]}"
            now = datetime.now(timezone.utc)
            conversation = AiConversation(
                conversation_id=conv_id,
                owner_user_id=owner_user_id,
                tenant_id=tenant_id,
                title=title,
                model_id=model_id,
                provider=provider,
                system_prompt_override=system_prompt_override,
                is_archived=False,
                is_pinned=False,
                pinned_at=None,
                message_count=0,
                total_tokens=0,
                metadata=metadata or {},
                created_at=now,
                updated_at=now,
                last_message_at=None,
            )
            self._conversations[conv_id] = conversation
            self._messages[conv_id] = []
            self.record_audit_event(
                owner_user_id=owner_user_id,
                event_type="CONVERSATION_CREATED",
                conversation_id=conv_id,
                payload={"title": title, "model_id": model_id},
            )
            return conversation

    def get_conversation(
        self, conversation_id: str, owner_user_id: str
    ) -> Optional[AiConversation]:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if not conv:
                return None
            if conv.owner_user_id != owner_user_id:
                raise AiAccessDeniedError("conversation", conversation_id)
            return conv

    def list_conversations(
        self,
        owner_user_id: str,
        search_query: Optional[str] = None,
        is_archived: Optional[bool] = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[AiConversation], int]:
        with self._lock:
            user_convs = [
                c for c in self._conversations.values() if c.owner_user_id == owner_user_id
            ]

            if is_archived is not None:
                user_convs = [c for c in user_convs if c.is_archived == is_archived]

            if search_query:
                q = search_query.lower()
                user_convs = [c for c in user_convs if q in c.title.lower()]

            # Sort: pinned first, then last_message_at or updated_at descending
            user_convs.sort(
                key=lambda c: (
                    1 if c.is_pinned else 0,
                    (c.last_message_at or c.updated_at).timestamp(),
                ),
                reverse=True,
            )

            total = len(user_convs)
            paginated = user_convs[offset : offset + limit]
            return paginated, total

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
        with self._lock:
            conv = self.get_conversation(conversation_id, owner_user_id)
            if not conv:
                raise AiConversationNotFoundError(conversation_id)

            now = datetime.now(timezone.utc)
            if title is not None:
                conv.title = title.strip() or "Untitled Conversation"
            if is_archived is not None:
                conv.is_archived = is_archived
            if is_pinned is not None:
                conv.is_pinned = is_pinned
                conv.pinned_at = now if is_pinned else None
            if model_id is not None:
                conv.model_id = model_id
            if metadata is not None:
                conv.metadata.update(metadata)
            conv.updated_at = now

            self.record_audit_event(
                owner_user_id=owner_user_id,
                event_type="CONVERSATION_UPDATED",
                conversation_id=conversation_id,
                payload={
                    "title": conv.title,
                    "is_archived": conv.is_archived,
                    "is_pinned": conv.is_pinned,
                },
            )
            return conv

    def delete_conversation(self, conversation_id: str, owner_user_id: str) -> bool:
        with self._lock:
            conv = self.get_conversation(conversation_id, owner_user_id)
            if not conv:
                raise AiConversationNotFoundError(conversation_id)

            messages = self._messages.pop(conversation_id, [])
            for m in messages:
                self._message_lookup.pop(m.message_id, None)

            self._conversations.pop(conversation_id, None)

            self.record_audit_event(
                owner_user_id=owner_user_id,
                event_type="CONVERSATION_DELETED",
                conversation_id=conversation_id,
                payload={},
            )
            return True

    # ---------------- Messages ----------------

    def add_message(
        self,
        conversation_id: str,
        owner_user_id: str,
        role: MessageRole,
        content: str,
        route_context: Optional[Dict[str, Any]] = None,
        generation_run_id: Optional[str] = None,
        status: MessageStatus = MessageStatus.COMPLETED,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AiMessage:
        with self._lock:
            conv = self.get_conversation(conversation_id, owner_user_id)
            if not conv:
                raise AiConversationNotFoundError(conversation_id)

            msg_id = f"msg_{uuid.uuid4().hex[:16]}"
            now = datetime.now(timezone.utc)
            token_count = len(content.split()) * 2

            message = AiMessage(
                message_id=msg_id,
                conversation_id=conversation_id,
                owner_user_id=owner_user_id,
                tenant_id=tenant_id,
                role=role,
                content=content,
                status=status,
                route_context=route_context,
                token_count=token_count,
                generation_run_id=generation_run_id,
                error_code=error_code,
                error_message=error_message,
                metadata=metadata or {},
                created_at=now,
                updated_at=now,
            )

            if conversation_id not in self._messages:
                self._messages[conversation_id] = []
            self._messages[conversation_id].append(message)
            self._message_lookup[msg_id] = message

            # Update conversation aggregates
            conv.message_count += 1
            conv.total_tokens += token_count
            conv.updated_at = now
            conv.last_message_at = now

            # If user message and title is default, auto-generate title from query
            if role == MessageRole.USER and conv.title in (
                "New Conversation",
                "Untitled Conversation",
            ):
                snippet = content.strip().replace("\n", " ")
                conv.title = (snippet[:40] + "...") if len(snippet) > 40 else snippet

            return message

    def get_message(self, message_id: str, owner_user_id: str) -> Optional[AiMessage]:
        with self._lock:
            msg = self._message_lookup.get(message_id)
            if not msg:
                return None
            if msg.owner_user_id != owner_user_id:
                raise AiAccessDeniedError("message", message_id)
            return msg

    def list_messages(
        self,
        conversation_id: str,
        owner_user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AiMessage]:
        with self._lock:
            conv = self.get_conversation(conversation_id, owner_user_id)
            if not conv:
                raise AiConversationNotFoundError(conversation_id)

            msgs = self._messages.get(conversation_id, [])
            return msgs[offset : offset + limit]

    def update_message(
        self,
        message_id: str,
        owner_user_id: str,
        content: Optional[str] = None,
        status: Optional[MessageStatus] = None,
        token_count: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> AiMessage:
        with self._lock:
            msg = self.get_message(message_id, owner_user_id)
            if not msg:
                raise AiMessageNotFoundError(message_id)

            now = datetime.now(timezone.utc)
            if content is not None:
                msg.content = content
            if status is not None:
                msg.status = status
            if token_count is not None:
                msg.token_count = token_count
            if error_code is not None:
                msg.error_code = error_code
            if error_message is not None:
                msg.error_message = error_message
            msg.updated_at = now
            return msg

    def delete_message(self, message_id: str, owner_user_id: str) -> bool:
        with self._lock:
            msg = self.get_message(message_id, owner_user_id)
            if not msg:
                raise AiMessageNotFoundError(message_id)

            conv_id = msg.conversation_id
            if conv_id in self._messages:
                self._messages[conv_id] = [
                    m for m in self._messages[conv_id] if m.message_id != message_id
                ]
            self._message_lookup.pop(message_id, None)

            conv = self._conversations.get(conv_id)
            if conv:
                conv.message_count = max(0, conv.message_count - 1)
                conv.total_tokens = max(0, conv.total_tokens - msg.token_count)
            return True

    # ---------------- Generation Runs & Cancellation ----------------

    def create_generation_run(
        self,
        conversation_id: str,
        user_message_id: str,
        owner_user_id: str,
        model_id: str,
        provider: str,
        tenant_id: Optional[str] = None,
    ) -> AiGenerationRun:
        with self._lock:
            gen_id = f"gen_{uuid.uuid4().hex[:16]}"
            run = AiGenerationRun(
                generation_id=gen_id,
                conversation_id=conversation_id,
                user_message_id=user_message_id,
                assistant_message_id=None,
                owner_user_id=owner_user_id,
                tenant_id=tenant_id,
                status=GenerationStatus.RUNNING,
                model_id=model_id,
                provider=provider,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                created_at=datetime.now(timezone.utc),
            )
            self._generation_runs[gen_id] = run
            return run

    def get_generation_run(
        self, generation_id: str, owner_user_id: str
    ) -> Optional[AiGenerationRun]:
        with self._lock:
            run = self._generation_runs.get(generation_id)
            if not run:
                return None
            if run.owner_user_id != owner_user_id:
                raise AiAccessDeniedError("generation", generation_id)
            return run

    def update_generation_run(
        self,
        generation_id: str,
        owner_user_id: str,
        status: Optional[GenerationStatus] = None,
        assistant_message_id: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        duration_ms: Optional[float] = None,
        source_manifest_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> AiGenerationRun:
        with self._lock:
            run = self.get_generation_run(generation_id, owner_user_id)
            if not run:
                raise AiGenerationRunNotFoundError(generation_id)

            if status is not None:
                run.status = status
                if status in (
                    GenerationStatus.COMPLETED,
                    GenerationStatus.FAILED,
                    GenerationStatus.CANCELLED,
                ):
                    run.finished_at = datetime.now(timezone.utc)
            if assistant_message_id is not None:
                run.assistant_message_id = assistant_message_id
            if prompt_tokens is not None:
                run.prompt_tokens = prompt_tokens
            if completion_tokens is not None:
                run.completion_tokens = completion_tokens
            if total_tokens is not None:
                run.total_tokens = total_tokens
            if duration_ms is not None:
                run.duration_ms = duration_ms
            if source_manifest_id is not None:
                run.source_manifest_id = source_manifest_id
            if error_code is not None:
                run.error_code = error_code
            if error_message is not None:
                run.error_message = error_message
            return run

    def register_cancellation_token(self, generation_id: str) -> None:
        with self._lock:
            self._cancelled_generations.discard(generation_id)

    def request_cancellation(self, generation_id: str) -> bool:
        with self._lock:
            self._cancelled_generations.add(generation_id)
            return True

    def is_cancelled(self, generation_id: str) -> bool:
        with self._lock:
            return generation_id in self._cancelled_generations

    # ---------------- User Preferences ----------------

    def get_user_preferences(
        self, owner_user_id: str, tenant_id: Optional[str] = None
    ) -> AiUserPreferences:
        with self._lock:
            if owner_user_id not in self._preferences:
                pref_id = f"pref_{uuid.uuid4().hex[:16]}"
                self._preferences[owner_user_id] = AiUserPreferences(
                    preference_id=pref_id,
                    owner_user_id=owner_user_id,
                    tenant_id=tenant_id,
                )
            return self._preferences[owner_user_id]

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
        with self._lock:
            prefs = self.get_user_preferences(owner_user_id)
            now = datetime.now(timezone.utc)
            if default_model_id is not None:
                prefs.default_model_id = default_model_id
            if temperature is not None:
                prefs.temperature = max(0.0, min(1.0, temperature))
            if send_on_enter is not None:
                prefs.send_on_enter = send_on_enter
            if sound_enabled is not None:
                prefs.sound_enabled = sound_enabled
            if overlay_dock_side is not None:
                prefs.overlay_dock_side = overlay_dock_side
            if overlay_width_px is not None:
                prefs.overlay_width_px = max(320, min(800, overlay_width_px))
            if metadata is not None:
                prefs.metadata.update(metadata)
            prefs.updated_at = now
            return prefs

    # ---------------- Audit ----------------

    def record_audit_event(
        self,
        owner_user_id: str,
        event_type: str,
        conversation_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            self._audit_events.append(
                {
                    "audit_id": f"audit_{uuid.uuid4().hex[:16]}",
                    "owner_user_id": owner_user_id,
                    "conversation_id": conversation_id,
                    "event_type": event_type,
                    "payload": payload or {},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
