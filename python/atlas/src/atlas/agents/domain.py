"""Typed domain contracts for the Stage 146 agent foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class AgentStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DISABLED = "DISABLED"


class AgentRunStatus(StrEnum):
    QUEUED = "QUEUED"
    CANCELLED = "CANCELLED"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class AgentVersion:
    version_id: str
    agent_id: str
    version: int
    model_id: str
    instructions: str
    tool_ids: tuple[str, ...]
    execution_limits: dict[str, int]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    agent_id: str
    tenant_id: str
    owner_id: str
    name: str
    description: str
    role: str
    status: AgentStatus
    versions: tuple[AgentVersion, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class AgentRunEvent:
    event_id: str
    run_id: str
    event_type: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentRun:
    run_id: str
    tenant_id: str
    owner_id: str
    agent_id: str
    version_id: str
    status: AgentRunStatus
    execution_enabled: bool
    input: dict[str, Any]
    created_at: datetime
    events: tuple[AgentRunEvent, ...] = field(default_factory=tuple)
