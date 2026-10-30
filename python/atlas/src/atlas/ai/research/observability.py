"""Observability and Audit Logging for Stage 127 AI Research (Part LXXIX)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger("atlas.ai.research")


@dataclass
class ResearchAuditEvent:
    """Audit log entry for research queries, retrieval, and citation inspection."""

    event_id: str
    event_type: str  # "SEARCH", "QUERY_RUN", "CITATION_RESOLVED", "COMPARISON"
    user_id: str
    tenant_id: str
    details: Dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResearchObservability:
    """Tracks performance metrics and security audit events."""

    _events: List[ResearchAuditEvent] = []

    @classmethod
    def record_event(
        cls,
        event_id: str,
        event_type: str,
        user_id: str,
        tenant_id: str,
        details: Optional[Dict[str, str]] = None,
    ) -> None:
        event = ResearchAuditEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            tenant_id=tenant_id,
            details=details or {},
        )
        cls._events.append(event)
        logger.info(
            "AI Research Audit: [%s] User=%s Tenant=%s Details=%s",
            event_type,
            user_id,
            tenant_id,
            details,
        )

    @classmethod
    def get_events(cls) -> List[ResearchAuditEvent]:
        return list(cls._events)
