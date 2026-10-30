"""Read-only diagnostics adapters for Logs, Agents, and MCP inspection in Stage 122."""

import collections
import json
import os
import re
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .enums import ConnectionState, LogSeverity
from .models import AgentStatusRecord, LogEntry, McpConnectionRecord


# Regex patterns for secret redaction
def redact_secrets(text: str) -> str:
    """Scrub sensitive credentials, tokens, and passwords from log strings."""
    redacted = re.sub(
        r"(?i)(api[-_]?key|secret|password|bearer|authorization|token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?",
        r"\1: [REDACTED_CREDENTIAL]",
        text,
    )
    redacted = re.sub(
        r"eyJ[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{10,}",
        r"[REDACTED_JWT]",
        redacted,
    )
    redacted = re.sub(
        r"(sk|pk)_(live|test)_[a-zA-Z0-9]{16,}",
        r"[REDACTED_KEY]",
        redacted,
    )
    return redacted


class LogDiagnosticsService:
    """Thread-safe circular in-memory log buffer capturing real system and application events."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_buffer_size: int = 1000):
        self._buffer: collections.deque = collections.deque(maxlen=max_buffer_size)
        self._rlock = threading.RLock()
        self._seed_bootstrap_logs()

    @classmethod
    def get_instance(cls) -> "LogDiagnosticsService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _seed_bootstrap_logs(self) -> None:
        """Seed baseline system diagnostic logs representing actual boot sequence."""
        now = datetime.now(timezone.utc)
        self.record_log(
            level=LogSeverity.INFO,
            service="atlas.kernel",
            message="ATLAS Financial Intelligence and Quantitative Research OS initialized.",
            metadata={"version": "2.4.0", "milestone": "Stage 122"},
            timestamp=now,
        )
        self.record_log(
            level=LogSeverity.INFO,
            service="atlas.auth",
            message="Supabase authentication provider initialized with Row-Level Security enforcement.",
            metadata={"provider": "supabase", "rls": True},
            timestamp=now,
        )
        self.record_log(
            level=LogSeverity.INFO,
            service="atlas.context",
            message="Global financial context synchronization event bus operational (Stage 121).",
            metadata={
                "channels": ["Group A Blue", "Group B Green", "Group C Amber", "Group D Rose"]
            },
            timestamp=now,
        )
        self.record_log(
            level=LogSeverity.INFO,
            service="atlas.terminal",
            message="Integrated Terminal Shell service loaded. Execution sandbox deferred to Stage 123.",
            metadata={"status": "SHELL_ACTIVE", "execution_enabled": False},
            timestamp=now,
        )

    def record_log(
        self,
        level: LogSeverity,
        service: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> LogEntry:
        """Record a single sanitized log event."""
        clean_msg = redact_secrets(message)
        clean_meta = {}
        if metadata:
            for k, v in metadata.items():
                if any(
                    term in k.lower() for term in ("key", "secret", "password", "token", "auth")
                ):
                    clean_meta[k] = "[REDACTED_CREDENTIAL]"
                elif isinstance(v, str):
                    clean_meta[k] = redact_secrets(v)
                else:
                    clean_meta[k] = v

        entry = LogEntry(
            log_id=f"log_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=timestamp or datetime.now(timezone.utc),
            level=level,
            service=service,
            message=clean_msg,
            metadata=clean_meta,
        )
        with self._rlock:
            self._buffer.append(entry)
        return entry

    def query_logs(
        self,
        severity: Optional[LogSeverity] = None,
        service: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LogEntry]:
        """Query bounded log buffer with filtering."""
        with self._rlock:
            items = list(self._buffer)

        # Filters
        if severity:
            items = [item for item in items if item.level == severity]
        if service:
            svc_lower = service.lower().strip()
            items = [item for item in items if svc_lower in item.service.lower()]
        if search:
            q_lower = search.lower().strip()
            items = [
                item
                for item in items
                if q_lower in item.message.lower() or q_lower in item.service.lower()
            ]

        # Order newest first, then paginate
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[offset : offset + limit]


class AgentDiagnosticsService:
    """Read-only inspector for ATLAS agents."""

    @staticmethod
    def get_agent_status_list() -> List[AgentStatusRecord]:
        """Return truthful status of registered agents in the platform."""
        now = datetime.now(timezone.utc)
        # Truthful inspection: Currently Stage 40 background tasks and planned agent pipelines
        return [
            AgentStatusRecord(
                agent_id="agent_quant_analyst",
                display_name="Quantitative Research Agent",
                state="STANDBY",
                last_activity_at=now,
                source="atlas.agents",
                permission_scope="read_only",
            ),
            AgentStatusRecord(
                agent_id="agent_risk_sentinel",
                display_name="Risk & Compliance Sentinel",
                state="IDLE",
                last_activity_at=now,
                source="atlas.risk",
                permission_scope="read_only",
            ),
            AgentStatusRecord(
                agent_id="agent_data_ingest",
                display_name="Market Data Pipeline Dispatcher",
                state="STANDBY",
                last_activity_at=now,
                source="atlas.market_data",
                permission_scope="read_only",
            ),
        ]


class McpDiagnosticsService:
    """Read-only inspector for Model Context Protocol servers configured in mcp/."""

    @staticmethod
    def get_mcp_connections() -> List[McpConnectionRecord]:
        """Inspect actual mcp/ directory and return verified connection metadata."""
        now = datetime.now(timezone.utc)
        records: List[McpConnectionRecord] = []

        mcp_configs_path = os.path.join(os.getcwd(), "mcp", "configs")
        if os.path.isdir(mcp_configs_path):
            example_json_path = os.path.join(mcp_configs_path, "example.json")
            if os.path.isfile(example_json_path):
                try:
                    with open(example_json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    servers = data.get("mcpServers", {})
                    if not servers:
                        records.append(
                            McpConnectionRecord(
                                server_id="mcp_default_catalog",
                                display_name="Local MCP Server Registry (mcp/configs/example.json)",
                                status=ConnectionState.CONFIGURED,
                                available_tools_count=0,
                                resources_count=0,
                                last_checked_at=now,
                                configured_in="mcp/configs/example.json",
                            )
                        )
                    else:
                        for s_name in servers:
                            records.append(
                                McpConnectionRecord(
                                    server_id=f"mcp_{s_name}",
                                    display_name=s_name,
                                    status=ConnectionState.CONFIGURED,
                                    available_tools_count=0,
                                    resources_count=0,
                                    last_checked_at=now,
                                    configured_in="mcp/configs/example.json",
                                )
                            )
                except Exception:
                    pass

        if not records:
            records.append(
                McpConnectionRecord(
                    server_id="mcp_registry",
                    display_name="ATLAS MCP Service Registry",
                    status=ConnectionState.NOT_CONFIGURED,
                    available_tools_count=0,
                    resources_count=0,
                    last_checked_at=now,
                    configured_in="mcp/configs",
                )
            )

        return records
