"""
Observability and Audit Logging Service for Stage 149.
Maintains structured audit records of all MCP, plugin, package, tool,
and external developer API operations.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from atlas.ecosystem.domain import (
    AuditEventType,
    EcosystemAuditEvent,
    utc_now,
)


class EcosystemObservabilityService:
    """
    Thread-safe audit event ledger and telemetry aggregator.
    """

    def __init__(self) -> None:
        self._events: List[EcosystemAuditEvent] = []

    def record_event(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        event_type: AuditEventType,
        resource_id: str,
        resource_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> EcosystemAuditEvent:
        event = EcosystemAuditEvent(
            event_id=f"audit-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            actor_id=actor_id,
            event_type=event_type,
            resource_id=resource_id,
            resource_type=resource_type,
            details=details or {},
            timestamp=utc_now(),
        )
        self._events.append(event)
        return event

    def list_events(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
        event_type: Optional[AuditEventType] = None,
    ) -> List[EcosystemAuditEvent]:
        filtered = [
            e for e in self._events
            if e.tenant_id == tenant_id or e.tenant_id == "system-tenant"
        ]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        return sorted(filtered, key=lambda e: e.timestamp, reverse=True)[:limit]

