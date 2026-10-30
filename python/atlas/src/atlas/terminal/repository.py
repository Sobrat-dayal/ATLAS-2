"""Thread-safe repository for Stage 122 Terminal sessions and preferences."""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .enums import (
    ConnectionState,
    ExecutionCapability,
    SessionLifecycle,
    SessionStatus,
    TerminalCursorStyle,
    TerminalType,
)
from .errors import (
    TerminalDraftTooLargeError,
    TerminalSessionAccessDeniedError,
    TerminalSessionLimitExceededError,
    TerminalSessionNotFoundError,
    TerminalSessionVersionConflictError,
)
from .models import TerminalSession, TerminalUserPreferences


class TerminalRepository:
    """In-memory thread-safe repository for terminal sessions and preferences."""

    _instance = None
    _lock = threading.Lock()

    MAX_SESSIONS_PER_USER = 32
    MAX_DRAFT_BYTES = 65536  # 64 KB

    def __init__(self):
        self._sessions: Dict[str, TerminalSession] = {}
        self._preferences: Dict[str, TerminalUserPreferences] = {}
        self._audit_events: List[Dict[str, Any]] = []
        self._rlock = threading.RLock()

    @classmethod
    def get_instance(cls) -> "TerminalRepository":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _ensure_default_sessions(
        self, user_id: str, workspace_id: Optional[str] = None
    ) -> List[TerminalSession]:
        """Ensure initial default 4 institutional tabs exist for a new user."""
        existing = [
            s
            for s in self._sessions.values()
            if s.owner_user_id == user_id and s.lifecycle != SessionLifecycle.CLOSED
        ]
        if existing:
            return sorted(existing, key=lambda s: s.session_order)

        now = datetime.now(timezone.utc)
        defaults = [
            TerminalSession(
                session_id=f"term_cli_{uuid.uuid4().hex[:8]}",
                owner_user_id=user_id,
                terminal_type=TerminalType.ATLAS_CLI,
                display_name="ATLAS CLI",
                lifecycle=SessionLifecycle.ACTIVE,
                connection_state=ConnectionState.CONNECTED,
                execution_capability=ExecutionCapability.DISABLED,
                status=SessionStatus.READY,
                session_order=0,
                workspace_id=workspace_id,
                draft_content="",
                created_at=now,
                updated_at=now,
                last_active_at=now,
            ),
            TerminalSession(
                session_id=f"term_py_{uuid.uuid4().hex[:8]}",
                owner_user_id=user_id,
                terminal_type=TerminalType.PYTHON,
                display_name="Python",
                lifecycle=SessionLifecycle.ACTIVE,
                connection_state=ConnectionState.CONNECTED,
                execution_capability=ExecutionCapability.DISABLED,
                status=SessionStatus.INPUT_ONLY,
                session_order=1,
                workspace_id=workspace_id,
                draft_content="# Quantitative Scratchpad (Stage 122)\nimport math\n\ndef calculate_sharpe(returns, rf=0.04):\n    return (sum(returns)/len(returns) - rf)\n",
                created_at=now,
                updated_at=now,
                last_active_at=now,
            ),
            TerminalSession(
                session_id=f"term_sql_{uuid.uuid4().hex[:8]}",
                owner_user_id=user_id,
                terminal_type=TerminalType.SQL,
                display_name="SQL",
                lifecycle=SessionLifecycle.ACTIVE,
                connection_state=ConnectionState.CONNECTED,
                execution_capability=ExecutionCapability.DISABLED,
                status=SessionStatus.INPUT_ONLY,
                session_order=2,
                workspace_id=workspace_id,
                draft_content="-- Institutional Query Composition (Stage 122)\nSELECT instrument_id, symbol, name, exchange_mic\nFROM market_instruments\nWHERE is_active = true\nLIMIT 25;\n",
                created_at=now,
                updated_at=now,
                last_active_at=now,
            ),
            TerminalSession(
                session_id=f"term_logs_{uuid.uuid4().hex[:8]}",
                owner_user_id=user_id,
                terminal_type=TerminalType.LOGS,
                display_name="Logs",
                lifecycle=SessionLifecycle.ACTIVE,
                connection_state=ConnectionState.CONNECTED,
                execution_capability=ExecutionCapability.DISABLED,
                status=SessionStatus.READ_ONLY,
                session_order=3,
                workspace_id=workspace_id,
                draft_content="",
                created_at=now,
                updated_at=now,
                last_active_at=now,
            ),
        ]

        for s in defaults:
            self._sessions[s.session_id] = s
        return defaults

    def list_sessions(
        self, user_id: str, workspace_id: Optional[str] = None
    ) -> List[TerminalSession]:
        with self._rlock:
            active_sessions = [
                s
                for s in self._sessions.values()
                if s.owner_user_id == user_id and s.lifecycle != SessionLifecycle.CLOSED
            ]
            if not active_sessions:
                active_sessions = self._ensure_default_sessions(user_id, workspace_id)
            return sorted(active_sessions, key=lambda s: s.session_order)

    def get_session(self, session_id: str, user_id: str) -> TerminalSession:
        with self._rlock:
            session = self._sessions.get(session_id)
            if not session or session.lifecycle == SessionLifecycle.CLOSED:
                raise TerminalSessionNotFoundError(session_id)
            if session.owner_user_id != user_id:
                raise TerminalSessionAccessDeniedError(session_id, user_id)
            return session

    def create_session(
        self,
        user_id: str,
        terminal_type: TerminalType,
        display_name: Optional[str] = None,
        workspace_id: Optional[str] = None,
        initial_draft: str = "",
    ) -> TerminalSession:
        with self._rlock:
            # Check draft size limit
            draft_bytes = len(initial_draft.encode("utf-8"))
            if draft_bytes > self.MAX_DRAFT_BYTES:
                raise TerminalDraftTooLargeError(draft_bytes, self.MAX_DRAFT_BYTES)

            user_sessions = [
                s
                for s in self._sessions.values()
                if s.owner_user_id == user_id and s.lifecycle != SessionLifecycle.CLOSED
            ]
            if not user_sessions:
                user_sessions = self._ensure_default_sessions(user_id, workspace_id)

            if len(user_sessions) >= self.MAX_SESSIONS_PER_USER:
                raise TerminalSessionLimitExceededError(
                    len(user_sessions), self.MAX_SESSIONS_PER_USER
                )

            next_order = len(user_sessions)
            name = display_name or terminal_type.value.replace("_", " ").title()
            now = datetime.now(timezone.utc)
            session_id = f"term_{terminal_type.value.lower()[:3]}_{uuid.uuid4().hex[:8]}"

            # Determine appropriate status
            if terminal_type == TerminalType.ATLAS_CLI:
                status = SessionStatus.READY
            elif terminal_type in (TerminalType.PYTHON, TerminalType.SQL):
                status = SessionStatus.INPUT_ONLY
            else:
                status = SessionStatus.READ_ONLY

            new_session = TerminalSession(
                session_id=session_id,
                owner_user_id=user_id,
                terminal_type=terminal_type,
                display_name=name,
                lifecycle=SessionLifecycle.ACTIVE,
                connection_state=ConnectionState.CONNECTED,
                execution_capability=ExecutionCapability.DISABLED,
                status=status,
                session_order=next_order,
                workspace_id=workspace_id,
                draft_content=initial_draft,
                created_at=now,
                updated_at=now,
                last_active_at=now,
            )
            self._sessions[session_id] = new_session
            self.record_audit_event(
                user_id, session_id, "SESSION_CREATED", {"terminal_type": terminal_type.value}
            )
            return new_session

    def update_session(
        self,
        session_id: str,
        user_id: str,
        display_name: Optional[str] = None,
        draft_content: Optional[str] = None,
        scrollback_limit: Optional[int] = None,
        expected_version: Optional[int] = None,
    ) -> TerminalSession:
        with self._rlock:
            session = self.get_session(session_id, user_id)

            if expected_version is not None and session.version != expected_version:
                raise TerminalSessionVersionConflictError(
                    session_id, expected_version, session.version
                )

            if draft_content is not None:
                draft_bytes = len(draft_content.encode("utf-8"))
                if draft_bytes > self.MAX_DRAFT_BYTES:
                    raise TerminalDraftTooLargeError(draft_bytes, self.MAX_DRAFT_BYTES)
                session.draft_content = draft_content

            if display_name is not None and display_name.strip():
                session.display_name = display_name.strip()

            if scrollback_limit is not None and 100 <= scrollback_limit <= 10000:
                session.scrollback_limit = scrollback_limit

            session.version += 1
            session.updated_at = datetime.now(timezone.utc)
            session.last_active_at = datetime.now(timezone.utc)
            return session

    def close_session(self, session_id: str, user_id: str) -> bool:
        with self._rlock:
            session = self.get_session(session_id, user_id)
            session.lifecycle = SessionLifecycle.CLOSED
            session.closed_at = datetime.now(timezone.utc)
            session.updated_at = datetime.now(timezone.utc)

            # Re-normalize order
            remaining = [
                s
                for s in self._sessions.values()
                if s.owner_user_id == user_id and s.lifecycle != SessionLifecycle.CLOSED
            ]
            remaining.sort(key=lambda s: s.session_order)
            for idx, s in enumerate(remaining):
                s.session_order = idx

            self.record_audit_event(user_id, session_id, "SESSION_CLOSED", {})
            return True

    def reorder_sessions(self, user_id: str, session_ids: List[str]) -> List[TerminalSession]:
        with self._rlock:
            user_sessions = {
                s.session_id: s
                for s in self._sessions.values()
                if s.owner_user_id == user_id and s.lifecycle != SessionLifecycle.CLOSED
            }

            now = datetime.now(timezone.utc)
            for order, s_id in enumerate(session_ids):
                if s_id in user_sessions:
                    user_sessions[s_id].session_order = order
                    user_sessions[s_id].updated_at = now

            ordered = sorted(user_sessions.values(), key=lambda s: s.session_order)
            self.record_audit_event(user_id, None, "SESSIONS_REORDERED", {"order": session_ids})
            return ordered

    def get_preferences(self, user_id: str) -> TerminalUserPreferences:
        with self._rlock:
            if user_id not in self._preferences:
                self._preferences[user_id] = TerminalUserPreferences(user_id=user_id)
            return self._preferences[user_id]

    def update_preferences(
        self,
        user_id: str,
        font_size: Optional[int] = None,
        font_family: Optional[str] = None,
        line_height: Optional[float] = None,
        scrollback_limit: Optional[int] = None,
        cursor_style: Optional[TerminalCursorStyle] = None,
        word_wrap: Optional[bool] = None,
        terminal_height: Optional[int] = None,
        default_tab_type: Optional[TerminalType] = None,
        restore_previous_tabs: Optional[bool] = None,
        timestamp_display: Optional[bool] = None,
    ) -> TerminalUserPreferences:
        with self._rlock:
            pref = self.get_preferences(user_id)
            if font_size is not None and 8 <= font_size <= 32:
                pref.font_size = font_size
            if font_family is not None and font_family.strip():
                pref.font_family = font_family.strip()
            if line_height is not None and 1.0 <= line_height <= 2.5:
                pref.line_height = line_height
            if scrollback_limit is not None and 100 <= scrollback_limit <= 10000:
                pref.scrollback_limit = scrollback_limit
            if cursor_style is not None:
                pref.cursor_style = cursor_style
            if word_wrap is not None:
                pref.word_wrap = word_wrap
            if terminal_height is not None and 140 <= terminal_height <= 1200:
                pref.terminal_height = terminal_height
            if default_tab_type is not None:
                pref.default_tab_type = default_tab_type
            if restore_previous_tabs is not None:
                pref.restore_previous_tabs = restore_previous_tabs
            if timestamp_display is not None:
                pref.timestamp_display = timestamp_display

            pref.updated_at = datetime.now(timezone.utc)
            return pref

    def record_audit_event(
        self,
        user_id: str,
        session_id: Optional[str],
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        with self._rlock:
            self._audit_events.append(
                {
                    "event_id": f"evt_term_{uuid.uuid4().hex[:12]}",
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_type": event_type,
                    "payload": payload,
                    "created_at": datetime.now(timezone.utc),
                }
            )
