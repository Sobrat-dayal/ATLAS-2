"""In-Memory Thread-Safe Session Manager for ATLAS Historical Chart Replay V1 (Stage 75).

Provides:
- User-scoped session ownership enforcement
- Bounded session TTL with periodic expiration cleanup
- Internal session representation caching qualified series bars
- Conversion to public DTOs without leaking unrevealed bars
"""

import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID

from ..models import ChartBarDTO
from .models import (
    ReplaySessionDTO,
    ReplaySessionStatus,
    ReplaySourceSnapshot,
)

# Standard session lifetime is 60 minutes of inactivity
DEFAULT_SESSION_TTL_MINUTES = 60
MAX_SESSIONS_PER_USER = 5


class ReplaySessionInternal:
    """Internal server-side representation of an active historical replay session."""

    def __init__(
        self,
        session_id: UUID,
        owner_user_id: UUID,
        target_panel_id: str,
        instrument_entity_id: UUID,
        display_symbol: str,
        interval: str,
        source_snapshot: ReplaySourceSnapshot,
        bars: List[ChartBarDTO],
        start_index: int,
        cursor_index: int,
        history_window: int = 100,
        playback_speed: float = 1.0,
        ttl_minutes: int = DEFAULT_SESSION_TTL_MINUTES,
    ) -> None:
        self.session_id = session_id
        self.owner_user_id = owner_user_id
        self.target_panel_id = target_panel_id
        self.instrument_entity_id = instrument_entity_id
        self.display_symbol = display_symbol
        self.interval = interval
        self.source_snapshot = source_snapshot
        self.bars = bars  # Server-side authoritative chronological qualified bars
        self.start_index = max(0, min(start_index, len(bars) - 1)) if bars else 0
        self.cursor_index = max(0, min(cursor_index, len(bars) - 1)) if bars else 0
        self.history_window = history_window
        self.playback_speed = playback_speed
        self.status = (
            ReplaySessionStatus.END_OF_DATA
            if (bars and self.cursor_index >= len(bars) - 1)
            else ReplaySessionStatus.READY
        )
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.expires_at = now + timedelta(minutes=ttl_minutes)

    def touch(self, ttl_minutes: int = DEFAULT_SESSION_TTL_MINUTES) -> None:
        """Extends session expiration time upon activity."""
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)

    def is_expired(self) -> bool:
        """Checks if session has exceeded its inactivity TTL."""
        return datetime.now(timezone.utc) > self.expires_at

    def get_revealed_bars(self) -> List[ChartBarDTO]:
        """Returns all qualified bars from start window up to current cursor position.

        CRITICAL FUTURE ISOLATION:
        Bars after cursor_index are strictly excluded.
        """
        if not self.bars:
            return []
        # Return bars up to cursor (clamped by history window if desired, or all from 0 to cursor)
        return self.bars[: self.cursor_index + 1]

    def get_cursor_bar(self) -> Optional[ChartBarDTO]:
        """Returns the single finalized bar active at cursor position."""
        if 0 <= self.cursor_index < len(self.bars):
            return self.bars[self.cursor_index]
        return None

    def to_dto(self) -> ReplaySessionDTO:
        """Converts to public DTO."""
        return ReplaySessionDTO(
            session_id=self.session_id,
            owner_user_id=self.owner_user_id,
            target_panel_id=self.target_panel_id,
            instrument_entity_id=self.instrument_entity_id,
            display_symbol=self.display_symbol,
            interval=self.interval,
            status=self.status,
            cursor_index=self.cursor_index,
            start_index=self.start_index,
            cursor_bar=self.get_cursor_bar(),
            revealed_bars_count=self.cursor_index + 1 if self.bars else 0,
            total_bars=len(self.bars),
            playback_speed=self.playback_speed,
            source_snapshot=self.source_snapshot,
            created_at=self.created_at,
            expires_at=self.expires_at,
        )


class ReplaySessionManager:
    """Thread-safe in-memory session registry for historical replay sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[UUID, ReplaySessionInternal] = {}
        self._lock = threading.RLock()

    def get_active_count_for_user(self, user_id: UUID) -> int:
        """Returns the number of non-expired sessions owned by a user."""
        with self._lock:
            self.evict_expired()
            return sum(
                1
                for s in self._sessions.values()
                if s.owner_user_id == user_id and s.status != ReplaySessionStatus.CLOSED
            )

    def create_session(self, session: ReplaySessionInternal) -> ReplaySessionDTO:
        """Registers a newly initialized replay session with quota enforcement."""
        with self._lock:
            self.evict_expired()
            user_count = self.get_active_count_for_user(session.owner_user_id)
            if user_count >= MAX_SESSIONS_PER_USER:
                raise ValueError(
                    f"Active replay session quota exceeded: maximum allowed is "
                    f"{MAX_SESSIONS_PER_USER} concurrent sessions per user."
                )
            self._sessions[session.session_id] = session
            return session.to_dto()

    def get_session(
        self, session_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[ReplaySessionInternal]:
        """Retrieves an active session enforcing user ownership and TTL."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            if session.is_expired():
                del self._sessions[session_id]
                return None
            if user_id and session.owner_user_id != user_id:
                return None
            session.touch()
            return session

    def delete_session(self, session_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """Safely closes and removes a session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False
            if user_id and session.owner_user_id != user_id:
                return False
            session.status = ReplaySessionStatus.CLOSED
            del self._sessions[session_id]
            return True

    def evict_expired(self) -> int:
        """Evicts expired sessions from memory."""
        with self._lock:
            expired_ids = [
                sid for sid, session in self._sessions.items() if session.is_expired()
            ]
            for sid in expired_ids:
                del self._sessions[sid]
            return len(expired_ids)

    def clear(self) -> None:
        """Clears all sessions (primarily for unit test isolation)."""
        with self._lock:
            self._sessions.clear()


# Global singleton instance
default_replay_session_manager = ReplaySessionManager()
